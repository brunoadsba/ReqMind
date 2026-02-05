# 🏗️ Arquitetura do Assistente Digital

## Visão Geral

O Assistente Digital é um bot Telegram avançado construído com arquitetura modular, utilizando agentes autônomos com tool calling para executar tarefas complexas.

**Estrutura do repositório:** o código-fonte está em `src/` (ex.: `src/bot_simple.py`, `src/workspace/`, `src/security/`). A execução deve usar `PYTHONPATH=src` quando iniciada na raiz do projeto.

```
┌─────────────────────────────────────────────────────────────┐
│                      TELEGRAM BOT API                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT_SIMPLE.PY (Main)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Handlers:                                           │   │
│  │  • handle_message  → Texto                           │   │
│  │  • handle_photo    → Imagens                         │   │
│  │  • handle_video    → Vídeos                          │   │
│  │  • handle_voice    → Áudio de voz                    │   │
│  │  • handle_audio    → Arquivos de áudio               │   │
│  │  • handle_document → Documentos (Excel, Word, etc)   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYER (v1.1)                     │
│  • @require_auth         → Autenticação                      │
│  • rate_limiter          → Controle de taxa                  │
│  • media_validator       → Validação de mídia                │
│  • sanitizer             → Sanitização de inputs             │
│  • secure_files          → Arquivos temporários seguros      │
│  • SafeSubprocessExecutor → Execução segura de comandos      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT (Core)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Groq Llama 3.3 70B (versatile)                      │   │
│  │  • Tool calling automático                           │   │
│  │  • Iterações até 5x                                  │   │
│  │  • Fallback sem tools                                │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TOOL REGISTRY (15 Tools)                    │
│                                                               │
│  🌐 Web & Search          📁 Filesystem                       │
│  • web_search             • read_file                         │
│  • rag_search             • write_file                        │
│  • save_memory            • list_directory                    │
│                                                               │
│  💻 Code & Git            📊 Extras                           │
│  • search_code            • get_weather                       │
│  • git_status             • get_news                          │
│  • git_diff               • create_reminder                   │
│                           • create_chart                      │
│                           • generate_image                    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                           │
│                                                               │
│  🤖 AI Models             📧 Notifications                    │
│  • Groq (Chat/Vision)     • Email (SMTP)                      │
│  • ElevenLabs (TTS)       • Telegram                          │
│                                                               │
│  🔧 Tools                 💾 Storage                          │
│  • ffmpeg                 • SQLite (histórico)                │
│  • yt-dlp                 • JSON (lembretes)                  │
│  • tesseract (OCR)        • Filesystem                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Principais

### 1. Bot Principal (`src/bot_simple.py`) - Modularizado

**Responsabilidades:**
- Setup e inicialização do bot
- Registro de handlers e comandos
- Gerenciamento do ciclo de vida (start/stop)
- Injeção de dependências (agent, store) nos handlers

**Estrutura Modularizada:**
```
src/
├── bot_simple.py          # Setup e registro (160 linhas)
├── agent_setup.py         # Criação do agente e TTS
├── commands.py            # Comandos (/start, /clear, /status)
└── handlers/              # Handlers por tipo de mídia
    ├── message.py         # Mensagens de texto
    ├── photo.py           # Fotos
    ├── video.py           # Vídeos
    ├── voice.py           # Voz
    ├── audio.py           # Áudio
    └── document.py         # Documentos
```

**Handlers Implementados (em `src/handlers/`):**

```python
# handlers/message.py
@require_auth
async def handle_message(update, context, agent, store)
    → Mensagens de texto
    → Detecção de YouTube
    → Solicitação de TTS
    → Chamada ao Agent

# handlers/photo.py
@require_auth
async def handle_photo(update, context, store)
    → Download da imagem
    → Análise com Groq Vision
    → Resposta com descrição

# handlers/video.py
@require_auth
async def handle_video(update, context, store)
    → Extração de frame (ffmpeg via SafeSubprocessExecutor)
    → Extração de áudio (ffmpeg via SafeSubprocessExecutor)
    → Análise visual (Groq Vision)
    → Transcrição de áudio (Whisper)
    → Resposta combinada

# handlers/voice.py
@require_auth
async def handle_voice(update, context, agent, store)
    → Transcrição (Whisper)
    → Processamento com Agent
    → Resposta contextual

