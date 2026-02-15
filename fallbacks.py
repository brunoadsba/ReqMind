"""
Gerenciador de Fallbacks LLM com retry e verificação de ambiente.

Este módulo implementa a lógica de fallback para quando o Groq retorna 429,
 garantindo que o bot sempre responda mesmo em picos de uso.
"""

import time
import logging
import os
from typing import Optional, Callable, List, Dict, Any

# Configuração de logs para facilitar o debug no Docker
logger = logging.getLogger(__name__)


def call_with_retry(func: Callable, max_retries: int = 3, delay: int = 2):
    """Executa uma função com retry e backoff simples."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise e


class LLMFallbackManager:
    """
    Gerenciador de fallbacks LLM para quando o Groq retorna 429.

    Ordem de fallback:
    1. Groq (principal)
    2. Kimi (NVIDIA) - se configurado
    3. GLM (Zhipu) - se configurado
    4. Resposta de emergência (se tudo falhar)
    """

    def __init__(self):
        self.nvidia_key = os.getenv("NVIDIA_API_KEY", "").strip()
        self.glm_key = os.getenv("GLM_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()

    def check_env(self) -> Dict[str, Any]:
        """
        Verifica se as chaves estão presentes e sem aspas.

        Returns:
            Dict com status de cada chave
        """
        result = {}
        keys = {
            "NVIDIA_API_KEY": self.nvidia_key,
            "GLM_API_KEY": self.glm_key,
            "GROQ_API_KEY": self.groq_key,
        }

        for name, val in keys.items():
            if not val:
                result[name] = {"present": False, "has_quotes": False, "status": "MISSING"}
                logger.error(f"ERRO: {name} não encontrada no ambiente.")
            elif (
                val.startswith('"') or val.endswith('"') or val.startswith("'") or val.endswith("'")
            ):
                result[name] = {"present": True, "has_quotes": True, "status": "HAS_QUOTES"}
                logger.warning(
                    f"AVISO: {name} contém aspas no .env. Isso pode causar falhas de autenticação."
                )
            else:
                result[name] = {"present": True, "has_quotes": False, "status": "OK"}
                logger.info(f"✅ {name} configurada corretamente")

        return result

    def get_fallback_status(self) -> str:
        """Retorna string com status dos fallbacks para logs."""
        nvidia_status = "✅" if self.nvidia_key else "❌"
        glm_status = "✅" if self.glm_key else "❌"
        return f"Fallbacks: NVIDIA={nvidia_status} GLM={glm_status}"

    def call_kimi_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 20,
    ) -> Optional[str]:
        """
        Chama Kimi (NVIDIA) com retry e backoff.

        Args:
            messages: Lista de mensagens no formato OpenAI
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            timeout: Timeout da requisição em segundos

        Returns:
            Conteúdo da resposta ou None se falhar
        """
        if not self.nvidia_key:
            logger.warning("fallback_kimi_pulado: NVIDIA_API_KEY ausente")
            return None

        logger.info("Iniciando fallback para Kimi...")

        def _try_call():
            from workspace.core.nvidia_kimi import chat_completion_sync

            return chat_completion_sync(
                api_key=self.nvidia_key,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )

        try:
            return call_with_retry(_try_call, max_retries=2, delay=2)
        except Exception as e:
            logger.error(f"Fallback Kimi falhou após retries: {e}")
            return None

    def call_glm_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 25,
    ) -> Optional[str]:
        """
        Chama GLM (Zhipu) com retry e backoff.

        Args:
            messages: Lista de mensagens no formato OpenAI
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
            timeout: Timeout da requisição em segundos

        Returns:
            Conteúdo da resposta ou None se falhar
        """
        if not self.glm_key:
            logger.warning("fallback_glm_pulado: GLM_API_KEY ausente")
            return None

        logger.info("Iniciando fallback para GLM...")

        def _try_call():
            from workspace.core.glm_client import chat_completion_sync

            return chat_completion_sync(
                api_key=self.glm_key,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )

        try:
            return call_with_retry(_try_call, max_retries=2, delay=2)
        except Exception as e:
            logger.error(f"Fallback GLM falhou após retries: {e}")
            return None

    def get_emergency_response(self) -> str:
        """
        Retorna resposta de emergência quando todos os fallbacks falham.
        """
        return (
            "⚠️ **API temporariamente indisponível**\n\n"
            "Todas as APIs de IA estão fora do ar no momento.\n"
            "Tente novamente em alguns minutos.\n\n"
            "💡 Você ainda pode usar comandos que não dependem de IA, como:\n"
            "• /status - Verificar status do sistema\n"
            "• /lembretes - Ver seus lembretes agendados\n"
            "• /noticias - Ver notícias (se disponível em cache)"
        )


# Instância global
_fallback_manager: Optional[LLMFallbackManager] = None


def get_fallback_manager() -> LLMFallbackManager:
    """Retorna instância singleton do LLMFallbackManager."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = LLMFallbackManager()
    return _fallback_manager


def check_environment() -> Dict[str, Any]:
    """
    Função utilitária para verificar variáveis de ambiente.
    Use no startup do bot.
    """
    manager = get_fallback_manager()
    return manager.check_env()


# Instrução para verificar envs no Docker:
# docker exec assistente-bot env | grep -E 'NVIDIA|GLM|GROQ'
