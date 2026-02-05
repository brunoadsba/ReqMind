"""FactStore - Armazenamento de fatos com busca semantica

Usa TF-IDF + similaridade de cosseno (sem dependencias pesadas)
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Fact:
    """Representa um fato armazenado"""
    id: str
    content: str
    timestamp: str
    source: str
    tags: List[str]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Fact":
        return cls(**data)


class SimpleVectorizer:
    """Vectorizador simples baseado em TF-IDF manual"""
    
    def __init__(self, max_features: int = 100):
        self.max_features = max_features
        self.vocab = {}
        self.idf = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto em palavras"""
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,15}\b', text)
        return words
    
    def _get_vocab(self, texts: List[str]):
        """Constroi vocabulario a partir de textos"""
        word_freq = {}
        for text in texts:
            words = self._tokenize(text)
            for word in set(words):
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Seleciona palavras mais frequentes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        self.vocab = {word: i for i, (word, _) in enumerate(sorted_words[:self.max_features])}
    
    def _compute_idf(self, texts: List[str]):
        """Calcula IDF para cada palavra no vocabulario"""
        n_docs = len(texts)
        for word in self.vocab:
            doc_count = sum(1 for text in texts if word in text.lower())
            self.idf[word] = 1 + (n_docs / (doc_count + 1))
    
    def fit(self, texts: List[str]):
        """Treina o vectorizador"""
        self._get_vocab(texts)
        self._compute_idf(texts)
        return self
    
    def transform(self, text: str) -> List[float]:
        """Transforma texto em vetor"""
        if not self.vocab:
            return [0.0] * self.max_features
        
        words = self._tokenize(text)
        vec = [0.0] * len(self.vocab)
        
        for word in words:
            if word in self.vocab:
                idx = self.vocab[word]
                vec[idx] += 1
        
        # Aplica IDF
        for word, idx in self.vocab.items():
            if word in self.idf:
                vec[idx] *= self.idf[word]
        
        return vec


class FactStore:
    """Armazenamento de fatos com busca semantica"""
    
    def __init__(self, memory_dir: Path = None):
        if memory_dir is None:
            from config import config
            memory_dir = config.WORKSPACE_DIR / "memory"
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos
        self.facts_file = self.memory_dir / "facts.jsonl"
        self.index_file = self.memory_dir / "facts.index"
        
        # Vectorizador
        self.vectorizer = SimpleVectorizer(max_features=100)
        self.facts: Dict[str, Fact] = {}
        
        # Carrega fatos existentes
        self._load_facts()
        
        # Se nao tem fatos, inicializa com vocabulario basico
        if not self.facts:
            self._init_vocab()
    
    def _init_vocab(self):
        """Inicializa vocabulario com palavras comuns em portugues"""
        common_words = [
            "arquivo", "diretorio", "projeto", "caminho", "codigo",
            "funcao", "classe", "metodo", "configuracao", "usuario",
            "senha", "token", "api", "servidor", "database",
            "backup", "erro", "sucesso", "teste", "deploy",
            "python", "javascript", "docker", "git", "comando",
            "dados", "entrada", "saida", "resultado", "execucao",
            "bruno", "moltbot", "assistente", "bot", "telegram",
            "workspace", "memory", "agent", "runs", "config"
        ]
        self.vectorizer.vocab = {word: i for i, word in enumerate(common_words)}
        self.vectorizer.idf = {word: 1.0 for word in common_words}
    
    def _load_facts(self):
        """Carrega fatos do arquivo JSONL"""
        if not self.facts_file.exists():
            return
        
        texts = []
        with open(self.facts_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    fact = Fact.from_dict(json.loads(line))
                    self.facts[fact.id] = fact
                    texts.append(fact.content)
        
        # Treina vectorizador
        if texts:
            self.vectorizer.fit(texts)
            # Re-calcula embeddings
            for fact in self.facts.values():
                fact.embedding = self.vectorizer.transform(fact.content)
    
    def _save_fact(self, fact: Fact):
        """Salva um fato no arquivo JSONL"""
        with open(self.facts_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(fact.to_dict(), ensure_ascii=False) + '\n')
    
    def _generate_id(self, content: str) -> str:
        """Gera ID unico baseado no conteudo"""
        hash_content = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"fact_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash_content}"
    
    def add_fact(self, content: str, source: str = None, tags: List[str] = None) -> str:
        """Adiciona um novo fato"""
        # Verifica duplicacao simples
        for fact in self.facts.values():
            if fact.content == content:
                return fact.id  # Ja existe
        
        # Cria novo fato
        fact_id = self._generate_id(content)
        embedding = self.vectorizer.transform(content)
        
        fact = Fact(
            id=fact_id,
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
            source=source or "manual",
            tags=tags or [],
            embedding=embedding
        )
        
        self.facts[fact_id] = fact
        self._save_fact(fact)
        
        return fact_id
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade de cosseno"""
        if not vec1 or not vec2:
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a ** 2 for a in vec1) ** 0.5
        norm2 = sum(b ** 2 for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot / (norm1 * norm2)
    
    def search_facts(self, query: str, top_k: int = 5, threshold: float = 0.1) -> List[Tuple[Fact, float]]:
        """Busca fatos semanticamente similares"""
        if not self.facts:
            return []
        
        query_vec = self.vectorizer.transform(query)
        
        scores = []
        for fact in self.facts.values():
            if fact.embedding:
                sim = self._cosine_similarity(query_vec, fact.embedding)
                if sim >= threshold:
                    scores.append((fact, sim))
        
        # Ordena por similaridade
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Retorna um fato pelo ID"""
        return self.facts.get(fact_id)
    
    def get_recent_facts(self, limit: int = 10) -> List[Fact]:
        """Retorna fatos mais recentes"""
        sorted_facts = sorted(
            self.facts.values(),
            key=lambda f: f.timestamp,
            reverse=True
        )
        return sorted_facts[:limit]
    
    def get_stats(self) -> Dict:
        """Retorna estatisticas do store"""
        return {
            "total_facts": len(self.facts),
            "vocab_size": len(self.vectorizer.vocab),
            "facts_with_embeddings": sum(1 for f in self.facts.values() if f.embedding)
        }


__all__ = ["FactStore", "Fact", "SimpleVectorizer"]