# handlers/audio.py
@require_auth
async def handle_audio(update, context, agent, store)
    → Similar ao voice
    → Suporte a arquivos maiores

# handlers/document.py
@require_auth
async def handle_document(update, context, agent, store)
    → Excel/CSV: Análise profissional
    → Word: Extração de texto
    → Markdown: Leitura
    → Imagens: OCR
```

**Comandos (em `src/commands.py`):**
- `/start` - Mensagem de boas-vindas
- `/clear` - Limpar histórico
- `/status` - Status do sistema e ferramentas disponíveis

---

### 2. Agent (`src/workspace/core/agent.py`)

**Arquitetura do Agente:**

```python
class Agent:
    def __init__(self, tool_registry):
        self.groq = Groq()
        self.tools = tool_registry
        self.model = "llama-3.3-70b-versatile"
    
    async def run(self, user_message, history):
        # Loop de até 5 iterações
        for iteration in range(5):
            # 1. Chama LLM com tools
            response = self.groq.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools.get_schemas(),
                tool_choice="auto"
            )
            
            # 2. Se não há tool calls, retorna resposta
            if not response.tool_calls:
                return response.content
            
            # 3. Executa tools chamadas
            for tool_call in response.tool_calls:
                result = await self.tools.execute(
                    tool_call.name,
                    tool_call.arguments
                )
                messages.append(tool_result)
            
            # 4. Continua loop com resultados
```

**Fluxo de Execução:**

```
Usuário: "Busque na web sobre Python 3.12"
    ↓
Agent recebe mensagem
    ↓
LLM decide usar tool: web_search("Python 3.12")
    ↓
Tool Registry executa web_search
    ↓
Resultado retorna ao Agent
    ↓
LLM processa resultado e gera resposta
    ↓
Resposta enviada ao usuário
```

---

### 3. Tool Registry (`src/workspace/core/tools.py`)

**Gerenciamento de Ferramentas:**

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.schemas = []
    
    def register(self, name, function, schema):
        """Registra uma ferramenta"""
        self.tools[name] = function
        self.schemas.append(schema)
    
    async def execute(self, name, args):
        """Executa ferramenta"""
        if name in self.tools:
            return await self.tools[name](**args)
    
    def get_schemas(self):
        """Retorna schemas para LLM"""
        return self.schemas
```

**Ferramentas Registradas:**

| Categoria | Ferramenta | Descrição |
|-----------|-----------|-----------|
| **Web** | `web_search` | Busca DuckDuckGo |
| **Memória** | `rag_search` | Busca na memória |
| **Memória** | `save_memory` | Salva informação |
| **Código** | `search_code` | Busca em código |
| **Código** | `git_status` | Status do Git |
| **Código** | `git_diff` | Diff do Git |
| **Filesystem** | `read_file` | Lê arquivo |
| **Filesystem** | `write_file` | Escreve arquivo |
| **Filesystem** | `list_directory` | Lista diretório |
| **Clima** | `get_weather` | Clima atual |
| **Notícias** | `get_news` | Últimas notícias |
| **Lembretes** | `create_reminder` | Cria lembrete |
| **Gráficos** | `create_chart` | Gera gráfico |
| **Imagens** | `generate_image` | Gera imagem |

---

### 4. Segurança (`security/`)

**Camadas de Proteção:**

```python
# 1. Autenticação
@require_auth
def handler(update, context):
    # Verifica se user_id está em ALLOWED_USERS
    if user_id not in ALLOWED_USERS:
        return "Acesso negado"

# 2. Rate Limiting
class RateLimiter:
    def __init__(self, max_requests, window):
        self.limits = {}
    
    def is_allowed(self, user_id):
        # Verifica se usuário excedeu limite

# 3. Validação de Mídia
def validate_video(path):
    # Verifica tamanho, tipo, extensão
    if size > MAX_SIZE:
        return False

# 4. Sanitização
def sanitize_youtube_url(url):
    # Valida e limpa URL do YouTube
    if not is_valid_youtube(url):
        return None
```

---

### 5. Análise de Mídia

#### Imagens (Groq Vision)

