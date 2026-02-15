# 🧠 Plano de Implementação: HippocampAI (Versão Lite/KISS)

Este plano descreve como implementar o sistema de memória **HippocampAI** no projeto, respeitando as restrições de arquitetura (KISS, Features-based) e infraestrutura (Docker simples).

## 🎯 Objetivo
Transformar o bot em um agente com **memória de longo prazo real**, capaz de lembrar fatos, preferências e histórico complexo, usando uma arquitetura híbrida (Vetores + Grafo) porém leve (sem novos containers pesados).

---

## 🛠️ Stack Tecnológica (Lite Version)
Para manter o princípio **KISS** e evitar complexidade de infraestrutura (Qdrant/Redis exigem muita RAM), usaremos:

1.  **Vector Store:** `ChromaDB` (Embarcado)
    *   *Por que?* Roda no mesmo processo Python, persistência em arquivo, sem necessidade de container extra.
2.  **Graph Store:** `NetworkX` + `JSON/Pickle`
    *   *Por que?* Suficiente para grafos de conhecimento pessoais (< 10k nós).
3.  **Cache:** `LRU Cache` (In-memory) + `SQLite`
    *   *Por que?* Redis é overkill para um único usuário.
4.  **LLM:** `Groq` (Llama 3.3/4)
    *   *Por que?* Já integrado e rápido.

---

## 📅 Roteiro de Implementação

### Fase 1: Estrutura & Dependências (Dia 1)
O foco é preparar o terreno sem quebrar o bot atual.

1.  **Criar Feature Module:**
    *   `src/features/hippocampus/` (Respeitando regra: "Todo código novo em src/features/")
    *   `src/features/hippocampus/client.py` (Lógica principal)
    *   `src/features/hippocampus/graph.py` (Gerenciador do Grafo)
    *   `src/features/hippocampus/types.py` (Data models)

2.  **Atualizar Dependências:**
    *   Adicionar `chromadb`, `networkx` ao `requirements.txt`.
    *   Rebuild do Docker.

### Fase 2: O Motor Hippocampus (Dia 2)
Implementar a lógica de armazenamento e recuperação híbrida.

1.  **Implementar `HippocampusClient`:**
    *   **Ingestão (`remember`):**
        *   Recebe texto -> Gera Embedding (via OpenAI ou Llama/Groq se possível, ou `sentence-transformers` local).
        *   Extrai Triplas (Sujeito-Verbo-Objeto) via LLM.
        *   Salva Vetor no ChromaDB.
        *   Atualiza Grafo NetworkX.
    *   **Recuperação (`recall`):**
        *   Busca Vetorial (ChromaDB).
        *   Busca no Grafo (PageRank simplificado).
        *   Reranking (RRF Fusion).

2.  **Camada de Persistência:**
    *   Garantir que o Grafo seja salvo em `dados/hippocampus_graph.json` a cada atualização.
    *   ChromaDB persistindo em `dados/chroma_db`.

### Fase 3: Integração com o Agente (Dia 3)
Conectar o "cérebro" ao "corpo" do bot.

1.  **Modificar `src/bot_simple.py`:**
    *   Inicializar `HippocampusClient` no startup.
    *   Injetar cliente no contexto do `Agent`.

2.  **Hook de Memória no `Agent`:**
    *   **Antes de responder:** `hippocampus.recall(query)` -> Adicionar contexto ao System Prompt.
    *   **Depois de responder:** `hippocampus.remember(interaction)` (Async).

3.  **Extração de Fatos em Background:**
    *   Criar task que roda após cada conversa para extrair fatos importantes ("O usuário disse que gosta de X") e salvar como Memória Semântica.

### Fase 4: Consolidação ("Sleep Phase") (Dia 4)
Manutenção da memória.

1.  **Script de Consolidação (`scripts/consolidate_memory.py`):**
    *   Lê memórias recentes.
    *   Remove redundâncias.
    *   Aplica decaimento temporal (esquece detalhes irrelevantes).
    *   Executar via Cron ou comando `/consolidar`.

---

## 📂 Estrutura de Diretórios Proposta

```bash
src/
  features/
    hippocampus/
      __init__.py
      client.py       # Fachada principal
      vector_store.py # Wrapper ChromaDB
      graph_store.py  # Wrapper NetworkX
      models.py       # Pydantic models (Memory, Triple)
      prompts.py      # Prompts para extração de fatos/triplas
```

## ⚠️ Pontos de Atenção
*   **Embeddings:** Usar `sentence-transformers` (local, CPU) pode ser lento no Docker se não tiver cuidado. Alternativa: Usar API da OpenAI (paga) ou Groq (se suportar embeddings, ainda limitado). *Recomendação: `all-MiniLM-L6-v2` (rápido e leve).*
*   **Tokens:** Extrair triplas consome tokens do LLM. Usar modelos menores (Llama 3.3 8B ou até Gemma 2B local se possível) para essa tarefa auxiliar.

## 🚀 Próximos Passos
1.  Aprovar este plano.
2.  Criar branch `feature/hippocampus`.
3.  Instalar dependências.
