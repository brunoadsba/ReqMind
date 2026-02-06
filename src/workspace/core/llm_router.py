"""Roteador de LLMs (fase 1 - apenas Groq).

Nesta fase o LlmRouter encapsula apenas as chamadas ao Groq, com retry e
configuração centralizada de modelo/limites. A lógica de fallback (NVIDIA Kimi
e RAG) permanece em `agent.py` e será migrada para cá em fases posteriores.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from groq import Groq

from config.settings import config
from utils.retry import retry_with_backoff_sync
from workspace.storage.llm_usage import has_reached_daily_limit

logger = logging.getLogger(__name__)


@dataclass
class GroqChatClient:
    """Cliente fino para chamadas de chat no Groq."""

    client: Groq
    model: str

    @staticmethod
    @retry_with_backoff_sync(
        max_retries=3,
        exceptions=(ConnectionError, TimeoutError, OSError),
    )
    def _chat_sync(
        groq_client: Groq,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs: Any,
    ):
        """Chamada Groq chat síncrona com retry."""
        max_tokens = kwargs.get("max_tokens") or config.GROQ_MAX_TOKENS
        temperature = kwargs.get("temperature", 0.7)

        if tools is not None:
            return groq_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        return groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ):
        """Wrapper de conveniência para chamadas de chat."""
        return self._chat_sync(
            self.client,
            self.model,
            messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
            temperature=temperature,
        )


@dataclass
class LlmRouter:
    """Roteador de LLMs.

    Fase 1: apenas Groq, sem quotas nem rotação de provedores.
    """

    groq_client: GroqChatClient

    @classmethod
    def from_env(cls) -> "LlmRouter":
        """Cria roteador usando variáveis de ambiente e config global."""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.warning("GROQ_API_KEY não configurada – chamadas ao LLM irão falhar")
        client = Groq(api_key=groq_api_key)

        # Preferir modelo configurado em settings; cair para default histórico se ausente
        model_name = getattr(config, "GROQ_MODEL_CHAT", "llama-3.3-70b-versatile")
        return cls(groq_client=GroqChatClient(client=client, model=model_name))

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        user_id: Optional[int] = None,  # reservado para quotas futuras
    ):
        """Ponto único de entrada para chamadas ao LLM.

        Por enquanto apenas delega para o Groq, mas já aceita `user_id` para
        futura implementação de quotas por usuário/provedor.
        """
        # Limite diário opcional por provedor (Groq)
        daily_limit = config.LLM_GROQ_DAILY_LIMIT_TOKENS
        if has_reached_daily_limit("groq", daily_limit):
            # Exceção específica tratada em Agent.run
            raise RuntimeError("LLM_GROQ_DAILY_LIMIT_REACHED")

        return self.groq_client.chat(
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
            temperature=temperature,
        )