```
Foto recebida
    ↓
Download via Telegram API
    ↓
Conversão para base64
    ↓
Groq Vision (Llama 4 Scout 17B)
    ↓
Descrição detalhada
```

#### Vídeos do Telegram

```
Vídeo recebido
    ↓
Download do vídeo
    ↓
┌─────────────────┬─────────────────┐
│  Extração Frame │  Extração Áudio │
│    (ffmpeg)     │    (ffmpeg)     │
└────────┬────────┴────────┬────────┘
         │                 │
         ▼                 ▼
   Groq Vision      Groq Whisper
         │                 │
         └────────┬────────┘
                  ▼
         Resposta Combinada
```

#### Vídeos do YouTube

```
Link do YouTube
    ↓
Download (yt-dlp) - qualidade baixa
    ↓
Extração de frames (1 a cada 5s, máx 10)
    ↓
Seleção de 3 frames (início, meio, fim)
    ↓
Análise com Groq Vision
    ↓
Resumo do vídeo
```

#### Áudio/Voz

```
Áudio recebido
    ↓
Download (.ogg ou .mp3)
    ↓
Groq Whisper Large v3 Turbo
    ↓
Transcrição em texto
    ↓
Processamento com Agent
    ↓
Resposta contextual
```

---

### 6. Text-to-Speech (ElevenLabs)

```
Usuário: "responda em áudio"
    ↓
Agent gera resposta em texto
    ↓
Detecção de keyword "em áudio"
    ↓
ElevenLabs TTS
    • Modelo: eleven_multilingual_v2
    • Voz: Antoni (masculina)
    • Idioma: PT-BR
    ↓
Conversão para MP3
    ↓
Envio como mensagem de voz
```

---

### 7. Análise de Documentos

#### Excel/CSV

```
Arquivo recebido
    ↓
Download
    ↓
Pandas: pd.read_excel() / pd.read_csv()
    ↓
Limpeza de dados:
    • Remove colunas/linhas vazias
    • Preenche NaN
    • Identifica tipos
    ↓
Geração de estatísticas:
    • Dimensões
    • Colunas numéricas/texto
    • Valores únicos
    • Estatísticas descritivas
    ↓
Análise com Agent (IA)
    ↓
Relatório executivo:
    • Resumo
    • Insights
    • Análise de padrões
    • Recomendações
```

#### Word (.docx)

```
Arquivo recebido
    ↓
python-docx: Document()
    ↓
Extração de parágrafos
    ↓
Concatenação de texto
    ↓
Preview (primeiros 3500 chars)
```

#### OCR (Imagens)

```
Imagem recebida
    ↓
Tesseract OCR
    • Idiomas: por+eng
    ↓
Extração de texto
    ↓
Retorno do texto extraído
```

---

### 8. Sistema de Lembretes

```
Usuário: create_reminder("Reunião", "31/01/2026 15:00")
    ↓
Parsing de data/hora
    ↓
Salva em /tmp/moltbot_reminders.json
    ↓
Thread de monitoramento (loop infinito)
    ↓
A cada 1 minuto:
    • Lê arquivo JSON
    • Verifica lembretes pendentes
    • Se horário chegou (±1 min):
        ├─ Envia Email (SMTP)
        └─ Envia Telegram
    • Remove lembretes enviados
```

---

### 9. Storage (`src/workspace/storage/sqlite_store.py`)

**Histórico de Conversação:**

```python
class SQLiteStore:
    def __init__(self):
        self.db = sqlite3.connect('moltbot.db')
        self.create_tables()
    
    def add_message(self, role, content):
        """Salva mensagem no histórico"""
    
    def get_history(self, limit=10):
        """Recupera últimas N mensagens"""
    
    def log_metric(self, metric, data):
        """Registra métrica"""
```

---

## Fluxos de Dados

### Fluxo 1: Mensagem de Texto Simples

```
1. Usuário envia: "Olá"
2. Telegram → handle_message()
3. @require_auth verifica user_id
4. Agent.run("Olá", history=[])
5. Groq LLM gera resposta (sem tools)
6. Resposta enviada ao usuário
```

### Fluxo 2: Mensagem com Tool Calling

