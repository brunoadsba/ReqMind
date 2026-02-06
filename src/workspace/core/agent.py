"""Agent - Agente autonomo com tool calling e arquitetura de 3 camadas"""

import os
import re
import json
import logging
import time
import asyncio
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config.settings import config
from security.rate_limiter import message_limiter
from workspace.core.llm_router import LlmRouter
from .tools import ToolRegistry

# Import run management
from workspace.runs import RunManager, RunMetrics

# Import memory management
from workspace.memory.memory_manager import MemoryManager
from workspace.core.nvidia_kimi import chat_completion_sync as nvidia_kimi_chat

logger = logging.getLogger(__name__)


class Agent:
    """Agente com arquitetura de memoria em 3 camadas"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tools = tool_registry
        # LlmRouter encapsula chamadas ao Groq (e futuros provedores)
        self.llm_router = LlmRouter.from_env()
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
    def _format_rate_limit_message(error_msg: str) -> str:
        """Extrai tempo de espera do erro 429 da Groq e formata mensagem em pt-BR."""
        base = "Limite de uso da API atingido no momento."
        # Ex.: "Please try again in 6m43.488s" ou "in 0m30.123s"
        m = re.search(r"try again in (\d+)m(\d+(?:\.\d+)?)s", error_msg, re.IGNORECASE)
        if m:
            mins, secs = int(m.group(1)), float(m.group(2))
            total_secs = mins * 60 + secs
            if total_secs >= 60:
                min_str = "1 minuto" if mins == 1 else f"{mins} minutos"
                return f"{base} Tente novamente em cerca de {min_str}."
            seg = int(total_secs)
            seg_str = "1 segundo" if seg == 1 else f"{seg} segundos"
            return f"{base} Tente novamente em cerca de {seg_str}."
        return f"{base} Tente novamente em alguns minutos."

    def _sanitize_embedded_tool_calls(self, content: str) -> tuple[str, Optional[tuple[str, dict]]]:
        """
        Remove do texto blocos de tool call em formato literal (ex.: <|tool_calls_section_begin|>...).
        Se encontrar save_memory, extrai nome e argumentos para execução posterior.
        Retorna (texto_limpo, (tool_name, tool_args) ou None).
        """
        if not content or not isinstance(content, str):
            return (content or "", None)
        text = content
        parsed_tool = None
        # Bloco completo: <|tool_calls_section_begin|> ... <|tool_calls_section_end|>
        section_re = re.compile(
            r"<\|tool_calls_section_begin\|>\s*.*?<\|tool_calls_section_end\|>",
            re.DOTALL,
        )
        match = section_re.search(text)
        if match:
            block = match.group(0)
            text = text.replace(block, "").strip()
            # Dentro do bloco: functions.save_memory:0 <|tool_call_argument_begin|> {...}
            save_re = re.compile(
                r"<\|tool_call_begin\|>\s*functions\.save_memory:\d+\s*"
                r"<\|tool_call_argument_begin\|>\s*(\{.*?\})\s*<\|tool_call_end\|>",
                re.DOTALL,
            )
            save_match = save_re.search(block)
            if save_match:
                try:
                    args = json.loads(save_match.group(1))
                    # API do modelo pode enviar key/value; nosso schema usa content/category
                    content_val = args.get("content") or args.get("value") or ""
                    category_val = args.get("category", "general")
                    if content_val:
                        parsed_tool = ("save_memory", {"content": content_val, "category": category_val})
                except (json.JSONDecodeError, TypeError):
                    pass
        # Remove também fragmentos soltos do mesmo padrão
        text = re.sub(r"<\|tool_calls?_section?_?\w*\|>\s*", "", text)
        text = re.sub(r"<\|tool_call_\w+\|>\s*", "", text)
        return (text.strip(), parsed_tool)

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
                image_url=image_url,
            )
            logger.info(
                "run_criado id=%s user_id=%s len=%d",
                run_dir.name,
                user_id,
                len(user_message or ""),
            )
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

        safety_cap = config.MAX_ITERATIONS  # só para evitar loop infinito em caso de bug

        while True:
            iteration = tools_used + 1
            if iteration > safety_cap:
                logger.warning(
                    "agent_safety_cap atingido safety_cap=%d user_id=%s", safety_cap, user_id
                )
                status = "partial"
                output_text = "Resposta interrompida por segurança. Tente uma pergunta mais direta."
                self._finalize_run(run_dir, output_text, user_message, start_time, tools_used, status, messages)
                return output_text

            logger.info(
                "agent_iteracao run=%s iter=%d/%d tools_usados=%d",
                run_dir.name if run_dir else None,
                iteration,
                safety_cap,
                tools_used,
            )

            try:
                schemas = self.tools.get_schemas()
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.llm_router.chat(
                        messages,
                        tools=schemas,
                        tool_choice="auto",
                        user_id=user_id,
                    ),
                )
            except Exception as e:
                error_msg = str(e)
                # Limite diário configurado para o Groq
                if "LLM_GROQ_DAILY_LIMIT_REACHED" in error_msg:
                    daily_limit = config.LLM_GROQ_DAILY_LIMIT_TOKENS
                    limit_msg = (
                        "Limite diário de uso do modelo Groq atingido. "
                        "Tente novamente amanhã ou faça uma pergunta coberta pelas memórias salvas."
                    )
                    self._finalize_run(
                        run_dir,
                        limit_msg,
                        user_message,
                        start_time,
                        tools_used,
                        "daily_limit_groq",
                        messages,
                    )
                    return limit_msg

                if "429" in error_msg or "rate_limit" in error_msg.lower() or "Rate limit" in error_msg:
                    logger.warning(
                        "llm_rate_limit provider=groq user_id=%s msg=\"%s\"",
                        user_id,
                        error_msg[:120],
                    )
                    nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
                    if nvidia_key:
                        # Limite diário opcional para NVIDIA/Kimi
                        from workspace.storage.llm_usage import has_reached_daily_limit

                        if has_reached_daily_limit("nvidia", config.LLM_NVIDIA_DAILY_LIMIT_TOKENS):
                            logger.warning(
                                "llm_daily_limit provider=nvidia user_id=%s pulando_fallback_kimi",
                                user_id,
                            )
                        else:
                            try:
                                kimi_content = await asyncio.get_event_loop().run_in_executor(
                                    None,
                                    lambda: nvidia_kimi_chat(
                                        nvidia_key,
                                        messages,
                                        max_tokens=4096,
                                        temperature=0.7,
                                        timeout=20,
                                    ),
                                )
                                if kimi_content:
                                    logger.info(
                                        "llm_resposta_fallback provider=nvidia kind=kimi_k2_5 user_id=%s",
                                        user_id,
                                    )
                                    self._finalize_run(
                                        run_dir,
                                        kimi_content,
                                        user_message,
                                        start_time,
                                        tools_used,
                                        "fallback_kimi",
                                        messages,
                                    )
                                    return kimi_content
                            except Exception as kimi_e:
                                logger.warning("Fallback Kimi K2.5 falhou: %s", kimi_e)
                    rate_msg = self._format_rate_limit_message(error_msg)
                    # Fallback RAG: responder da memória (ex.: NR-29) quando API indisponível
                    try:
                        from workspace.tools.impl.rag_memory import search_memory as rag_search_memory
                        q = (user_message or "").strip().lower()
                        if q and len(q) >= 2:
                            search_query = user_message
                            if "nr" in q and "29" in q:
                                search_query = "NR-29"
                            elif "nr" in q or "norma" in q:
                                search_query = "NR"
                            out = rag_search_memory(search_query)
                            if out.get("success") and out.get("results"):
                                texts = [r.get("text", "") for r in out["results"][:2] if r.get("text")]
                                if texts:
                                    raw = texts[0]
                                    max_len = 1200
                                    if len(raw) > max_len:
                                        chunk = raw[: max_len + 1]
                                        for sep in (". ", ".\n", "? ", "! ", "\n"):
                                            idx = chunk.rfind(sep)
                                            if idx != -1:
                                                raw = raw[: idx + len(sep)].rstrip()
                                                break
                                        else:
                                            raw = chunk.rsplit(" ", 1)[0] if " " in chunk else chunk
                                        raw += "\n\n(Resumo truncado.)"
                                    note = "Resposta com base na memória (API temporariamente indisponível).\n\n"
                                    self._finalize_run(
                                        run_dir, note + raw, user_message, start_time,
                                        tools_used, "rate_limit_rag_fallback", messages,
                                    )
                                    return note + raw
                    except Exception as rag_e:
                        logger.debug("fallback_rag_ignorado error=%s", rag_e)
                    self._finalize_run(
                        run_dir, rate_msg, user_message, start_time,
                        tools_used, "rate_limit", messages,
                    )
                    return rate_msg
                is_tool_error = (
                    "tool_use_failed" in error_msg
                    or "failed_generation" in error_msg
                    or "Failed to call a function" in error_msg
                    or "Error code: 400" in error_msg
                )
                if is_tool_error:
                    logger.debug("tool_calling_erro detalhe=%s", error_msg)
                    logger.warning(
                        "tool_calling_falhou provider=groq action=fallback_sem_tools user_id=%s",
                        user_id,
                    )
                    try:
                        response = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.llm_router.chat(messages, user_id=user_id),
                        )
                        output_text = (response.choices[0].message.content or "").strip()
                        if not output_text:
                            output_text = "Não consegui processar com ferramentas; tente reformular a pergunta."
                        self._finalize_run(
                            run_dir,
                            output_text,
                            user_message,
                            start_time,
                            tools_used,
                            "fallback_no_tools",
                            messages,
                        )
                        return output_text
                    except Exception as fallback_e:
                        logger.warning("fallback_sem_tools_falhou error=%s", fallback_e)
                        fallback_text = "Desculpe, tive um problema ao processar sua solicitação. Tente novamente."
                        self._finalize_run(
                            run_dir, fallback_text, user_message, start_time,
                            tools_used, "error", messages,
                        )
                        return fallback_text
                else:
                    raise

            message = response.choices[0].message

            if not message.tool_calls:
                logger.info("Resposta final gerada")
                raw_content = message.content or ""
                output_text, embedded_tool = self._sanitize_embedded_tool_calls(raw_content)
                if embedded_tool:
                    tool_name, tool_args = embedded_tool
                    try:
                        result = await self.tools.execute(tool_name, tool_args)
                        tools_used += 1
                        if run_dir:
                            try:
                                self.run_manager.log_action(run_dir, tool_name, tool_args, result, tools_used)
                            except Exception as e:
                                logger.error("Erro ao logar acao: %s", e)
                        if not output_text.strip():
                            output_text = "Informação salva na memória."
                        elif "salvar" in output_text.lower() or "memória" in output_text.lower():
                            output_text = output_text.rstrip(". ")
                            if not output_text.endswith("."):
                                output_text += "."
                            output_text += " Feito."
                    except Exception as e:
                        logger.warning("Execução de tool embutida falhou: %s", e)
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

    def _finalize_run(self, run_dir, output_text, user_message, start_time, tools_used, status, messages):
        """Salva output e metrics no final do run"""
        if not run_dir:
            return

        try:
            duration = (time.time() - start_time) * 1000  # ms

            # Estimar tokens (aprox. 4 chars por token)
            tokens_input = (
                sum(len(m.get("content", "")) for m in messages if m.get("role") in ["system", "user"])
                // 4
            )
            tokens_output = (
                sum(len(m.get("content", "")) for m in messages if m.get("role") == "assistant")
                // 4
            )

            # Salvar output
            self.run_manager.save_output(run_dir, output_text)

            # Salvar metrics
            metrics = RunMetrics(
                timestamp=datetime.utcnow().isoformat() + "Z",
                duration_ms=duration,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                iterations=len([m for m in messages if m.get("role") == "assistant"]),
                tools_used=tools_used,
                status=status,
            )
            self.run_manager.save_metrics(run_dir, metrics)

            # Atualizar uso diário por provedor (aproximação suficiente para uso pessoal)
            from workspace.storage import llm_usage

            provider: Optional[str] = None
            if status in ("success", "fallback_no_tools", "rate_limit", "rate_limit_rag_fallback", "daily_limit_groq"):
                provider = "groq"
            elif status == "fallback_kimi":
                provider = "nvidia"

            if provider:
                try:
                    llm_usage.add_usage(provider, tokens_input, tokens_output)
                except Exception as usage_err:
                    logger.error("Erro ao registrar uso de tokens (%s): %s", provider, usage_err)

        except Exception as e:
            logger.error(f"Erro ao salvar run/metrics ou uso de tokens: {e}")

        logger.info(f"Run finalizado: {run_dir.name} ({status}, {tools_used} tools)")

        try:
            self.memory_manager.remember_interaction(user_message, output_text)
            logger.debug("Interação memorizada")
        except Exception as mem_e:
            logger.error(f"Erro ao memorizar interação: {mem_e}")
