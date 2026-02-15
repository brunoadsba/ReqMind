"""
Sistema de cache inteligente para o bot.

Implementa cache LRU (Least Recently Used) para:
- Respostas de perguntas frequentes
- Resultados de web_search
- Dados de memória

Uso:
    from cache import cache

    # Buscar do cache
    result = cache.get("pergunta")
    if result:
        return result

    # Processar e armazenar
    result = processar()
    cache.set("pergunta", result, ttl=300)  # 5 minutos
"""

import time
import hashlib
from typing import Any, Optional, Dict
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """Cache LRU simples e eficiente."""

    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """
        Args:
            max_size: Número máximo de itens no cache
            default_ttl: Tempo de vida padrão em segundos (5 min)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _generate_key(self, text: str) -> str:
        """Gera chave única para o texto (normalizado)."""
        # Normaliza: lowercase, remove espaços extras
        normalized = " ".join(text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def get(self, key: str) -> Optional[Any]:
        """
        Busca item no cache.

        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        cache_key = self._generate_key(key)

        if cache_key not in self._cache:
            self._misses += 1
            return None

        item = self._cache[cache_key]

        # Verifica se expirou
        if time.time() > item["expires_at"]:
            del self._cache[cache_key]
            self._misses += 1
            return None

        # Move para o final (mais recentemente usado)
        self._cache.move_to_end(cache_key)
        self._hits += 1

        return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena item no cache.

        Args:
            key: Chave de identificação
            value: Valor a armazenar
            ttl: Tempo de vida em segundos (usa default se None)
        """
        cache_key = self._generate_key(key)

        # Se já existe, atualiza e move para o final
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)

        # Se atingiu capacidade máxima, remove o mais antigo
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[cache_key] = {
            "value": value,
            "expires_at": time.time() + (ttl or self.default_ttl),
        }

    def invalidate(self, key: str) -> bool:
        """Remove item específico do cache."""
        cache_key = self._generate_key(key)
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
        }

    def cleanup_expired(self) -> int:
        """Remove itens expirados. Retorna número de itens removidos."""
        now = time.time()
        expired = [key for key, item in self._cache.items() if now > item["expires_at"]]
        for key in expired:
            del self._cache[key]
        return len(expired)


# Instância global de cache
# Cache de respostas (5 min TTL)
response_cache = LRUCache(max_size=50, default_ttl=300)

# Cache de web_search (10 min TTL)
web_search_cache = LRUCache(max_size=30, default_ttl=600)

# Cache de memória (2 min TTL - mais curto pois muda frequentemente)
memory_cache = LRUCache(max_size=20, default_ttl=120)


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """Retorna estatísticas de todos os caches."""
    return {
        "responses": response_cache.get_stats(),
        "web_search": web_search_cache.get_stats(),
        "memory": memory_cache.get_stats(),
    }


def cleanup_all_caches() -> Dict[str, int]:
    """Limpa caches expirados e retorna quantos foram removidos."""
    return {
        "responses": response_cache.cleanup_expired(),
        "web_search": web_search_cache.cleanup_expired(),
        "memory": memory_cache.cleanup_expired(),
    }


# Perguntas que devem ser cacheadas (respostas estáveis)
CACHEABLE_PATTERNS = [
    "qual é a data",
    "que dia é hoje",
    "que horas são",
    "qual o horário",
    "data e hora",
    "quem é você",
    "o que você faz",
    "quais seus comandos",
    "ajuda",
    "help",
    "status",
    "oque você sabe sobre mim",
    "o que você sabe sobre mim",
]


def should_cache_query(query: str) -> bool:
    """
    Determina se uma query deve ser cacheada.

    Args:
        query: Texto da pergunta

    Returns:
        True se deve cachear, False caso contrário
    """
    normalized = query.lower().strip()

    # Não cachear perguntas pessoais/complexas
    if len(normalized) > 100:
        return False

    # Não cachear se contém palavras de tempo real
    time_words = ["clima", "preço", "cotação", "notícias", "hoje", "agora"]
    if any(word in normalized for word in time_words):
        return False

    # Cachear se corresponde a padrões conhecidos
    return any(pattern in normalized for pattern in CACHEABLE_PATTERNS)


# Exporta instâncias principais
__all__ = [
    "response_cache",
    "web_search_cache",
    "memory_cache",
    "get_cache_stats",
    "cleanup_all_caches",
    "should_cache_query",
    "LRUCache",
]