```
1. Usuário: "Qual o clima em São Paulo?"
2. Telegram → handle_message()
3. @require_auth ✓
4. Agent.run("Qual o clima em São Paulo?")
5. LLM decide: tool_call(get_weather, city="São Paulo")
6. Tool Registry executa get_weather()
7. OpenWeatherMap API retorna dados
8. LLM processa resultado
9. Resposta: "Em São Paulo está 25°C, ensolarado..."
```

### Fluxo 3: Análise de Imagem

```
1. Usuário envia foto
2. Telegram → handle_photo()
3. @require_auth ✓
4. Download da imagem
5. Conversão para base64
6. Groq Vision analisa
7. Resposta: "Esta imagem mostra..."
```

### Fluxo 4: Vídeo do YouTube

```
1. Usuário: "https://youtube.com/watch?v=..."
2. handle_message() detecta YouTube
3. YouTubeAnalyzer.analyze_youtube_video()
4. yt-dlp baixa vídeo (qualidade baixa)
5. ffmpeg extrai 10 frames
6. Seleciona 3 frames (início, meio, fim)
7. Groq Vision analisa frames
8. Resposta: "🎬 Resumo do Vídeo: ..."
```

---

## Tecnologias Utilizadas

### Backend
- **Python 3.12.3** - Linguagem principal
- **python-telegram-bot 20.7** - API do Telegram
- **asyncio** - Programação assíncrona

### IA e ML
- **Groq** - LLM, Vision, Whisper
  - `llama-3.3-70b-versatile` - Chat
  - `meta-llama/llama-4-scout-17b-16e-instruct` - Vision
  - `whisper-large-v3-turbo` - Transcrição
- **ElevenLabs** - Text-to-Speech

### Processamento de Mídia
- **ffmpeg** - Vídeo/áudio
- **yt-dlp** - Download do YouTube
- **Pillow** - Processamento de imagens
- **pytesseract** - OCR

### Análise de Dados
- **pandas** - Excel/CSV
- **python-docx** - Word
- **matplotlib** - Gráficos

### Storage
- **SQLite** - Histórico de conversação
- **JSON** - Lembretes

### Segurança
- **dotenv** - Variáveis de ambiente
- **functools.wraps** - Decorators
- **Custom modules** - auth, rate_limiter, sanitizer

---

## Padrões de Projeto

### 1. Registry Pattern
```python
# Tool Registry centraliza todas as ferramentas
registry = ToolRegistry()
registry.register("tool_name", function, schema)
```

### 2. Decorator Pattern
```python
# Autenticação como decorator
@require_auth
async def handler(update, context):
    pass
```

### 3. Strategy Pattern
```python
# Diferentes estratégias para diferentes tipos de mídia
if is_photo:
    handle_photo()
elif is_video:
    handle_video()
elif is_audio:
    handle_audio()
```

### 4. Factory Pattern
```python
# Criação do agente
def create_agent_no_sandbox():
    registry = ToolRegistry()
    # Registra ferramentas
    return Agent(registry)
```

---

## Escalabilidade

### Limitações Atuais
- **Single-threaded** (exceto lembretes)
- **Sem cache** de respostas
- **Sem load balancing**
- **Storage local** (SQLite)

### Melhorias Futuras
- [ ] Containerização (Docker)
- [ ] Redis para cache
- [ ] PostgreSQL para storage
- [ ] Kubernetes para orquestração
- [ ] Message queue (RabbitMQ/Kafka)
- [ ] Horizontal scaling

---

## Segurança

### Implementado
- ✅ Autenticação por whitelist
- ✅ Rate limiting
- ✅ Validação de mídia
- ✅ Credenciais protegidas (chmod 600)
- ✅ Sanitização básica

### Recomendado para Produção
- [ ] HTTPS obrigatório
- [ ] Criptografia de dados
- [ ] Audit logging
- [ ] Backup automático
- [ ] Monitoramento de segurança
- [ ] Penetration testing

---

## Performance

### Otimizações Implementadas
- **Vídeos:** Qualidade baixa para download rápido
- **Frames:** Máximo 10 frames, análise de 3
- **Timeouts:** Configurados em todas as operações
- **Async:** Handlers assíncronos

### Métricas Típicas
- **Mensagem de texto:** < 2s
- **Análise de imagem:** 3-5s
- **Vídeo do Telegram:** 10-20s
- **Vídeo do YouTube:** 30-60s
- **Transcrição de áudio:** 5-10s

