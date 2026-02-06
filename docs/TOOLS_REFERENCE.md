# 🛠️ Tools Reference - Assistente Digital

Referência completa de todas as 14 ferramentas disponíveis no Assistente Digital.

## Índice

1. [Web & Search](#web--search)
2. [Memória (RAG)](#memória-rag)
3. [Filesystem](#filesystem)
4. [Code & Git](#code--git)
5. [Extras](#extras)

---

## Web & Search

### web_search

**Descrição:** Busca informações na web usando DuckDuckGo.

**Parâmetros:**
- `query` (string, obrigatório) - Termo ou pergunta para buscar
- `max_results` (integer, opcional) - Número máximo de resultados (padrão: 5)

**Retorno:**
```json
{
  "success": true,
  "results": [
    {
      "title": "Título do resultado",
      "url": "https://...",
      "snippet": "Trecho do conteúdo..."
    }
  ]
}
```

**Exemplo:**
```python
result = await web_search("Python 3.12 features", max_results=3)
```

---

## Memória (RAG)

A memória fica em `src/dados/memory.json` (config.DATA_DIR). Pode ser alimentada por scripts (ex.: `scripts/feed_nr29_to_memory.py`, `scripts/feed_nr29_oficial.py`). Em rate limit (429) da API, o agente usa esta memória para responder quando a pergunta menciona NR/normas.

### rag_search

**Descrição:** Busca informações na memória pessoal de longo prazo.

**Parâmetros:**
- `query` (string, obrigatório) - O que buscar na memória

**Retorno:**
```json
{
  "success": true,
  "results": "Informações encontradas na memória..."
}
```

**Exemplo:**
```python
result = await rag_search("aniversário do Bruno")
```

---

### save_memory

**Descrição:** Salva informação importante na memória de longo prazo.

**Parâmetros:**
- `content` (string, obrigatório) - Conteúdo a salvar
- `category` (string, opcional) - Categoria da informação

**Retorno:**
```json
{
  "success": true,
  "message": "Informação salva na memória"
}
```

**Exemplo:**
```python
result = await save_memory("Aniversário do Bruno é dia 15 de março", "pessoal")
```

---

## Filesystem

### read_file

**Descrição:** Lê conteúdo de um arquivo.

**Parâmetros:**
- `path` (string, obrigatório) - Caminho do arquivo

**Retorno:**
```json
{
  "success": true,
  "content": "Conteúdo do arquivo...",
  "path": "/caminho/completo/arquivo.txt"
}
```

**Exemplo:**
```python
result = await read_file("~/documentos/notas.txt")
```

---

### write_file

**Descrição:** Escreve conteúdo em um arquivo.

**Parâmetros:**
- `path` (string, obrigatório) - Caminho do arquivo
- `content` (string, obrigatório) - Conteúdo a escrever

**Retorno:**
```json
{
  "success": true,
  "message": "Arquivo salvo em /caminho/arquivo.txt"
}
```

**Exemplo:**
```python
result = await write_file("teste.txt", "Hello World")
```

---

### list_directory

**Descrição:** Lista arquivos e diretórios.

**Parâmetros:**
- `path` (string, obrigatório) - Caminho do diretório

**Retorno:**
```json
{
  "success": true,
  "path": "/caminho/diretorio",
  "files": ["arquivo1.txt", "arquivo2.py"],
  "directories": ["subdir1", "subdir2"],
  "total": 4
}
```

**Exemplo:**
```python
result = await list_directory("~/projetos")
```

---

## Code & Git

### search_code

**Descrição:** Busca termo em arquivos de código.

**Parâmetros:**
- `query` (string, obrigatório) - Termo a buscar
- `path` (string, opcional) - Diretório base do projeto (padrão: diretório oficial do bot)
- `extensions` (array, opcional) - Extensões de arquivo (padrão: [".py", ".js", ".ts"])

**Retorno:**
```json
{
  "success": true,
  "results": "arquivo.py:10: def funcao()...",
  "matches": 5
}
```

**Exemplo:**
```python
result = await search_code("async def", path="~/projeto", extensions=[".py"])
```

---

### git_status

**Descrição:** Mostra status do repositório Git.

**Parâmetros:**
- `repo_path` (string, opcional) - Caminho do repositório (padrão: diretório oficial do bot)

**Retorno:**
```json
{
  "success": true,
  "status": "On branch main\nChanges not staged..."
}
```

**Exemplo:**
```python
result = await git_status("~/meu-projeto")
```

---

### git_diff

**Descrição:** Mostra diferenças não commitadas.

**Parâmetros:**
- `repo_path` (string, opcional) - Caminho do repositório (padrão: ~/clawd)

**Retorno:**
```json
{
  "success": true,
  "diff": "diff --git a/file.py..."
}
```

**Exemplo:**
```python
result = await git_diff()
```

---

## Extras

### get_weather

**Descrição:** Obtém clima atual de uma cidade.

**Parâmetros:**
- `city` (string, obrigatório) - Nome da cidade

**Retorno:**
```json
{
  "success": true,
  "weather": {
    "cidade": "São Paulo",
    "temperatura": "25°C",
    "sensacao": "26°C",
    "descricao": "céu limpo",
    "umidade": "60%",
    "vento": "3.5 m/s"
  }
}
```

**Exemplo:**
```python
result = await get_weather("Rio de Janeiro")
```

**Requer:** `OPENWEATHER_API_KEY` no `.env`

---

### get_news

**Descrição:** Obtém últimas notícias sobre um tópico.

**Parâmetros:**
- `topic` (string, opcional) - Tópico (padrão: "brasil")
- `limit` (integer, opcional) - Número de notícias (padrão: 5)

**Retorno:**
```json
{
  "success": true,
  "articles": [
    {
      "titulo": "Título da notícia",
      "fonte": "Nome da fonte",
      "url": "https://...",
      "data": "2026-01-31"
    }
  ]
}
```

**Exemplo:**
```python
result = await get_news("tecnologia", limit=3)
```

**Requer:** `NEWS_API_KEY` no `.env`

---

### create_reminder

**Descrição:** Cria um lembrete com notificação por Email e Telegram.

**Parâmetros:**
- `text` (string, obrigatório) - Texto do lembrete
- `datetime_str` (string, obrigatório) - Data/hora (formatos: "DD/MM/YYYY HH:MM", "YYYY-MM-DD HH:MM")

**Retorno:**
```json
{
  "success": true,
  "message": "Lembrete criado para 31/01/2026 15:00"
}
```

**Exemplo:**
```python
result = await create_reminder("Reunião importante", "31/01/2026 15:00")
```

**Requer:** Configuração de Email no `.env`

---

### create_chart

**Descrição:** Gera gráfico com matplotlib.

**Parâmetros:**
- `chart_type` (string, obrigatório) - Tipo: "bar", "line", "pie", "scatter"
- `data` (object, obrigatório) - Dados do gráfico
- `title` (string, opcional) - Título do gráfico
- `xlabel` (string, opcional) - Label do eixo X
- `ylabel` (string, opcional) - Label do eixo Y

**Retorno:**
```json
{
  "success": true,
  "image_path": "/tmp/chart_12345.png"
}
```

**Exemplo:**
```python
result = await create_chart(
    chart_type="bar",
    data={"Jan": 100, "Fev": 150, "Mar": 120},
    title="Vendas Mensais"
)
```

---

### generate_image

**Descrição:** Gera imagem usando IA (se configurado).

**Parâmetros:**
- `prompt` (string, obrigatório) - Descrição da imagem
- `size` (string, opcional) - Tamanho (padrão: "1024x1024")

**Retorno:**
```json
{
  "success": true,
  "image_url": "https://..."
}
```

**Exemplo:**
```python
result = await generate_image("gato astronauta no espaço")
```

**Nota:** Requer configuração de serviço de geração de imagens.

---

## Schemas para Tool Calling

Cada ferramenta tem um schema JSON que define sua interface para o LLM:

```python
WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Busca informações na web usando DuckDuckGo",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo ou pergunta para buscar"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de resultados",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}
```

---

## Adicionar Nova Ferramenta

### 1. Criar a Função

```python
# workspace/tools/minha_ferramenta.py

async def minha_ferramenta(parametro: str) -> dict:
    """Descrição da ferramenta"""
    try:
        # Lógica da ferramenta
        resultado = fazer_algo(parametro)
        return {"success": True, "resultado": resultado}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Definir o Schema

```python
MINHA_FERRAMENTA_SCHEMA = {
    "type": "function",
    "function": {
        "name": "minha_ferramenta",
        "description": "O que esta ferramenta faz",
        "parameters": {
            "type": "object",
            "properties": {
                "parametro": {
                    "type": "string",
                    "description": "Descrição do parâmetro"
                }
            },
            "required": ["parametro"]
        }
    }
}
```

### 3. Registrar no Bot

```python
# bot_simple.py

from workspace.tools.minha_ferramenta import minha_ferramenta, MINHA_FERRAMENTA_SCHEMA

def create_agent_no_sandbox():
    registry = ToolRegistry()
    # ... outras ferramentas
    registry.register("minha_ferramenta", minha_ferramenta, MINHA_FERRAMENTA_SCHEMA)
    return Agent(registry)
```

### 4. Testar

```
Você: Use minha_ferramenta com parametro="teste"
Bot: [executa ferramenta e retorna resultado]
```

---

## Boas Práticas

### 1. Sempre Retornar Dict
```python
# ✅ Correto
return {"success": True, "data": resultado}

# ❌ Errado
return resultado
```

### 2. Tratamento de Erros
```python
try:
    resultado = operacao_perigosa()
    return {"success": True, "resultado": resultado}
except Exception as e:
    logger.error(f"Erro: {e}")
    return {"success": False, "error": str(e)}
```

### 3. Validação de Parâmetros
```python
if not parametro or len(parametro) == 0:
    return {"success": False, "error": "Parâmetro inválido"}
```

### 4. Timeouts
```python
result = subprocess.run(cmd, timeout=30, capture_output=True)
```

### 5. Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Executando ferramenta com {parametro}")
logger.error(f"Erro ao executar: {e}")
```

---

## Limitações (estado atual)

### Filesystem
- Operações via ferramentas usam a infraestrutura atual de segurança (ex.: `SecureFileManager`, sanitização de paths, limites de tamanho).  
- Ainda assim, as ferramentas são pensadas para **uso pessoal/local**, não para multi‑tenant nem acesso arbitrário de terceiros.

### Code Tools
- Busca baseada em grep (sem análise semântica).
- Limitado a extensões específicas configuradas na ferramenta.

### Web Search
- Máximo 5 resultados por busca.
- Sem cache de resultados.
- Dependente de DuckDuckGo (pode variar por região).

### RAG
- Implementação focada em uso pessoal (memória em `memory.json`).
- Sem embeddings locais avançados; estratégia simples de busca/texto.

---

## 🔧 Ferramentas de Segurança Internas (v1.1)

Além das 15 ferramentas acima, o sistema inclui módulos de segurança para uso interno no desenvolvimento:

### SecureFileManager

**Uso:** Gerenciamento seguro de arquivos temporários.

```python
from security import secure_files

async with secure_files.temp_file(suffix='.mp4') as path:
    # Arquivo criado em diretório seguro
    await process_file(path)
    # Auto-deletado ao sair do contexto
```

**Extensões Permitidas:** mp4, mp3, jpg, png, xlsx, csv, docx, etc.

---

### SafeSubprocessExecutor

**Uso:** Execução segura de comandos externos.

```python
from security import SafeSubprocessExecutor

success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(input), str(output)
])
```

**Comandos Permitidos:** ffmpeg, ffprobe, tesseract, python

---

### Retry Decorator

**Uso:** Resiliência em chamadas de API.

```python
from utils import retry_with_backoff

@retry_with_backoff(max_retries=3)
async def call_api():
    return await api.request()
```

---

### Config

**Uso:** Acesso centralizado a configurações.

```python
from config import config

path = config.TEMP_DIR / "arquivo.txt"
model = config.GROQ_MODEL_VISION
```

**Documentação detalhada:** Ver `API_REFERENCE.md` → "APIs Internas"

---

## Melhorias Futuras

- [ ] Validação de paths no filesystem
- [ ] Cache de resultados de web search
- [ ] RAG com embeddings locais
- [ ] Ferramentas de banco de dados
- [ ] Integração com APIs de terceiros
- [ ] Ferramentas de automação de navegador
- [ ] Análise de código com AST
- [ ] Geração de código

---

## Referências

- `ARCHITECTURE.md` - Arquitetura do sistema
- `DEVELOPMENT.md` - Guia de desenvolvimento
- `API_REFERENCE.md` - Referência de APIs
