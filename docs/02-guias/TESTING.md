# 🧪 Guia de Testes - Assistente Digital

**Documentação completa dos testes e validações do sistema**

**Execução dos testes:** na raiz do repositório, use `PYTHONPATH=src` para que os imports encontrem os módulos em `src/`:

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Testes Via Terminal** | 7/7 ✅ (100%) |
| **Testes E2E** | 28/28 ✅ (100%) |
| **Funcionalidades Testadas** | 15/15 ✅ |
| **Cobertura Core** | 100% |
| **Última Execução** | 2026-01-31 |

---

## 🎯 Tipos de Testes

### 1. Testes Via Terminal (Funcionalidades Core)

Testes que podem ser executados independentemente do bot Telegram, validando as ferramentas individualmente.

**Arquivos:**
- `tests/test_bot_completo.py` - **7 funcionalidades** (recomendado)
- `tests/test_bot_simples.py` - **4 funcionalidades** (core)
- `tests/test_bot_funcionalidades.py` - **11 funcionalidades** (completo)

#### Resultados do Último Teste (2026-01-31)

```
✅ PASSOU - 1. Web Search (DuckDuckGo)
✅ PASSOU - 2. RAG Search (Memória)
✅ PASSOU - 3. Save Memory
✅ PASSOU - 4. Search Code
✅ PASSOU - 5. Filesystem (R/W/List)
✅ PASSOU - 6. Git (Status/Diff)
✅ PASSOU - 7. Tool Registry

Total: 7/7 testes passaram (100%)
```

#### Como Executar

```bash
# Na raiz do repositório assistente/
source venv/bin/activate   # ou venv311

# Teste completo (7 funcionalidades)
PYTHONPATH=src python tests/test_bot_completo.py

# Teste simplificado (4 funcionalidades)
PYTHONPATH=src python tests/test_bot_simples.py
```

#### Funcionalidades Testadas

| # | Funcionalidade | Arquivo | Evidência do Último Teste |
|---|---------------|---------|---------------------------|
| 1 | **Web Search** | `src/workspace/tools/web_search.py` | Busca DuckDuckGo executada |
| 2 | **RAG Search** | `src/workspace/tools/rag_tools.py` | Encontrou entradas na memória |
| 3 | **Save Memory** | `src/workspace/tools/rag_tools.py` | Salvou informação de teste |
| 4 | **Search Code** | `src/workspace/tools/code_tools.py` | 88 matches de "async def" |
| 5 | **Read File** | `src/workspace/tools/filesystem.py` | Leitura OK |
| 6 | **Write File** | `src/workspace/tools/filesystem.py` | Escrita OK |
| 7 | **List Directory** | `src/workspace/tools/filesystem.py` | 26 arquivos, 17 dirs |
| 8 | **Git Status** | `src/workspace/tools/code_tools.py` | Status do repo OK |
| 9 | **Git Diff** | `src/workspace/tools/code_tools.py` | Diff operacional |
| 10 | **Tool Registry** | `src/workspace/core/tools.py` | 8 ferramentas registradas |

---

### 2. Testes E2E (End-to-End)

Testes de integração completa validando o sistema como um todo.

**Arquivos:**
- `tests/test_e2e.py` - Testes E2E completos (28 testes)
- `tests/test_e2e_simple.py` - Testes E2E simplificados

#### Resultados

- ✅ **28/28 testes passando (100%)**
- ✅ Validação de APIs (Groq + Telegram)
- ✅ Testes de Tool Registry
- ✅ Testes de SQLite Store
- ✅ Testes de Filesystem

#### Como Executar

```bash
# Na raiz do repositório
source venv/bin/activate

# Testes E2E com pytest (recomendado)
PYTHONPATH=src python -m pytest tests/test_e2e_simple.py tests/test_e2e.py -v

# Apenas E2E simplificado
PYTHONPATH=src python -m pytest tests/test_e2e_simple.py -v
```

---

## 📁 Estrutura de Testes

```
tests/
├── test_bot_completo.py         # 7 funcionalidades testadas ✅
├── test_bot_simples.py          # 4 funcionalidades core
├── test_bot_funcionalidades.py  # 11 funcionalidades (com dependências)
├── test_e2e.py                  # 28 testes E2E completos
├── test_e2e_simple.py           # Testes E2E simplificados
└── test_security.py             # Sanitização, paths, rate limiter, executor
```

---

## 🔧 Detalhes dos Testes

### Test 1: Web Search (DuckDuckGo)

**Objetivo:** Validar busca na web via DuckDuckGo

**Comando Testado:**
```python
result = await web_search("Python 3.12 features", max_results=3)
```

**Resultado Esperado:**
- ✅ Sucesso na execução
- ✅ Retorno de resultados
- ✅ Estrutura JSON válida

**Status:** ✅ PASSOU

---

### Test 2: RAG Search (Memória)

**Objetivo:** Validar busca na memória pessoal

**Comando Testado:**
```python
result = await rag_search("projeto")
```

**Resultado Esperado:**
- ✅ Sucesso na execução
- ✅ Retorna entradas da memória
- ✅ Formato consistente

**Status:** ✅ PASSOU

---

### Test 3: Save Memory