---

## Monitoramento

### Logs
```bash
# Logs em tempo real (na pasta onde o bot roda)
tail -f bot.log

# Buscar erros
grep -i error bot.log

# Métricas
grep "message_processed" bot.log | wc -l
```

### Métricas Coletadas
- Mensagens processadas
- Erros por tipo
- Tempo de resposta
- Uso de ferramentas

---

## 🛡️ Módulos de Segurança (v1.1 - 2026-01-31)

### Overview

Novos módulos de segurança implementados para garantir estabilidade, prevenir vulnerabilidades e melhorar a manutenibilidade do sistema.

### 1. SecureFileManager (`src/security/file_manager.py`)

**Propósito:** Gerenciamento seguro de arquivos temporários com auto-cleanup garantido.

**Funcionalidades:**
- Context managers para criação automática e limpeza de arquivos
- Sanitização de filenames contra path traversal
- Validação real de MIME types usando python-magic
- Whitelist de extensões permitidas
- Limite de tamanho (50MB)
- Diretório seguro: `/tmp/moltbot_secure` (criado automaticamente)

**Exemplo de Uso:**
```python
from security import secure_files

async with secure_files.temp_file(suffix='.mp4') as video_path:
    await download_video(video_path)
    await process_video(video_path)
    # Arquivo automaticamente deletado ao sair do contexto
```

**Problemas Resolvidos:**
- ✅ Vazamento de memória (arquivos temporários acumulados)
- ✅ Path traversal attacks
- ✅ MIME type spoofing
- ✅ Limpeza manual inconsistente

---

### 2. SafeSubprocessExecutor (`security/executor.py`)

**Propósito:** Execução assíncrona e segura de subprocessos.

**Funcionalidades:**
- Execução assíncrona (não bloqueia o event loop)
- Whitelist de comandos permitidos: ffmpeg, ffprobe, tesseract, python
- Prevenção de command injection (bloqueia `;`, `&&`, `||`, `|`, `>`, `<`, etc)
- Timeout configurável (padrão: 30s)
- Tratamento especial para exit code 8 do FFmpeg (normal em Ubuntu/Debian)

**Exemplo de Uso:**
```python
from security import SafeSubprocessExecutor

success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video_path), "-vframes", "1",
    "-q:v", "2", str(frame_path)
])

if not success:
    logger.error(f"FFmpeg falhou: {stderr}")
```

**Problemas Resolvidos:**
- ✅ Command injection vulnerabilities
- ✅ Processos travados (bloqueando o bot)
- ✅ Bloqueio do event loop asyncio
- ✅ Validação incorreta de exit codes

---

### 3. Retry Decorator (`utils/retry.py`)

**Propósito:** Resiliência a falhas temporárias de API.

**Funcionalidades:**
- Exponential backoff (delays: 1s → 2s → 4s...)
- Jitter aleatório para evitar thundering herd
- Configurável: max_retries, initial_delay, max_delay, exceções
- Suporte para funções async e sync

**Exemplo de Uso:**
```python
from utils import retry_with_backoff

@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
async def call_groq_api(image_data):
    return groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[...]
    )
    # Se falhar, tenta automaticamente mais 2 vezes
```

**Problemas Resolvidos:**
- ✅ Falhas temporárias de rede
- ✅ Instabilidade de APIs externas
- ✅ Rate limiting não intencional
- ✅ Timeouts ocasionais

---

### 4. Configuração Centralizada (`config/settings.py`)

**Propósito:** Centralização de todas as configurações do sistema.

**Funcionalidades:**
- Dataclass frozen (imutável)
- Valores via variáveis de ambiente ou defaults sensíveis
- Paths configuráveis: BASE_DIR, TEMP_DIR, DATA_DIR
- Modelos de API, limites, rate limiting, segurança
- Fácil acesso global via `from config import config`

**Exemplo de Uso:**
```python
from config import config

# Paths configuráveis via env vars
base_dir = config.BASE_DIR       # MOLTBOT_DIR
 temp_dir = config.TEMP_DIR      # MOLTBOT_TEMP ou /tmp/moltbot_secure

# Modelos de API
model = config.GROQ_MODEL_VISION  # "meta-llama/llama-4-scout-17b-16e-instruct"

# Limites
max_size = config.MAX_FILE_SIZE_MB  # 50
```

