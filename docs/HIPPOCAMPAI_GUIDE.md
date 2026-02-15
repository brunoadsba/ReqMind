# 🧠 HippocampAI Lite: Sistema de Memória de Longo Prazo

O **HippocampAI Lite** é uma implementação simplificada e eficiente do conceito de memória hipocampal para o assistente, focado na arquitetura **KISS** (Keep It Simple, Stupid) e **Serverless-ready** (sem containers de banco de dados pesados).

---

## 🏗️ Arquitetura

Diferente de sistemas RAG tradicionais que dependem apenas de busca vetorial, o HippocampAI usa uma abordagem híbrida:

1.  **Memória Episódica (Vector Store - ChromaDB):** Armazena o "que" e o "quando". Logs de conversas e eventos brutos.
2.  **Memória Semântica (Graph Store - NetworkX):** Armazena o "quem" e "como". Entidades e seus relacionamentos (triplas sujeito-verbo-objeto).
3.  **Memória de Curto Prazo (Cache):** LRU Cache em memória para acesso instantâneo a fatos recentes.

### Componentes

| Componente | Tecnologia | Função | Persistência |
|:---|:---|:---|:---|
| **Vector Store** | `chromadb` (Embedded) | Busca por similaridade semântica | `dados/chroma_db/` |
| **Graph Store** | `networkx` | Relações entre entidades (PageRank) | `dados/knowledge_graph.json` |
| **Embeddings** | `sentence-transformers` | Vetorização de texto (CPU-friendly) | Local (cache) |
| **Manager** | `MemoryManager` | Orquestração e decisão de retenção | Código Python |

---

## 🚀 Funcionalidades Implementadas (v1.4)

### 1. Ingestão de Memória (`remember`)
Quando o assistente interage:
1.  **Captura:** O texto do usuário e a resposta são capturados.
2.  **Vetorização:** O conteúdo é transformado em vetor (embedding).
3.  **Armazenamento:** Salvo no ChromaDB com metadados (timestamp, user_id, tipo).
4.  **Grafo (Futuro):** Extração de entidades (ex: "Bruno" -> "gosta de" -> "Python") e atualização do grafo.

### 2. Recuperação de Memória (`recall`)
Antes de responder ao usuário:
1.  **Busca Vetorial:** Encontra interações passadas semanticamente similares.
2.  **Busca no Grafo:** (Em desenvolvimento) Identifica entidades conectadas para contexto profundo.
3.  **Context Injection:** Os fatos relevantes são injetados no System Prompt do LLM.

### 3. Integração Transparente
O sistema roda dentro do processo do bot (`src/features/hippocampus`), sem necessidade de serviços externos (como Redis ou Qdrant), ideal para deployment em container único ou VPS modesta.

---

## 📂 Estrutura de Dados

### Memory Object
```json
{
  "id": "uuid-v4",
  "content": "O usuário prefere respostas concisas.",
  "type": "semantic",
  "timestamp": "2026-02-15T10:00:00",
  "embedding": [...],
  "metadata": {
    "source": "interaction",
    "confidence": 0.9
  }
}
```

### Knowledge Graph (Triplas)
```json
[
  {"subject": "Bruno", "predicate": "trabalha_com", "object": "Automação"},
  {"subject": "Projeto", "predicate": "usa", "object": "Docker"}
]
```

---

## 🛠️ Como Usar

O sistema é automático, mas pode ser acessado via código:

```python
from features.hippocampus import HippocampusClient, MemoryType

client = HippocampusClient("dados/hippocampus")

# Lembrar
client.remember(
    content="O usuário é desenvolvedor Python.",
    user_id="user_123",
    memory_type=MemoryType.SEMANTIC
)

# Lembrar
context = client.recall("O que você sabe sobre mim?", user_id="user_123")
print(context)
# > "[SEMANTIC] O usuário é desenvolvedor Python."
```

---

## 🔮 Roadmap (Próximos Passos)

1.  **Extração Automática de Triplas:** Usar LLM (Groq/Llama) em background para converter texto livre em triplas para o grafo.
2.  **Consolidação de Memória (Sono):** Script noturno para limpar memórias irrelevantes e fundir fatos repetidos.
3.  **Interface de Visualização:** Gerar gráfico visual das conexões de memória do usuário.
