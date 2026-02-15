# Investigação: resumo de MEMORY.md retornava blocos incorretos

## Problema

**Entrada:** "Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas."

**Saída observada:** Lista genérica (Memoria Pessoal, Dados Pessoais, Preferencias, etc.) em vez dos blocos reais do MEMORY.md (Informações Essenciais, Arquitetura do Sistema, Decisões Arquiteturais, etc.).

## Causa raiz

1. O modelo recebia o conteúdo completo do arquivo via tool `read_file`, mas o MEMORY.md é longo (milhares de linhas). O início do contexto do agente fala de "memória pessoal" e "preferências" (IDENTITY/CONTEXT_PACK), o que levava o modelo a priorizar esse esquema e ignorar o texto da tool.
2. Não havia regra explícita obrigando a resposta a ser baseada apenas no retorno da ferramenta e nos títulos reais (##/###) do documento.
3. Para arquivos muito longos, o resultado da tool era enviado inteiro, sem destacar a estrutura (títulos) para o modelo.

## Soluções implementadas

### 1. Regra de política e estilo (POLICIES.md + STYLE.md)

- **POLICIES.md:** Regra 57: ao resumir ou listar blocos de um arquivo, usar exclusivamente o conteúdo retornado por `read_file` e citar os títulos reais (## ou ###); nunca inventar seções que não constem do arquivo.
- **STYLE.md:** Seção "Resumo de arquivos" com a mesma orientação, para entrar no CONTEXT_PACK (Estilo).
- **CONTEXT_PACK.md:** Regenerado para incluir a nova seção de estilo.

### 2. Enriquecimento do resultado de read_file (agent.py)

- Para `read_file` com conteúdo maior que 10.000 caracteres, o resultado enviado ao modelo passou a incluir:
  - **structure:** lista de linhas com `##` e `###` extraídas do markdown (`_extract_markdown_headings`).
  - **content:** truncado em 14.000 caracteres + aviso de truncamento.
- Assim o modelo vê primeiro a estrutura real do documento e depois o trecho inicial do conteúdo, reduzindo invenção de seções.

### 3. Testes

- `test_extract_file_path`: garante extração segura de path a partir da mensagem.
- `test_extract_markdown_headings`: garante extração apenas de linhas `##` e `###`.

## Como validar

1. Enviar no Telegram: "Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas."
2. A resposta deve listar blocos que existem no arquivo (ex.: Informações Essenciais, Arquitetura do Sistema, Decisões Arquiteturais, Gerenciamento de Instâncias, etc.), não "Dados Pessoais" ou "Preferencias" genéricos.
3. Nos logs, para arquivos grandes deve aparecer o resultado de `read_file` com o campo `structure` no JSON enviado ao modelo.

## Arquivos alterados

- `src/workspace/agent/POLICIES.md` – regra 57
- `src/workspace/agent/STYLE.md` – seção "Resumo de arquivos"
- `src/workspace/agent/CONTEXT_PACK.md` – regenerado
- `src/workspace/core/agent.py` – `_extract_markdown_headings`, enriquecimento do resultado de `read_file`, uso de `structure` + truncamento
- `tests/test_fixes_bot.py` – testes para `_extract_file_path` e `_extract_markdown_headings`