**Problemas Resolvidos:**
- ✅ Hardcoded paths espalhados pelo código
- ✅ Dificuldade de manutenção
- ✅ Inconsistência de configurações
- ✅ Deploy em diferentes ambientes

---

### 5. Rate Limiting no Agent (`src/workspace/core/agent.py`)

**Propósito:** Proteção contra abuso do sistema.

**Funcionalidades:**
- Verificação de limite no início do processamento
- Limites configuráveis: 20 msgs/min, 5 media/min, 3 YouTube/5min
- Mensagem em português quando limitado
- Fácil integração passando `user_id` para `agent.run()`

**Exemplo de Uso:**
```python
# No handler de mensagens
response = await agent.run(
    user_message,
    history,
    user_id=update.effective_user.id
)
# Retorna mensagem de rate limit se excedido
```

**Problemas Resolvidos:**
- ✅ Abuso do sistema (spam)
- ✅ Consumo excessivo de recursos
- ✅ Custos inesperados de API
- ✅ Fair use entre usuários

---

### 6. Migração para Asyncio Puro (`src/bot_simple.py`)

**Propósito:** Modernização do sistema de lembretes.

**Mudanças:**
- Sistema de lembretes: threading → asyncio.create_task()
- Signal handling para graceful shutdown (SIGINT, SIGTERM)
- Cleanup adequado de recursos (cancelamento de tasks)
- Função `main()` → `async def main()`

**Problemas Resolvidos:**
- ✅ Instabilidade do sistema de lembretes
- ✅ Threads órfãs
- ✅ Cleanup inadequado
- ✅ Race conditions

---

## 🧪 Testes e Validação

### Cobertura de Testes (2026-01-31)

O sistema possui múltiplas camadas de testes:

#### 1. Testes Via Terminal (Funcionalidades Core)
**Localização:** `tests/test_bot_completo.py`

Testes executados em ambiente real (venv311) para validar funcionalidades independentes do Telegram:

| Funcionalidade | Status | Detalhes |
|---------------|--------|----------|
| Web Search (DuckDuckGo) | ✅ OK | Busca web funcional |
| RAG Search | ✅ OK | Memória pessoal acessível |
| Save Memory | ✅ OK | Persistência funcionando |
| Search Code | ✅ OK | 88 matches em teste |
| Filesystem (R/W/List) | ✅ OK | Operações de arquivo OK |
| Git Status/Diff | ✅ OK | Integração git funcionando |
| Tool Registry | ✅ OK | 8 ferramentas registradas |

**Execução (na raiz do repositório):**
```bash
source venv/bin/activate
PYTHONPATH=src python tests/test_bot_completo.py
# Ou: PYTHONPATH=src python -m pytest tests/ -v
```

#### 2. Testes E2E (End-to-End)
**Localização:** `tests/test_e2e.py`, `tests/test_e2e_simple.py`

- ✅ **28/28 testes passando (100%)**
- Validação de integração completa
- Testes de API (Groq, Telegram)
- Testes de segurança

#### 3. Arquivos de Teste Disponíveis
```
tests/
├── test_bot_completo.py         # 7 funcionalidades (terminal)
├── test_bot_simples.py          # 4 funcionalidades (core)
├── test_bot_funcionalidades.py  # 11 funcionalidades
├── test_e2e.py                  # Testes E2E completos
└── test_e2e_simple.py           # Testes E2E simplificados
```

---

## Conclusão

O Assistente Digital utiliza uma arquitetura modular e extensível, com separação clara de responsabilidades. O uso de agentes autônomos com tool calling permite adicionar novas funcionalidades facilmente, enquanto a camada de segurança garante uso controlado.

**Pontos Fortes:**
- ✅ Modular e extensível
- ✅ Múltiplas capacidades de IA
- ✅ Segurança avançada implementada (v1.1)
- ✅ Fácil manutenção
- ✅ Resiliência a falhas

**Áreas de Melhoria:**
- ⚠️ Escalabilidade limitada
- ⚠️ Sem cache distribuído
- ⚠️ Storage local (SQLite)
- ⚠️ Monitoramento avançado
