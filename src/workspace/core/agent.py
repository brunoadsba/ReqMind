"""Agent - Agente autonomo com tool calling e arquitetura de 3 camadas"""

import os
import json
import logging
import time
import asyncio
import requests
from groq import Groq
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .tools import ToolRegistry
from security.rate_limiter import message_limiter
from utils.retry import retry_with_backoff_sync

# Import run management
from workspace.runs import RunManager, RunMetrics

# Import memory management
from workspace.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class Agent:
    """Agente com arquitetura de memoria em 3 camadas"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # GLM removido - migrado para Groq Vision (mais rápido e confiável)
        self.tools = tool_registry
        self.model = "llama-3.3-70b-versatile"
        self.system_prompt = self._load_context_pack()
        self.run_manager = RunManager()
        self.memory_manager = MemoryManager()
    
    def _load_context_pack(self) -> str:
        """Carrega CONTEXT_PACK.md ou compila se necessario"""
        agent_dir = Path(__file__).parent.parent / "agent"
        context_path = agent_dir / "CONTEXT_PACK.md"
        
        if not context_path.exists():
            # Fallback: compilar automaticamente
            from workspace.agent.scripts.compiler import ContextCompiler
            compiler = ContextCompiler(agent_dir)
            content, _ = compiler.compile_and_save()
            return content
        
        return context_path.read_text(encoding='utf-8')

    def _has_image(self, message: str) -> bool:
        """Verifica se a mensagem contém referência a imagem"""
        return any(
            word in message.lower()
            for word in ["imagem", "foto", "figura", "screenshot", "print"]
        )

    @staticmethod
    @retry_with_backoff_sync(max_retries=3, exceptions=(ConnectionError, TimeoutError, OSError))
    def _groq_chat_sync(groq_client, model: str, messages: list, tools=None, tool_choice="auto", **kwargs):
        """Chamada Groq chat com retry (sync)."""
        if tools is not None:
            return groq_client.chat.completions.create(
                model=model, messages=messages, tools=tools, tool_choice=tool_choice,
                temperature=kwargs.get("temperature", 0.7), max_tokens=kwargs.get("max_tokens", 2048)
            )
        return groq_client.chat.completions.create(
            model=model, messages=messages,
            temperature=kwargs.get("temperature", 0.7), max_tokens=kwargs.get("max_tokens", 2048)
        )

    # Código GLM removido - migrado para Groq Vision
    # GLM-4.6V foi substituído por Groq Vision (llama-4-scout-17b-16e-instruct)
    # que é mais rápido, confiável e gratuito

    async def run(
        self,
        user_message: str,
        history: List[Dict] = None,
        image_url: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> str:
        # Inicializa metricas
        start_time = time.time()
        tools_used = 0
        run_dir = None
        status = "success"
        error_msg = None
        output_text = ""

        # Rate limiting check
        if user_id:
            if not message_limiter.is_allowed(user_id):
                remaining = message_limiter.get_remaining(user_id)
                return f"⏱️ Muitas requisições. Aguarde um momento. Requisições restantes: {remaining}"

        # Análise de imagem agora usa Groq Vision diretamente nos handlers
        # (handle_photo, handle_video) - código GLM removido

        if history is None:
            history = []

        # Cria run no inicio
        try:
            run_dir = self.run_manager.create_run(
                user_message=user_message,
                user_id=user_id,
                image_url=image_url
            )
            logger.info(f"Run criado: {run_dir.name}")
        except Exception as e:
            logger.error(f"Erro ao criar run: {e}")
            run_dir = None

        # Recupera memoria relevante
        memory_context = self.memory_manager.get_relevant_memory(user_message, max_facts=3)
        if memory_context:
            system_with_memory = self.system_prompt + "\n\n" + memory_context
        else:
            system_with_memory = self.system_prompt

        messages = (
            [{"role": "system", "content": system_with_memory}]
            + history
            + [{"role": "user", "content": user_message}]
        )

        max_iterations = 5

        for iteration in range(max_iterations):
            logger.info(f"Iteração {iteration + 1}/{max_iterations}")

            try:
                schemas = self.tools.get_schemas()
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._groq_chat_sync(
                        self.groq, self.model, messages,
                        tools=schemas, tool_choice="auto",
                    ),
                )
            except Exception as e:
                error_msg = str(e)
                if "tool_use_failed" in error_msg or "failed_generation" in error_msg:
                    logger.warning(
                        f"Tool calling falhou, tentando sem tools: {error_msg[:100]}"
                    )
                    # Retry sem tool calling
                    try:
                        response = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self._groq_chat_sync(self.groq, self.model, messages),
                        )
                        return response.choices[0].message.content
                    except Exception as fallback_e:
                        logger.warning(f"Fallback sem tools falhou: {fallback_e}")
                        return "Desculpe, tive um problema ao processar sua solicitação. Tente novamente."
                else:
                    raise

        message = response.choices[0].message

        if not message.tool_calls:
            logger.info("Resposta final gerada")
            output_text = message.content or ""
            status = "success"
            self._finalize_run(run_dir, output_text, user_message, start_time, tools_used, status, messages)
            return output_text

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args_str = tool_call.function.arguments.strip()
                args_str = args_str.replace("{ ", "{").replace(" }", "}")
                try:
                    tool_args = json.loads(args_str)
                except Exception as parse_e:
                    logger.error(
                        f"Erro ao parsear argumentos: {tool_call.function.arguments}: {parse_e}"
                    )
                    tool_args = {}

            logger.info(f"Executando: {tool_name}({tool_args})")
            tools_used += 1

            result = await self.tools.execute(tool_name, tool_args)

            if run_dir:
                try:
                    self.run_manager.log_action(
                        run_dir=run_dir,
                        tool_name=tool_name,
                        tool_args=tool_args,
                        result=result,
                        iteration=tools_used
                    )
                except Exception as e:
                    logger.error(f"Erro ao logar acao: {e}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        # Max iteracoes atingido
        status = "partial"
        output_text = "Desculpe, não consegui completar a tarefa no tempo esperado."
        self._finalize_run(run_dir, output_text, user_message, start_time, tools_used, status, messages)
        return output_text

    def _finalize_run(self, run_dir, output_text, user_message, start_time, tools_used, status, messages):
        """Salva output e metrics no final do run"""
        if not run_dir:
            return

        try:
            duration = (time.time() - start_time) * 1000  # ms

            # Estimar tokens
            tokens_input = sum(len(m.get('content', '')) for m in messages if m.get('role') in ['system', 'user']) // 4
            tokens_output = sum(len(m.get('content', '')) for m in messages if m.get('role') == 'assistant') // 4

            # Salvar output
            self.run_manager.save_output(run_dir, output_text)

            # Salvar metrics
            metrics = RunMetrics(
                timestamp=datetime.utcnow().isoformat() + "Z",
                duration_ms=duration,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                iterations=len([m for m in messages if m.get('role') == 'assistant']),
                tools_used=tools_used,
                status=status
            )
            self.run_manager.save_metrics(run_dir, metrics)
        except Exception as e:
            logger.error(f"Erro ao salvar run/metrics: {e}")

        logger.info(f"Run finalizado: {run_dir.name} ({status}, {tools_used} tools)")

        try:
            self.memory_manager.remember_interaction(user_message, output_text)
            logger.debug("Interação memorizada")
        except Exception as mem_e:
            logger.error(f"Erro ao memorizar interação: {mem_e}")
