# Análise crítica: fallback 429 x pergunta sobre arquivo

**Caso:** Usuário pede "Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas."  
**Resposta do bot (API indisponível):** "Com base na memória (API temporariamente indisponível):" + lista de fatos sobre Bruno (FactStore).

---

## 1. O que está errado

| Aspecto | Esperado | O que aconteceu |
|--------|----------|------------------|
| **Intenção** | Resumo do **conteúdo do arquivo** MEMORY.md (estrutura, blocos, ~10 linhas). | Resposta sobre **o que o bot tem na memória sobre o usuário** (FactStore). |
| **Fonte** | Conteúdo lido via tool `read_file` + possível resumo por LLM. | Fatos armazenados (Bruno, preferências, uso do bot). |
| **Semântica** | "Memória" = documento MEMORY.md. | "Memória" = memória do agente (FactStore). |

A frase "Com base na memória (API temporariamente indisponível)" é ambígua: o usuário pode achar que é um resumo do MEMORY.md, quando na verdade é uma listagem genérica de fatos sobre ele. **Resposta semanticamente incorreta e enganosa.**

---

## 2. Por que acontece

Em 429 o fluxo é:

1. Tentar Kimi (se houver chave).
2. Tentar RAG de documentos (ex.: NR-29); MEMORY.md pode não estar indexado ou a busca não retorna esse doc.
3. Tentar FactStore com a mensagem do usuário; "leia MEMORY.md" não dá match com fatos sobre Bruno.
4. **Último recurso:** devolver fatos recentes (qualquer um) para "não deixar só a mensagem de limite".

O passo 4 não considera a **intenção** da pergunta. Para pedidos explícitos de **ler/resumir arquivo**, devolver FactStore é irrelevante e piora a experiência.

---

## 3. Correção necessária

- **Regra:** Se a pergunta for claramente sobre **ler, resumir ou analisar um arquivo específico**, o fallback em 429 **não** deve devolver FactStore nem fatos recentes como se fossem a resposta.
- **Ação:** Devolver apenas a mensagem de rate limit e deixar explícito que perguntas que exigem leitura de arquivo não podem ser atendidas enquanto a API estiver indisponível.

Implementação: detectar padrões como "leia o arquivo", "conteúdo do arquivo", "resuma o arquivo", "MEMORY.md", etc. e, nesses casos, pular o fallback de memória (FactStore / fatos recentes) e retornar a mensagem de limite com essa ressalva.
