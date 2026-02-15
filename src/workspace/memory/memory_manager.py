"""MemoryManager - Gerenciador de memoria inteligente

Integra FactStore com extração automática de fatos das conversas.
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from workspace.memory.fact_store import FactStore, Fact
try:
    from features.hippocampus.client import HippocampusClient, MemoryType
except ImportError:
    HippocampusClient = None
    logger.warning("HippocampusClient não disponível (import failed)")


logger = logging.getLogger(__name__)


class MemoryManager:
    """Gerenciador inteligente de memoria do agente"""
    
    def __init__(self, memory_dir: Path = None):
        if memory_dir is None:
            from config import config
            memory_dir = config.WORKSPACE_DIR / "memory"
        
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # FactStore
        self.fact_store = FactStore(self.memory_dir)

        # Hippocampus (Lite)
        self.hippocampus = None
        if HippocampusClient:
            try:
                self.hippocampus = HippocampusClient(str(self.memory_dir / "hippocampus"))
            except Exception as e:
                logger.error(f"Falha ao iniciar Hippocampus: {e}")
        
        # Padrões para extração de fatos
        self.fact_patterns = [
            (r"(?:projeto|diretório|caminho) [ée]stá? em ([/\w~.-]+)", "path"),
            (r"(?:versão|versao) [ée] ([\d.]+)", "version"),
            (r"(?:usuário|login) [ée] (\w+)", "user"),
            (r"(?:token|senha|chave) [ée] (\S+)", "secret"),
            (r"(?:porta|port) [ée] (\d+)", "port"),
            (r"ip [ée] (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", "ip"),
        ]
        
        # Padrões de dados sensíveis que devem ser bloqueados
        self.sensitive_patterns = [
            r"(?:senha|password|passwd)\s*[:=]\s*\S+",
            r"(?:token|api[_-]?key|secret|chave)\s*[:=]\s*\S+",
            r"(?:senha|password)\s+(?:do|da|é|e)\s+\S+\s*[:=]\s*\S+",
            r"bearer\s+\S+",
            r"authorization:\s+\S+",
        ]
    
    def _contains_sensitive_data(self, content: str) -> bool:
        """Verifica se o conteúdo contém dados sensíveis que não devem ser armazenados"""
        content_lower = content.lower()
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        return False
    
    def add_fact(self, content: str, source: str = None, tags: List[str] = None, 
                 auto_extract: bool = True) -> Optional[str]:
        """Adiciona um fato, opcionalmente extraindo metadados
        
        Retorna None se o conteúdo contiver dados sensíveis (não armazena).
        """
        # Sanitização: bloqueia dados sensíveis
        if self._contains_sensitive_data(content):
            logger.warning(
                "memoria_bloqueada_dados_sensiveis source=%s len=%d",
                source or "unknown", len(content)
            )
            return None
        
        # Extrai tags automaticamente se necessario
        if auto_extract and not tags:
            tags = self._extract_tags(content)
        
        # Adiciona ao FactStore
        fact_id = self.fact_store.add_fact(content, source, tags)
        
        return fact_id
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extrai tags automaticamente do conteudo"""
        tags = []
        content_lower = content.lower()
        
        # Palavras-chave
        keywords = {
            "projeto": ["projeto", "project", "app", "sistema"],
            "config": ["configuracao", "config", "settings", ".env"],
            "caminho": ["caminho", "path", "diretorio", "pasta", "folder"],
            "seguranca": ["senha", "password", "token", "key", "secret"],
            "tech": ["python", "javascript", "docker", "api", "llm"],
            "infra": ["servidor", "server", "porta", "host", "deploy"],
        }
        
        for tag, words in keywords.items():
            if any(word in content_lower for word in words):
                tags.append(tag)
        
        return tags or ["general"]
    
    def extract_facts_from_message(self, message: str, context: str = None) -> List[str]:
        """Extrai fatos de uma mensagem automaticamente
        
        Ignora automaticamente fatos que contenham dados sensíveis.
        """
        extracted_facts = []
        
        for pattern, tag in self.fact_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                fact_content = match.group(0)
                if len(fact_content) > 10:  # Evita fatos muito curtos
                    fact_id = self.add_fact(
                        content=fact_content,
                        source=context or "auto_extract",
                        tags=[tag, "auto"]
                    )
                    # add_fact retorna None se contiver dados sensíveis
                    if fact_id:
                        extracted_facts.append(fact_id)
        
        return extracted_facts
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Busca fatos relevantes"""
        results = self.fact_store.search_facts(query, top_k=top_k)
        return [(fact.content, score) for fact, score in results]

    @staticmethod
    def _is_about_me_query(msg: str) -> bool:
        """True se a mensagem pergunta sobre o usuário / preferências / o que o bot sabe sobre mim."""
        if not (msg or msg.strip()):
            return False
        lower = msg.strip().lower()
        triggers = (
            "sabe sobre mim",
            "sabe de mim",
            "informações sobre mim",
            "informacoes sobre mim",
            "o que tem salvo",
            "minhas preferências",
            "minhas preferencias",
            "o que você sabe sobre mim",
            "o que voce sabe sobre mim",
        )
        return any(t in lower for t in triggers)

    def get_relevant_memory(self, user_message: str, max_facts: int = 3) -> str:
        """Retorna fatos relevantes como contexto para o agente."""
        results = self.search(user_message, top_k=max_facts)

        # Fallback: perguntas "sobre mim" podem não dar match na busca; usa query genérica de usuário
        if not results and self._is_about_me_query(user_message):
            fallback_query = "usuário Bruno preferências contexto do usuário do bot"
            results = self.search(fallback_query, top_k=max_facts)
        if not results and self._is_about_me_query(user_message):
            # Último recurso: fatos recentes (podem ser sobre o usuário)
            recent = self.fact_store.get_recent_facts(limit=max_facts)
            results = [(f.content, 0.5) for f in recent]

        # Busca no Hippocampus (Semântica + Episódica)
        hippocampus_context = ""
        if self.hippocampus:
            try:
                hippocampus_context = self.hippocampus.recall(user_message, "user_default", top_k=3)
            except Exception as e:
                logger.error(f"Erro no recall do Hippocampus: {e}")

        memory_context = ""
        if results:
            memory_context = "Fatos relevantes:\n"
            for content, score in results:
                if score > 0.1:
                    memory_context += f"- {content}\n"

        if hippocampus_context:
            memory_context += "\n[Memória Hippocampus]:\n" + hippocampus_context

        return memory_context if len(memory_context) > 20 else ""
    
    def remember_interaction(self, user_message: str, assistant_response: str):
        """Memoriza uma interação completa"""
        # Extrai fatos da mensagem do usuario
        self.extract_facts_from_message(user_message, "user")
        
        # Extrai fatos da resposta (se contiver informações uteis)
        if any(keyword in assistant_response.lower() 
               for keyword in ["diretorio", "caminho", "projeto", "configuracao"]):
            self.extract_facts_from_message(assistant_response, "assistant")
            
        # Salva no Hippocampus (Episodic Stream)
        if self.hippocampus:
            try:
                # 1. O que o usuário disse
                self.hippocampus.remember(
                    content=f"User: {user_message}",
                    user_id="user_default",
                    memory_type=MemoryType.EPISODIC
                )
                # 2. O que o bot respondeu (opcional, pode ser ruido, mas bom para contexto)
                # self.hippocampus.remember(f"Assistant: {assistant_response}", "user_default", MemoryType.EPISODIC)
            except Exception as e:
                logger.error(f"Erro ao salvar memoria no Hippocampus: {e}")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da memória"""
        return {
            "facts": self.fact_store.get_stats(),
            "total_stored": len(self.fact_store.facts)
        }


# Singleton global
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Retorna instância singleton do MemoryManager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


__all__ = ["MemoryManager", "get_memory_manager"]