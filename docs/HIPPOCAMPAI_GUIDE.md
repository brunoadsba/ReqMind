# 🧠 Guia Completo: HippocampAI para Chatbots
## Implementação de Memória de Longo Prazo em Sistemas Conversacionais

---

## 📋 Sumário

1. [Visão Geral](#1-visão-geral)
2. [Fundamentos Teóricos](#2-fundamentos-teóricos)
3. [Arquitetura do HippocampAI](#3-arquitetura-do-hippocampai)
4. [Tipos de Memória](#4-tipos-de-memória)
5. [Instalação e Configuração](#5-instalação-e-configuração)
6. [Implementação no Chatbot](#6-implementação-no-chatbot)
7. [Casos de Uso](#7-casos-de-uso)
8. [Considerações de Performance](#8-considerações-de-performance)
9. [Troubleshooting](#9-troubleshooting)
10. [Referências](#10-referências)

---

## 1. Visão Geral

### 1.1 O Problema: Chatbots Esquecem

Chatbots tradicionais sofrem de **amnésia contextual**:
- Perdem o contexto entre sessões
- Não lembram preferências do usuário
- Falham em conectar informações dispersas
- Repetem informações já fornecidas

### 1.2 A Solução: HippocampAI

O **HippocampAI** é uma engine de memória inspirada na neurobiologia do hipocampo humano. Ele adiciona:

- ✅ **Memória de longo prazo** persistente
- ✅ **Knowledge Graph** para relacionamentos
- ✅ **Recuperação híbrida** (semântica + lexical + grafo)
- ✅ **Consolidação de memória** (fase de sono)
- ✅ **Multi-agente** com memória compartilhada

### 1.3 Diferença para RAG Tradicional

| Aspecto | RAG Tradicional | HippocampAI |
|---------|----------------|-------------|
| **Armazenamento** | Vetores densos | Vetores + Grafo de Conhecimento |
| **Recuperação** | Similaridade semântica | PageRank Personalizado + RRF |
| **Relacionamentos** | Implícitos | Explícitos (triplas) |
| **Atualização** | Reindexação completa | Atualização incremental |
| **Explicabilidade** | Baixa | Alta (caminhos de recuperação) |

---

## 2. Fundamentos Teóricos

### 2.1 Teoria do Indexamento Hipocampal

Baseado na neurociência:

```
┌─────────────────────────────────────────────────────────────┐
│                    CÉREBRO HUMANO                          │
├─────────────────────────────────────────────────────────────┤
│  Neocórtex (Córtex Temporal)   │   Hipocampo               │
│  • Armazena memórias           │   • Índice dinâmico       │
│  • Representação distribuída   │   • Ponteiros associativos│
│  • Conhecimento semântico      │   • Consolidação          │
└─────────────────────────────────────────────────────────────┘
```

**Analogia com IA**:
- **Neocórtex** = LLM (parâmetros + corpus documental)
- **Hipocampo** = Knowledge Graph + Sistema de indexação

### 2.2 Tipos de Memória de Longo Prazo

```
Memória de Longo Prazo
├── Declarativa (Explícita)
│   ├── Episódica → Eventos, conversas, experiências
│   └── Semântica → Fatos, conceitos, conhecimento
└── Não-Declarativa (Implícita)
    ├── Procedural → Habilidades, comportamentos
    ├── Priming → Associações automáticas
    └── Condicionamento → Respostas aprendidas
```

---

## 3. Arquitetura do HippocampAI

### 3.1 Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    HIPPocampAI ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Entrada    │───▶│  Processamento│───▶│   Storage    │  │
│  │   (Texto)    │    │              │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  OpenIE      │    │  Embeddings  │    │  Qdrant      │  │
│  │  (Triplas)   │    │  (Vetores)   │    │  (Vector DB) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Knowledge   │    │  Importance  │    │  Redis       │  │
│  │  Graph       │    │  Scoring     │    │  (Cache)     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    RECUPERAÇÃO (Query)                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Vector      │    │  BM25        │    │  Graph       │  │
│  │  Search      │    │  Keyword     │    │  Traversal   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             ▼                              │
│                    ┌──────────────┐                        │
│                    │  RRF Fusion  │                        │
│                    │  (Reciprocal │                        │
│                    │   Rank Fusion)│                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Pipeline de Indexação (Offline)

**Fase 1: Extração de Conhecimento**
```python
# Pseudo-código do processo OpenIE
"""
Texto: "João trabalha na Google como engenheiro de ML"
       ↓
Triplas extraídas:
  - (João, trabalha_em, Google)
  - (João, cargo, Engenheiro de ML)
  - (Google, emprega, João)
"""
```

**Fase 2: Enriquecimento do Grafo**
- Adicionar arestas de sinonímia (baseado em embeddings)
- Calcular especificidade dos nós
- Criar matriz de co-ocorrência passagem-nó

**Fase 3: Consolidação (Sleep Phase)**
- Mesclar memórias relacionadas
- Decaimento de importância temporal
- Podar memórias de baixo valor

### 3.3 Pipeline de Recuperação (Online)

**Algoritmo: Personalized PageRank**

```python
# Pseudo-código
"""
1. Identificar nós da query no grafo
2. Ativar nós iniciais com peso baseado em similaridade
3. Executar PageRank personalizado a partir desses nós
4. Rankear passagens baseado na ativação dos nós
5. Combinar com BM25 e Vector Search via RRF
"""
```

---

## 4. Tipos de Memória

### 4.1 Mapeamento para o HippocampAI

| Tipo Biológico | Implementação | Uso no Chatbot |
|----------------|---------------|----------------|
| **Episódica** | `memory_type="conversation"` | Histórico de chats |
| **Semântica** | `memory_type="fact"` | Preferências, perfil |
| **Procedural** | `memory_type="behavioral"` | Tom de voz, estilo |
| **Working** | Context Window | Contexto imediato |

### 4.2 Estrutura de Dados

```json
{
  "memory_id": "uuid",
  "user_id": "user_123",
  "session_id": "session_456",
  "type": "episodic|semantic|procedural",
  "content": "string",
  "embedding": [0.1, 0.2, ...],
  "entities": ["entity1", "entity2"],
  "triples": [
    {"subject": "s", "predicate": "p", "object": "o"}
  ],
  "importance_score": 0.85,
  "timestamp": "2026-02-15T10:00:00Z",
  "access_count": 5,
  "last_accessed": "2026-02-15T12:00:00Z",
  "metadata": {
    "source": "conversation",
    "confidence": 0.92
  }
}
```

---

## 5. Instalação e Configuração

### 5.1 Pré-requisitos

```bash
# Infraestrutura necessária
Docker 20.10+
Python 3.9+
4GB RAM mínimo (8GB recomendado)
```

### 5.2 Instalação

```bash
# Método 1: Docker Compose (Recomendado)
git clone https://github.com/rexdivakar/HippocampAI.git
cd HippocampAI
docker-compose up -d

# Método 2: Instalação local (quando disponível no PyPI)
pip install hippocampai

# Método 3: Instalação do GitHub
pip install git+https://github.com/rexdivakar/HippocampAI.git
```

### 5.3 Configuração do Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  hippocampai-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - qdrant
      - redis

volumes:
  qdrant_storage:
  redis_data:
```

### 5.4 Configuração do Cliente

```python
# config.py
import os
from pydantic_settings import BaseSettings

class HippocampConfig(BaseSettings):
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "chatbot_memories"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hora
    
    # LLM/Embeddings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4"
    
    # Memória
    MAX_CONTEXT_MEMORIES: int = 10
    MEMORY_DECAY_DAYS: int = 30
    IMPORTANCE_THRESHOLD: float = 0.5
    
    class Config:
        env_file = ".env"

config = HippocampConfig()
```

---

## 6. Implementação no Chatbot

### 6.1 Estrutura do Projeto

```
chatbot-hippocampai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configurações
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── client.py        # Cliente HippocampAI
│   │   ├── types.py         # Tipos de memória
│   │   └── manager.py       # Gerenciador de memória
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── engine.py        # Motor de conversação
│   │   └── context.py       # Montagem de contexto
│   └── models/
│       └── schemas.py       # Pydantic models
├── docker-compose.yml
├── requirements.txt
└── .env
```

### 6.2 Cliente HippocampAI

```python
# app/memory/client.py
from typing import List, Dict, Optional, Literal
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import redis
import json
import hashlib
from datetime import datetime, timedelta
import networkx as nx
from collections import defaultdict

class MemoryType:
    EPISODIC = "episodic"      # Conversas, eventos
    SEMANTIC = "semantic"      # Fatos, preferências
    PROCEDURAL = "procedural"  # Comportamentos, estilo

class HippocampMemoryClient:
    """
    Cliente de memória inspirado no hipocampo humano.
    Implementa Knowledge Graph + Vector Search + Cache.
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        redis_url: str = "redis://localhost:6379",
        openai_api_key: str = None,
        collection_name: str = "memories"
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.redis = redis.from_url(redis_url, decode_responses=True)
        openai.api_key = openai_api_key
        
        self.collection_name = collection_name
        self.embedding_model = "text-embedding-3-small"
        self.graph = nx.DiGraph()  # Knowledge Graph em memória
        
        # Inicializar coleção
        self._init_collection()
    
    def _init_collection(self):
        """Inicializa coleção no Qdrant se não existir"""
        try:
            self.qdrant.get_collection(self.collection_name)
        except:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=Distance.COSINE
                )
            )
    
    def _get_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI"""
        cache_key = f"emb:{hashlib.md5(text.encode()).hexdigest()}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        response = openai.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        embedding = response.data[0].embedding
        
        # Cache por 24 horas
        self.redis.setex(cache_key, 86400, json.dumps(embedding))
        return embedding
    
    def _extract_triples(self, text: str) -> List[Dict]:
        """
        Extrai triplas (sujeito, predicado, objeto) do texto.
        Simplificação - em produção usar OpenIE ou LLM.
        """
        # TODO: Implementar extração real usando LLM
        # Exemplo simplificado:
        triples = []
        # Lógica de extração aqui
        return triples
    
    def _calculate_importance(self, text: str, memory_type: str) -> float:
        """
        Calcula score de importância baseado em:
        - Tipo de memória
        - Entidades nomeadas
        - Sentimento
        - Urgência implícita
        """
        base_score = 0.5
        
        # Memórias procedurais têm maior importância
        if memory_type == MemoryType.PROCEDURAL:
            base_score += 0.3
        
        # Memórias com entidades específicas são mais importantes
        # TODO: Análise mais sofisticada
        
        return min(base_score, 1.0)
    
    def remember(
        self,
        content: str,
        user_id: str,
        memory_type: Literal["episodic", "semantic", "procedural"] = "episodic",
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Armazena uma nova memória.
        
        Args:
            content: Conteúdo da memória
            user_id: ID do usuário
            memory_type: Tipo de memória
            session_id: ID da sessão (opcional)
            metadata: Metadados adicionais
            
        Returns:
            memory_id: ID único da memória
        """
        # Gerar embedding
        embedding = self._get_embedding(content)
        
        # Extrair entidades e triplas
        triples = self._extract_triples(content)
        entities = list(set([t["subject"] for t in triples] + 
                           [t["object"] for t in triples]))
        
        # Calcular importância
        importance = self._calculate_importance(content, memory_type)
        
        # Criar ponto de memória
        memory_id = hashlib.md5(
            f"{user_id}:{content}:{datetime.now()}".encode()
        ).hexdigest()
        
        memory_data = {
            "id": memory_id,
            "user_id": user_id,
            "session_id": session_id,
            "type": memory_type,
            "content": content,
            "entities": entities,
            "triples": triples,
            "importance_score": importance,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "metadata": metadata or {}
        }
        
        # Armazenar no Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(
                id=memory_id,
                vector=embedding,
                payload=memory_data
            )]
        )
        
        # Atualizar Knowledge Graph
        for triple in triples:
            self.graph.add_edge(
                triple["subject"],
                triple["object"],
                relation=triple["predicate"],
                memory_id=memory_id
            )
        
        # Invalidar cache de consultas relacionadas
        self._invalidate_user_cache(user_id)
        
        return memory_id
    
    def recall(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        memory_type: Optional[str] = None,
        use_graph: bool = True
    ) -> List[Dict]:
        """
        Recupera memórias relevantes usando múltiplas estratégias.
        
        Estratégias:
        1. Vector Search (similaridade semântica)
        2. BM25 (matching lexical)
        3. Graph Traversal (se use_graph=True)
        4. RRF Fusion (combinação dos rankings)
        """
        # Check cache
        cache_key = f"recall:{user_id}:{hashlib.md5(query.encode()).hexdigest()}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 1. Vector Search
        query_embedding = self._get_embedding(query)
        vector_results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter={
                "must": [{"key": "user_id", "match": {"value": user_id}}]
            },
            limit=top_k * 2
        )
        
        memories = []
        vector_scores = {}
        
        for idx, result in enumerate(vector_results):
            memory = result.payload
            if memory_type and memory["type"] != memory_type:
                continue
            
            memory["vector_score"] = result.score
            vector_scores[memory["id"]] = idx + 1
            memories.append(memory)
        
        # 2. Graph-based retrieval (Personalized PageRank simplificado)
        if use_graph and self.graph.number_of_nodes() > 0:
            # Encontrar nós relevantes na query
            query_entities = self._extract_entities_from_query(query)
            
            if query_entities:
                # Calcular PageRank a partir dos nós da query
                pagerank = nx.pagerank(
                    self.graph,
                    personalization={
                        node: 1.0 for node in query_entities 
                        if node in self.graph
                    }
                )
                
                # Boostar memórias conectadas aos nós importantes
                for memory in memories:
                    graph_score = 0
                    for entity in memory.get("entities", []):
                        if entity in pagerank:
                            graph_score += pagerank[entity]
                    memory["graph_score"] = graph_score
        
        # 3. RRF (Reciprocal Rank Fusion)
        final_scores = {}
        
        for memory in memories:
            mid = memory["id"]
            
            # Vector rank
            vector_rank = vector_scores.get(mid, 1000)
            
            # Importance boost
            importance_boost = memory.get("importance_score", 0.5) * 10
            
            # Recency boost
            days_old = (datetime.now() - datetime.fromisoformat(
                memory["timestamp"]
            )).days
            recency_boost = max(0, 30 - days_old) / 3
            
            # RRF Score
            final_scores[mid] = (
                1.0 / (60 + vector_rank) +  # Vector
                1.0 / (60 + importance_boost) +  # Importance
                1.0 / (60 + recency_boost)       # Recency
            )
            
            if "graph_score" in memory:
                final_scores[mid] += memory["graph_score"] * 0.1
        
        # Ordenar e retornar top_k
        sorted_memories = sorted(
            memories,
            key=lambda x: final_scores.get(x["id"], 0),
            reverse=True
        )[:top_k]
        
        # Atualizar access_count
        for memory in sorted_memories:
            self._update_access_stats(memory["id"])
        
        # Cache resultados por 5 minutos
        self.redis.setex(cache_key, 300, json.dumps(sorted_memories))
        
        return sorted_memories
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extrai entidades da query do usuário"""
        # TODO: Implementar NER
        return []
    
    def _update_access_stats(self, memory_id: str):
        """Atualiza estatísticas de acesso"""
        # TODO: Implementar atualização no Qdrant
        pass
    
    def _invalidate_user_cache(self, user_id: str):
        """Invalida cache do usuário quando novas memórias são adicionadas"""
        pattern = f"recall:{user_id}:*"
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
    
    def consolidate(self, user_id: str):
        """
        Fase de sono: consolida memórias relacionadas.
        - Mescla memórias similares
        - Remove duplicatas
        - Atualiza importância baseado em acessos
        """
        # TODO: Implementar consolidação
        pass
    
    def get_memory_context(
        self,
        user_id: str,
        current_query: str,
        max_tokens: int = 2000
    ) -> str:
        """
        Monta contexto de memória para o LLM.
        
        Estratégia:
        1. Recuperar memórias relevantes
        2. Ordenar por relevância e importância
        3. Respeitar limite de tokens
        4. Formatar para o prompt
        """
        memories = self.recall(current_query, user_id, top_k=10)
        
        if not memories:
            return ""
        
        context_parts = []
        current_tokens = 0
        
        # Memórias semânticas primeiro (perfil, preferências)
        semantic = [m for m in memories if m["type"] == MemoryType.SEMANTIC]
        episodic = [m for m in memories if m["type"] == MemoryType.EPISODIC]
        procedural = [m for m in memories if m["type"] == MemoryType.PROCEDURAL]
        
        # Ordem de prioridade: Procedural > Semântico > Episódico
        ordered = procedural + semantic + episodic
        
        for memory in ordered:
            content = memory["content"]
            mem_type = memory["type"]
            
            # Estimativa simples de tokens (1 token ≈ 4 chars)
            estimated_tokens = len(content) // 4 + 10
            
            if current_tokens + estimated_tokens > max_tokens:
                break
            
            prefix = {
                MemoryType.SEMANTIC: "[Fato]",
                MemoryType.EPISODIC: "[Histórico]",
                MemoryType.PROCEDURAL: "[Estilo]"
            }.get(mem_type, "[Info]")
            
            context_parts.append(f"{prefix} {content}")
            current_tokens += estimated_tokens
        
        return "\\n".join(context_parts)
```

### 6.3 Motor de Chat com Memória

```python
# app/chat/engine.py
from typing import List, Dict
import openai
from app.memory.client import HippocampMemoryClient, MemoryType

class HippocampChatEngine:
    """
    Motor de conversação com memória de longo prazo.
    """
    
    def __init__(self, memory_client: HippocampMemoryClient):
        self.memory = memory_client
        self.conversation_buffer = {}  # Buffer por sessão
    
    async def chat(
        self,
        message: str,
        user_id: str,
        session_id: str,
        system_prompt: str = None
    ) -> Dict:
        """
        Processa mensagem do usuário com contexto de memória.
        """
        # 1. Recuperar contexto de memória
        memory_context = self.memory.get_memory_context(
            user_id=user_id,
            current_query=message,
            max_tokens=1500
        )
        
        # 2. Construir mensagens para o LLM
        messages = self._build_messages(
            system_prompt=system_prompt,
            memory_context=memory_context,
            user_message=message,
            session_id=session_id
        )
        
        # 3. Gerar resposta
        response = await openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_message = response.choices[0].message.content
        
        # 4. Armazenar interação na memória
        self._store_interaction(
            user_id=user_id,
            session_id=session_id,
            user_message=message,
            assistant_message=assistant_message
        )
        
        # 5. Extrair e armazenar fatos importantes
        await self._extract_facts(
            user_id=user_id,
            session_id=session_id,
            conversation=[message, assistant_message]
        )
        
        return {
            "response": assistant_message,
            "memories_used": len(memory_context.split("\\n")) if memory_context else 0,
            "session_id": session_id
        }
    
    def _build_messages(
        self,
        system_prompt: str,
        memory_context: str,
        user_message: str,
        session_id: str
    ) -> List[Dict]:
        """Constrói lista de mensagens para o LLM"""
        
        # System prompt com contexto de memória
        full_system = system_prompt or "Você é um assistente útil."
        
        if memory_context:
            full_system += f"\\n\\nContexto do usuário:\\n{memory_context}"
        
        messages = [
            {"role": "system", "content": full_system},
        ]
        
        # Adicionar histórico recente do buffer
        if session_id in self.conversation_buffer:
            messages.extend(self.conversation_buffer[session_id][-6:])  # Últimas 3 interações
        
        # Mensagem atual
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _store_interaction(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_message: str
    ):
        """Armazena interação na memória episódica"""
        
        # Armazenar mensagem do usuário
        self.memory.remember(
            content=f"Usuário disse: {user_message}",
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            session_id=session_id,
            metadata={"role": "user", "session_id": session_id}
        )
        
        # Armazenar resposta do assistente
        self.memory.remember(
            content=f"Assistente respondeu: {assistant_message}",
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            session_id=session_id,
            metadata={"role": "assistant", "session_id": session_id}
        )
        
        # Atualizar buffer
        if session_id not in self.conversation_buffer:
            self.conversation_buffer[session_id] = []
        
        self.conversation_buffer[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ])
        
        # Manter apenas últimas 10 interações no buffer
        self.conversation_buffer[session_id] = self.conversation_buffer[session_id][-20:]
    
    async def _extract_facts(
        self,
        user_id: str,
        session_id: str,
        conversation: List[str]
    ):
        """
        Usa LLM para extrair fatos semânticos da conversa.
        """
        prompt = f"""Analise a seguinte conversa e extraia fatos importantes sobre o usuário 
(preferências, informações pessoais, objetivos). Retorne como bullet points:

Conversa:
{chr(10).join(conversation)}

Fatos:"""
        
        response = await openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        facts_text = response.choices[0].message.content
        
        # Armazenar cada fato como memória semântica
        for line in facts_text.split("\\n"):
            line = line.strip()
            if line and line.startswith("-"):
                fact = line[1:].strip()
                self.memory.remember(
                    content=fact,
                    user_id=user_id,
                    memory_type=MemoryType.SEMANTIC,
                    session_id=session_id,
                    metadata={"extracted": True, "source": "conversation"}
                )
```

### 6.4 API FastAPI

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

from app.memory.client import HippocampMemoryClient
from app.chat.engine import HippocampChatEngine
from app.config import config

app = FastAPI(title="Chatbot com HippocampAI")

# Inicializar clientes
memory_client = HippocampMemoryClient(
    qdrant_url=config.QDRANT_URL,
    redis_url=config.REDIS_URL,
    openai_api_key=config.OPENAI_API_KEY
)

chat_engine = HippocampChatEngine(memory_client)

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    memories_used: int

class MemoryRequest(BaseModel):
    content: str
    user_id: str
    memory_type: str = "episodic"
    metadata: Optional[dict] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal de conversação"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        result = await chat_engine.chat(
            message=request.message,
            user_id=request.user_id,
            session_id=session_id,
            system_prompt=request.system_prompt
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            memories_used=result["memories_used"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory")
async def create_memory(request: MemoryRequest):
    """Adicionar memória manualmente"""
    try:
        memory_id = memory_client.remember(
            content=request.content,
            user_id=request.user_id,
            memory_type=request.memory_type,
            metadata=request.metadata
        )
        return {"memory_id": memory_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{user_id}")
async def get_memories(
    user_id: str,
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 10
):
    """Recuperar memórias do usuário"""
    try:
        memories = memory_client.recall(
            query=query or "*",
            user_id=user_id,
            top_k=limit,
            memory_type=memory_type
        )
        return {"memories": memories, "count": len(memories)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consolidate/{user_id}")
async def consolidate_memories(user_id: str):
    """Executar consolidação de memórias (fase de sono)"""
    try:
        memory_client.consolidate(user_id)
        return {"status": "consolidation_complete", "user_id": user_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 7. Casos de Uso

### 7.1 Assistente Pessoal

```python
# Exemplo: Assistente que lembra preferências

async def personal_assistant_example():
    """
    Demonstração de memória semântica para preferências.
    """
    user_id = "user_123"
    
    # Conversa 1 - Primeira interação
    result1 = await chat_engine.chat(
        message="Meu nome é Carlos e sou alérgico a amendoim",
        user_id=user_id,
        session_id="session_1"
    )
    
    # Conversa 2 - Dias depois (nova sessão)
    result2 = await chat_engine.chat(
        message="Quero pedir comida, o que você recomenda?",
        user_id=user_id,
        session_id="session_2"  # Nova sessão!
    )
    
    # O assistente deve lembrar da alergia e sugerir opções seguras
    print(result2["response"])
    # Saída esperada: "Olá Carlos! Considerando sua alergia a amendoim, 
    # recomendo..."
```
