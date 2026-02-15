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
from .cache import response_cache, memory_cache, should_cache_query

# Import run management
from workspace.runs import RunManager, RunMetrics

# Import memory management
from workspace.memory.memory_manager import MemoryManager
from workspace.core.nvidia_kimi import chat_completion_sync as nvidia_kimi_chat
from workspace.core.glm_client import chat_completion_sync as glm_chat

logger = logging.getLogger(__name__)

# Circuit breaker: após 429 da Groq, usar Kimi por este tempo (segundos) antes de tentar Groq de novo
GROQ_COOLDOWN_SECONDS = 35 * 60  # 35 minutos
_groq_cooldown_until: float = 0.0  # unix timestamp; 0 = não em cooldown


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

        return context_path.read_text(encoding="utf-8")

    def _has_image(self, message: str) -> bool:
        """Verifica se a mensagem contém referência a imagem"""
        return any(
            word in message.lower() for word in ["imagem", "foto", "figura", "screenshot", "print"]
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
                msg = f"{base} Tente novamente em cerca de {min_str}."
            else:
                seg = int(total_secs)
                seg_str = "1 segundo" if seg == 1 else f"{seg} segundos"
                msg = f"{base} Tente novamente em cerca de {seg_str}."
        else:
            msg = f"{base} Tente novamente em alguns minutos."
        return (
            msg
            + " Quando retomar, tente: «O que você sabe sobre mim?» ou «Quais minhas preferências?»."
        )

    @staticmethod
    def _is_rate_limit_error(msg: str) -> bool:
        """True se a mensagem de erro indica rate limit (429, TPD, etc.)."""
        if not msg:
            return False
        m = msg.lower()
        return (
            "429" in msg
            or "rate_limit" in m
            or "rate limit" in m
            or "rate_limit_exceeded" in m
            or "tokens per day" in m
            or "tpd" in m
        )

    @staticmethod
    def _user_asked_to_read_file(msg: str) -> bool:
        """True se a mensagem pede explicitamente ler/resumir/analisar um arquivo específico."""
        if not (msg or msg.strip()):
            return False
        lower = msg.strip().lower()
        triggers = (
            "leia o arquivo",
            "leia o conteúdo do arquivo",
            "conteúdo do arquivo",
            "conteudo do arquivo",
            "resuma o arquivo",
            "resuma o conteúdo",
            "read file",
            "read the file",
            ".md",
            ".txt",
            ".json",
        )
        return any(t in lower for t in triggers)

    @staticmethod
    def _extract_file_path(message: str) -> Optional[str]:
        """Extrai caminho de arquivo de mensagens como 'leia MEMORY.md' ou 'arquivo docs/notes.md'. Seguro: sem '..' e sem path absoluto."""
        if not (message or message.strip()):
            return None
        patterns = [
            r"[\s\"'`]([a-zA-Z0-9_\-/]+\.md)[\s\"'`]",
            r"[\s\"'`]([a-zA-Z0-9_\-/]+\.txt)[\s\"'`]",
            r"[\s\"'`]([a-zA-Z0-9_\-/]+\.json)[\s\"'`]",
            r"arquivo\s+([a-zA-Z0-9_\-/.]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                if ".." not in path and not path.startswith("/"):
                    return path
        return None

    @staticmethod
    def _truncate(text: str, max_chars: int = 4000) -> str:
        """Trunca texto para limite do Telegram, evitando estouro de mensagem."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n\n[...]"

    @staticmethod
    def _extract_markdown_headings(text: str, max_entries: int = 50) -> str:
        """Extrai linhas com ## ou ### do markdown para ancorar resumos no conteúdo real."""
        lines = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("## ") or s.startswith("### "):
                lines.append(s)
                if len(lines) >= max_entries:
                    break
        return "\n".join(lines) if lines else ""

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
                        parsed_tool = (
                            "save_memory",
                            {"content": content_val, "category": category_val},
                        )
                except (json.JSONDecodeError, TypeError):
                    pass
        # Remove também fragmentos soltos do mesmo padrão
        text = re.sub(r"<\|tool_calls?_section?_?\w*\|>\s*", "", text)
        text = re.sub(r"<\|tool_call_\w+\|>\s*", "", text)
        return (text.strip(), parsed_tool)

    async def run(
        self,
        user_message: str,
        history: List[Dict] = None,
        image_url: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> str:
        global _groq_cooldown_until
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
                return (
                    f"⏱️ Muitas requisições. Aguarde um momento. Requisições restantes: {remaining}"
                )

        if len(history) <= 2 and should_cache_query(user_message):
            cached_response = response_cache.get(user_message)
            if cached_response:
                logger.info("cache_hit user_id=%s query=%s", user_id, user_message[:50])
                return cached_response

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
            memory_instruction = (
                "\n\n[INSTRUÇÃO DE MEMÓRIA]\n"
                "Você tem acesso a fatos sobre o usuário na seção 'Fatos relevantes' abaixo. "
                "Use essas informações para personalizar suas respostas. "
                "Se o usuário perguntar 'o que você sabe sobre mim' ou 'quais minhas preferências', "
                "cite especificamente esses fatos de forma natural e personalizada."
            )
            system_with_memory = self.system_prompt + memory_instruction + "\n\n" + memory_context
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
                self._finalize_run(
                    run_dir, output_text, user_message, start_time, tools_used, status, messages
                )
                return output_text

            logger.info(
                "agent_iteracao run=%s iter=%d/%d tools_usados=%d",
                run_dir.name if run_dir else None,
                iteration,
                safety_cap,
                tools_used,
            )

            try:
                # Circuit breaker: após 429, usar Kimi por GROQ_COOLDOWN_SECONDS antes de tentar Groq de novo
                nvidia_key_cb = os.getenv("NVIDIA_API_KEY", "").strip()
                if nvidia_key_cb and time.time() < _groq_cooldown_until:
                    try:
                        kimi_content = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: nvidia_kimi_chat(
                                nvidia_key_cb,
                                messages,
                                max_tokens=4096,
                                temperature=0.7,
                                timeout=20,
                            ),
                        )
                        if kimi_content:
                            logger.info(
                                "llm_circuit_breaker provider=nvidia user_id=%s",
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
                        logger.warning("Circuit breaker Kimi falhou: %s", kimi_e)
                if time.time() < _groq_cooldown_until:
                    glm_key_cb = os.getenv("GLM_API_KEY", "").strip()
                    if glm_key_cb:
                        try:
                            glm_content = await asyncio.get_event_loop().run_in_executor(
                                None,
                                lambda: glm_chat(
                                    glm_key_cb,
                                    messages,
                                    max_tokens=4096,
                                    temperature=0.7,
                                    timeout=25,
                                ),
                            )
                            if glm_content:
                                logger.info(
                                    "llm_circuit_breaker provider=glm user_id=%s",
                                    user_id,
                                )
                                self._finalize_run(
                                    run_dir,
                                    glm_content,
                                    user_message,
                                    start_time,
                                    tools_used,
                                    "fallback_glm",
                                    messages,
                                )
                                return glm_content
                        except Exception as glm_e:
                            logger.warning("Circuit breaker GLM falhou: %s", glm_e)

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

                if self._is_rate_limit_error(error_msg):
                    logger.warning(
                        'llm_rate_limit provider=groq user_id=%s msg="%s"',
                        user_id,
                        error_msg[:120],
                    )
                    _groq_cooldown_until = time.time() + GROQ_COOLDOWN_SECONDS
                    nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
                    logger.info(
                        "fallback_429 nvidia_key_presente=%s glm_key_presente=%s",
                        bool(nvidia_key),
                        bool(os.getenv("GLM_API_KEY", "").strip()),
                    )
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
                    else:
                        logger.info("fallback_kimi_pulado sem_nvidia_key")
                    glm_key = os.getenv("GLM_API_KEY", "").strip()
                    if glm_key:
                        try:
                            logger.info("tentando_fallback_glm user_id=%s", user_id)
                            glm_content = await asyncio.get_event_loop().run_in_executor(
                                None,
                                lambda: glm_chat(
                                    glm_key,
                                    messages,
                                    max_tokens=4096,
                                    temperature=0.7,
                                    timeout=25,
                                ),
                            )
                            if glm_content:
                                logger.info(
                                    "llm_resposta_fallback provider=glm user_id=%s",
                                    user_id,
                                )
                                self._finalize_run(
                                    run_dir,
                                    glm_content,
                                    user_message,
                                    start_time,
                                    tools_used,
                                    "fallback_glm",
                                    messages,
                                )
                                return glm_content
                        except Exception as glm_e:
                            logger.warning("Fallback GLM falhou: %s", glm_e)
                    else:
                        logger.info("fallback_glm_pulado sem_glm_key")
                    rate_msg = self._format_rate_limit_message(error_msg)

                    # NOVA ORDEM DE FALLBACKS (prioridade a web_search para perguntas gerais):

                    # NRs que estão na memória (sistema híbrido NRs)
                    NR_MEMORY = [
                        "nr-29",
                        "nr1",
                        "nr-1",
                        "nr5",
                        "nr-5",
                        "nr6",
                        "nr-6",
                        "nr10",
                        "nr-10",
                        "nr33",
                        "nr-33",
                        "nr35",
                        "nr-35",
                    ]

                    # Fallback 1: RAG de documentos (apenas para perguntas sobre NRs em memória)
                    q = (user_message or "").strip().lower()
                    # Extrai número da NR da pergunta (ex: "NR-35", "NR 35", "nr35")
                    nr_match = re.search(r"nr[s]?\s*[-\s]*(\d+)", q)
                    nr_number = nr_match.group(1) if nr_match else None
                    is_nr_question = bool(nr_number) or (
                        "nr" in q and ("norma" in q or "regulamentadora" in q)
                    )

                    # Verifica se a NR mencionada está na memória
                    nr_in_memory = False
                    if nr_number:
                        nr_key = f"nr{nr_number}".lower()
                        # Remove zeros à esquerda
                        nr_key = re.sub(r"^nr0+", "nr-", nr_key)
                        nr_in_memory = nr_key in [n.replace("-", "").lower() for n in NR_MEMORY]

                    if is_nr_question and nr_in_memory:
                        try:
                            from workspace.tools.impl.rag_memory import (
                                search_memory as rag_search_memory,
                            )

                            # Se temos o número, busca a NR específica; caso contrário, busca geral
                            search_query = f"NR-{nr_number}" if nr_number else "NR"
                            out = rag_search_memory(search_query)
                            if out.get("success") and out.get("results"):
                                texts = [
                                    r.get("text", "") for r in out["results"][:2] if r.get("text")
                                ]
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

                                    # Verifica se NR está na memória ou foi buscada na web
                                    if nr_in_memory:
                                        note = "Resposta com base na memória local.\n\n"
                                    else:
                                        note = "⚠️ APIs de IA temporariamente indisponíveis. Encontrei informação relevante.\n\n"

                                    self._finalize_run(
                                        run_dir,
                                        note + raw,
                                        user_message,
                                        start_time,
                                        tools_used,
                                        "nr_rag_fallback",
                                        messages,
                                    )
                                    return note + raw
                        except Exception as rag_e:
                            logger.debug("fallback_rag_nr_ignorado error=%s", rag_e)

                    # Fallback 2: web_search para perguntas sobre NRs NÃO na memória (busca automática)
                    # Se é pergunta sobre NR mas NR não está na memória, faz web search
                    elif is_nr_question and nr_number:
                        try:
                            from workspace.tools.web_search import web_search

                            logger.info(
                                "nr_web_search_fallback user_id=%s nr=%s query=%s",
                                user_id,
                                nr_number,
                                user_message[:50],
                            )
                            # Constrói query específica para NR
                            web_query = (
                                f"NR-{nr_number} Ministério do Trabalho Norma Regulamentadora"
                            )
                            search_result = await web_search(web_query)
                            if search_result.get("success") and search_result.get("results"):
                                results = search_result["results"][:3]
                                response_lines = [
                                    f"📋 Encontrei informações sobre NR-{nr_number}:\n"
                                ]
                                for i, r in enumerate(results, 1):
                                    title = r.get("title", "Sem título")
                                    snippet = r.get("body", r.get("snippet", "Sem descrição"))
                                    href = r.get("href", r.get("url", ""))
                                    response_lines.append(f"\n**{title}**")
                                    response_lines.append(f"{snippet[:200]}...")
                                    if href:
                                        response_lines.append(f"🔗 {href}")

                                web_response = "\n".join(response_lines)
                                logger.info(
                                    "nr_web_search_success user_id=%s nr=%s resultados=%s",
                                    user_id,
                                    nr_number,
                                    len(results),
                                )
                                self._finalize_run(
                                    run_dir,
                                    web_response,
                                    user_message,
                                    start_time,
                                    tools_used,
                                    "nr_web_search",
                                    messages,
                                )
                                return web_response
                        except Exception as web_e:
                            logger.debug("nr_web_search_fallback error=%s", web_e)

                    # Fallback 3: web_search para perguntas de conhecimento geral (NÃO sobre arquivos e NÃO sobre NRs)
                    # Isso DEVE vir antes do FactStore para evitar respostas irrelevantes sobre o usuário
                    web_search_attempted = False
                    if not self._user_asked_to_read_file(user_message) and not is_nr_question:
                        try:
                            from workspace.tools.web_search import web_search

                            logger.info(
                                "fallback_429_web_search user_id=%s query=%s",
                                user_id,
                                user_message[:50],
                            )
                            web_search_attempted = True
                            search_result = await web_search(user_message)
                            if search_result.get("success") and search_result.get("results"):
                                results = search_result["results"][:3]
                                response_lines = [
                                    "⚠️ APIs de IA temporariamente indisponíveis. Busquei na web para você:\n"
                                ]
                                for i, r in enumerate(results, 1):
                                    title = r.get("title", "Sem título")
                                    snippet = r.get("body", r.get("snippet", "Sem descrição"))
                                    href = r.get("href", r.get("url", ""))
                                    response_lines.append(f"\n{i}. **{title}**")
                                    response_lines.append(f"   {snippet[:150]}...")
                                    if href:
                                        response_lines.append(f"   🔗 {href}")

                                web_response = "\n".join(response_lines)
                                logger.info(
                                    "web_search_fallback_sucesso user_id=%s resultados=%s",
                                    user_id,
                                    len(results),
                                )
                                self._finalize_run(
                                    run_dir,
                                    web_response,
                                    user_message,
                                    start_time,
                                    tools_used + 1,
                                    "rate_limit_web_search_fallback",
                                    messages,
                                )
                                return web_response
                            else:
                                logger.warning(
                                    "web_search_fallback_vazio user_id=%s resultado=%s",
                                    user_id,
                                    search_result,
                                )
                        except Exception as web_e:
                            logger.warning("fallback_web_search_429 error=%s", web_e)

                    # Fallback 3: read_file para perguntas sobre arquivos
                    if self._user_asked_to_read_file(user_message):
                        path = self._extract_file_path(user_message)
                        if path:
                            try:
                                from workspace.tools.filesystem import read_file

                                result = await read_file(path)
                                if result.get("success") and result.get("content"):
                                    content = self._truncate(result["content"], 4000)
                                    msg = (
                                        "⚠️ API principal indisponível no momento.\n\n"
                                        "📄 **Conteúdo do arquivo solicitado:**\n\n"
                                        f"{content}"
                                    )
                                    logger.info(
                                        "read_file_fallback_429 path=%s bytes=%s",
                                        path,
                                        len(result.get("content", "")),
                                    )
                                    self._finalize_run(
                                        run_dir,
                                        msg,
                                        user_message,
                                        start_time,
                                        tools_used,
                                        "rate_limit_read_file",
                                        messages,
                                    )
                                    return msg
                            except Exception as fe:
                                logger.warning(
                                    "read_file fallback 429 falhou para %s: %s", path, fe
                                )
                            rate_msg += " Perguntas que exigem leitura de arquivos não podem ser atendidas enquanto a API estiver indisponível."

                    # Fallback 4: FactStore (último recurso - APENAS se web_search não foi tentado ou retornou erro)
                    # Se web_search foi tentado e retornou vazio, NÃO usar FactStore para perguntas gerais
                    if (
                        (not web_search_attempted)
                        and not self._user_asked_to_read_file(user_message)
                        and not is_nr_question
                    ):
                        try:
                            mem = self.memory_manager.get_relevant_memory(user_message, max_facts=5)
                            if not mem or len(mem) <= 25:
                                mem = self.memory_manager.get_relevant_memory(
                                    "usuário Bruno preferências contexto", max_facts=5
                                )
                            if mem and len(mem) > 25:
                                note = "Com base na memória (API temporariamente indisponível):\n\n"
                                body = mem.replace("Fatos relevantes:\n", "").strip()
                                logger.info(
                                    "factstore_fallback user_id=%s chars=%s", user_id, len(body)
                                )
                                self._finalize_run(
                                    run_dir,
                                    note + body,
                                    user_message,
                                    start_time,
                                    tools_used,
                                    "rate_limit_factstore_fallback",
                                    messages,
                                )
                                return note + body
                            recent = self.memory_manager.fact_store.get_recent_facts(limit=5)
                            if recent:
                                lines = [f"- {f.content}" for f in recent]
                                body = "\n".join(lines)
                                note = "API temporariamente indisponível. Enquanto isso, eis o que tenho na memória:\n\n"
                                self._finalize_run(
                                    run_dir,
                                    note + body,
                                    user_message,
                                    start_time,
                                    tools_used,
                                    "rate_limit_factstore_fallback",
                                    messages,
                                )
                                return note + body
                        except Exception as mem_e:
                            logger.debug("fallback_memoria_ignorado error=%s", mem_e)

                    self._finalize_run(
                        run_dir,
                        rate_msg,
                        user_message,
                        start_time,
                        tools_used,
                        "rate_limit",
                        messages,
                    )
                    return rate_msg
                is_tool_error = (
                    (
                        "tool_use_failed" in error_msg
                        or "failed_generation" in error_msg
                        or "Failed to call a function" in error_msg
                        or "Error code: 400" in error_msg
                    )
                    and "429" not in error_msg
                    and "rate_limit" not in error_msg.lower()
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
                        fallback_err = str(fallback_e)
                        # Se o fallback (sem tools) também deu 429, tratar como rate limit e tentar Kimi/RAG/memória
                        if self._is_rate_limit_error(fallback_err):
                            _groq_cooldown_until = time.time() + GROQ_COOLDOWN_SECONDS
                            nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
                            glm_key_fb = os.getenv("GLM_API_KEY", "").strip()
                            logger.info(
                                "fallback_429_apos_tool_error nvidia_key_presente=%s glm_key_presente=%s",
                                bool(nvidia_key),
                                bool(glm_key_fb),
                            )
                            if nvidia_key:
                                try:
                                    from workspace.storage.llm_usage import has_reached_daily_limit

                                    if not has_reached_daily_limit(
                                        "nvidia", config.LLM_NVIDIA_DAILY_LIMIT_TOKENS
                                    ):
                                        kimi_content = (
                                            await asyncio.get_event_loop().run_in_executor(
                                                None,
                                                lambda: nvidia_kimi_chat(
                                                    nvidia_key,
                                                    messages,
                                                    max_tokens=4096,
                                                    temperature=0.7,
                                                    timeout=20,
                                                ),
                                            )
                                        )
                                        if kimi_content:
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
                                    logger.warning(
                                        "fallback_kimi_apos_tool_error falhou: %s", kimi_e
                                    )
                            if glm_key_fb:
                                try:
                                    logger.info(
                                        "tentando_fallback_glm_apos_tool_error user_id=%s", user_id
                                    )
                                    glm_content = await asyncio.get_event_loop().run_in_executor(
                                        None,
                                        lambda: glm_chat(
                                            glm_key_fb,
                                            messages,
                                            max_tokens=4096,
                                            temperature=0.7,
                                            timeout=25,
                                        ),
                                    )
                                    if glm_content:
                                        self._finalize_run(
                                            run_dir,
                                            glm_content,
                                            user_message,
                                            start_time,
                                            tools_used,
                                            "fallback_glm",
                                            messages,
                                        )
                                        return glm_content
                                except Exception as glm_e:
                                    logger.warning("fallback_glm_apos_tool_error falhou: %s", glm_e)
                            rate_msg = self._format_rate_limit_message(fallback_err)
                            if not self._user_asked_to_read_file(user_message):
                                try:
                                    mem = self.memory_manager.get_relevant_memory(
                                        user_message, max_facts=5
                                    )
                                    if not mem or len(mem) <= 25:
                                        mem = self.memory_manager.get_relevant_memory(
                                            "usuário Bruno preferências contexto", max_facts=5
                                        )
                                    if mem and len(mem) > 25:
                                        body = mem.replace("Fatos relevantes:\n", "").strip()
                                        note = "Com base na memória (API temporariamente indisponível):\n\n"
                                        self._finalize_run(
                                            run_dir,
                                            note + body,
                                            user_message,
                                            start_time,
                                            tools_used,
                                            "rate_limit_rag_fallback",
                                            messages,
                                        )
                                        return note + body
                                    recent = self.memory_manager.fact_store.get_recent_facts(
                                        limit=5
                                    )
                                    if recent:
                                        body = "\n".join(f"- {f.content}" for f in recent)
                                        note = "API temporariamente indisponível. Enquanto isso, eis o que tenho na memória:\n\n"
                                        self._finalize_run(
                                            run_dir,
                                            note + body,
                                            user_message,
                                            start_time,
                                            tools_used,
                                            "rate_limit_rag_fallback",
                                            messages,
                                        )
                                        return note + body
                                except Exception as mem_e:
                                    logger.debug("fallback_memoria_apos_tool_error error=%s", mem_e)
                            if self._user_asked_to_read_file(user_message):
                                path = self._extract_file_path(user_message)
                                if path:
                                    try:
                                        from workspace.tools.filesystem import read_file

                                        result = await read_file(path)
                                        if result.get("success") and result.get("content"):
                                            content = self._truncate(result["content"], 4000)
                                            msg = (
                                                "⚠️ API principal indisponível no momento.\n\n"
                                                "📄 **Conteúdo do arquivo solicitado:**\n\n"
                                                f"{content}"
                                            )
                                            logger.info(
                                                "read_file_fallback_429 path=%s bytes=%s",
                                                path,
                                                len(result.get("content", "")),
                                            )
                                            self._finalize_run(
                                                run_dir,
                                                msg,
                                                user_message,
                                                start_time,
                                                tools_used,
                                                "rate_limit_read_file",
                                                messages,
                                            )
                                            return msg
                                    except Exception as fe:
                                        logger.warning(
                                            "read_file fallback 429 falhou para %s: %s", path, fe
                                        )
                                rate_msg += " Perguntas que exigem leitura de arquivos não podem ser atendidas enquanto a API estiver indisponível."
                            self._finalize_run(
                                run_dir,
                                rate_msg,
                                user_message,
                                start_time,
                                tools_used,
                                "rate_limit",
                                messages,
                            )
                            return rate_msg
                        fallback_text = "Desculpe, tive um problema ao processar sua solicitação. Tente novamente."
                        self._finalize_run(
                            run_dir,
                            fallback_text,
                            user_message,
                            start_time,
                            tools_used,
                            "error",
                            messages,
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
                                self.run_manager.log_action(
                                    run_dir, tool_name, tool_args, result, tools_used
                                )
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
                self._finalize_run(
                    run_dir, output_text, user_message, start_time, tools_used, status, messages
                )
                if should_cache_query(user_message):
                    response_cache.set(user_message, output_text)
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
                            iteration=tools_used,
                        )
                    except Exception as e:
                        logger.error(f"Erro ao logar acao: {e}")

                # Para read_file com conteúdo longo: expor estrutura (##/###) e truncar para o modelo ancorar no real
                if tool_name == "read_file" and result.get("success") and result.get("content"):
                    content = result["content"]
                    if len(content) > 10000:
                        structure = self._extract_markdown_headings(content)
                        result = {
                            "success": True,
                            "path": result.get("path", ""),
                            "structure": structure,
                            "content": content[:14000]
                            + "\n\n[... documento truncado; use a estrutura (títulos acima) para o resumo ...]",
                        }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

    def _finalize_run(
        self, run_dir, output_text, user_message, start_time, tools_used, status, messages
    ):
        """Salva output e metrics no final do run"""
        if not run_dir:
            return

        try:
            duration = (time.time() - start_time) * 1000  # ms

            # Estimar tokens (aprox. 4 chars por token)
            tokens_input = (
                sum(
                    len(m.get("content", ""))
                    for m in messages
                    if m.get("role") in ["system", "user"]
                )
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
            if status in (
                "success",
                "fallback_no_tools",
                "rate_limit",
                "rate_limit_rag_fallback",
                "daily_limit_groq",
            ):
                provider = "groq"
            elif status == "fallback_kimi":
                provider = "nvidia"
            elif status == "fallback_glm":
                provider = "glm"

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