**Objetivo:** Validar salvamento na memória

**Comando Testado:**
```python
result = await save_memory("Teste automatizado", category="test")
```

**Resultado Esperado:**
- ✅ Sucesso na execução
- ✅ Mensagem de confirmação
- ✅ Dados persistidos

**Status:** ✅ PASSOU

---

### Test 4: Search Code

**Objetivo:** Validar busca em código

**Comando Testado:**
```python
result = await search_code("async def", path="/path", extensions=[".py"])
```

**Resultado Esperado:**
- ✅ Sucesso na execução
- ✅ Encontrar matches
- ✅ Total de matches > 0

**Evidência:** 88 matches encontrados de "async def"

**Status:** ✅ PASSOU

---

### Test 5: Filesystem (R/W/List)

**Objetivo:** Validar operações de arquivo

**Comandos Testados:**
```python
write_result = await write_file("/tmp/test.txt", "conteúdo")
read_result = await read_file("/tmp/test.txt")
list_result = await list_directory("/tmp")
```

**Resultados Esperados:**
- ✅ Escrita bem-sucedida
- ✅ Leitura retorna conteúdo correto
- ✅ Listagem mostra arquivos e diretórios

**Evidência:**
- 26 arquivos em /tmp
- 17 diretórios em /tmp
- Conteúdo lido corretamente (119 chars)

**Status:** ✅ PASSOU

---

### Test 6: Git (Status/Diff)

**Objetivo:** Validar integração com Git

**Comandos Testados:**
```python
status_result = await git_status("/path/to/repo")
diff_result = await git_diff("/path/to/repo")
```

**Resultados Esperados:**
- ✅ Status do repositório
- ✅ Diff de alterações
- ✅ Informações de branch

**Evidência:**
- Branch: main
- Status: up to date with origin/main
- Diff: 121870 caracteres de alterações não commitadas

**Status:** ✅ PASSOU

---

### Test 7: Tool Registry

**Objetivo:** Validar sistema de registro de ferramentas

**Comandos Testados:**
```python
registry = ToolRegistry()
registry.register("tool_name", function, schema)
tools = registry.list_tools()
schemas = registry.get_schemas()
result = await registry.execute("tool_name", args)
```

**Resultados Esperados:**
- ✅ Registro de ferramentas
- ✅ Listagem de ferramentas
- ✅ Execução via registry
- ✅ Schemas disponíveis

**Evidência:**
- 8 ferramentas registradas
- Execução via registry funcionando
- Todos os schemas disponíveis

**Ferramentas Registradas:**
- git_status
- list_directory
- rag_search
- read_file
- save_memory
- search_code
- web_search
- write_file

**Status:** ✅ PASSOU

---

## Segfault em alguns ambientes

Em alguns ambientes (ex.: WSL2, certas versões de Python/venv), a execução de testes que importam módulos com `logging` e asyncio pode causar **segfault**. O contorno aplicado foi remover o `logging.warning()` na importação de `src/security/file_manager.py`. Para mais detalhes, causas e alternativas, veja a seção **"Notas sobre Testes"** em `MEMORY.md`.

**Sugestão:** usar venv dedicado; rodar apenas testes síncronos se o segfault persistir; validar E2E em outro ambiente se necessário.

---

## 🚨 Troubleshooting de Testes

### Erro: "No module named X"

**Causa:** `PYTHONPATH` não configurado ou ambiente virtual não ativado.

**Solução:**
```bash
source venv/bin/activate
PYTHONPATH=src python -m pytest tests/ -v
```

---

### Erro: "ImportError: ... undefined symbol"

**Causa:** Conflito de bibliotecas no sistema

**Solução:** Use sempre o venv do projeto para executar testes

---

### Erro: Web Search / RAG retorna erro

**Causa:** Scripts externos não encontrados

**Detalhe:** Estas ferramentas dependem de scripts em `~/.clawdbot/skills/`

**Solução:** Verificar se os scripts estão instalados

---

## 📝 Notas Importantes

1. **Ambiente:** Sempre execute testes dentro do venv do projeto
2. **PYTHONPATH:** Use `PYTHONPATH=src` na raiz do repositório (código em `src/`)
3. **Dependências:** Alguns testes requerem API keys configuradas (.env)
4. **Limpeza:** Testes de filesystem usam `config.TEMP_DIR` e limpam automaticamente

---

## 📊 Histórico de Testes

| Data | Teste | Resultado | Observações |
|------|-------|-----------|-------------|
| 2026-01-31 | Via Terminal (7 func) | 7/7 ✅ | Primeira execução completa |
| 2026-01-31 | E2E | 28/28 ✅ | Testes originais |
| 2026-01-31 | Tool Registry | 8/8 ✅ | Todas ferramentas OK |

---

## 🔗 Links Relacionados

- [MEMORY.md](../MEMORY.md) - Contexto completo (inclui notas sobre segfault em testes)
- [FEATURES.md](FEATURES.md) - Funcionalidades
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura
- [DOCS_INDEX.md](DOCS_INDEX.md) - Índice de docs

---

**Atualizado em:** 2026-02-05
**Versão:** 1.2
**Status:** Documentação alinhada com estrutura `src/` e comando `PYTHONPATH=src pytest`
