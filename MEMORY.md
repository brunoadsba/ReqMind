# 🧠 MEMORY - Assistente Digital

**Contexto completo do projeto para desenvolvedores**

---

## 📋 Informações Essenciais

### Identidade do Projeto
- **Nome:** Assistente Digital de Bruno
- **Tipo:** Bot Telegram com IA
- **Bot:** @br_bruno_bot
- **User ID Autorizado:** 6974901522
- **Status:** ✅ Produção (uso pessoal)
- **Versão:** 1.1
- **Última atualização:** 2026-02-05

### Stack Tecnológico
- **Linguagem:** Python 3.12.3
- **Framework Bot:** python-telegram-bot 20.7
- **IA Principal:** Groq (Llama 3.3 70B, Llama 4 Scout, Whisper)
- **TTS:** ElevenLabs (opcional)
- **Storage:** SQLite + JSON
- **Mídia:** ffmpeg, yt-dlp, tesseract

---

## 🏗️ Arquitetura do Sistema

### Padrão Arquitetural
**Agente Autônomo com Tool Calling**

```
Telegram → Bot → Agent → LLM (decide tools) → Tool Registry → Executa → Resposta
```

### Componentes Principais

Código em **`src/`**. Execução: `PYTHONPATH=src` na raiz.

1. **src/bot_simple.py** (160 linhas) - **Modularizado**
   - Ponto de entrada e setup do bot
   - Registro de handlers e comandos
   - Gerenciamento do ciclo de vida (start/stop)

2. **src/handlers/** - Handlers organizados por tipo de mídia
   - `message.py` - Mensagens de texto, YouTube, TTS
   - `photo.py` - Análise de imagens com Groq Vision
   - `video.py` - Análise de vídeos (frame + áudio)
   - `voice.py` - Transcrição de voz
   - `audio.py` - Transcrição de arquivos de áudio
   - `document.py` - Excel, CSV, Word, Markdown, OCR

3. **src/commands.py** - Comandos do bot
   - `/start` - Mensagem de boas-vindas
   - `/clear` - Limpar histórico
   - `/status` - Status do sistema

4. **src/agent_setup.py** - Setup do agente
   - `create_agent_no_sandbox()` - Cria agente com todas as ferramentas
   - `text_to_speech()` - Conversão texto → áudio (ElevenLabs)

5. **src/workspace/core/agent.py**
   - Loop de tool calling (até 5 iterações)
   - Integração com Groq (com retry)
   - Rate limiting por usuário
   - Fallback em 429: Kimi K2.5 (NVIDIA) → RAG (memory.json); truncamento em fronteira de frase e "(Resumo truncado.)"
   - Fallback sem tools

6. **src/workspace/core/tools.py**
   - Registry pattern
   - 15 ferramentas registradas

7. **src/workspace/tools/** (vários arquivos)
   - Ferramentas específicas
   - Cada uma retorna dict com success/error

8. **src/security/** (auth, rate_limiter, sanitizer, file_manager, executor, media_validator)
   - auth: Whitelist de usuários
   - rate_limiter: Controle de taxa
   - sanitizer: Sanitização de inputs e paths
   - file_manager: SecureFileManager (temp seguros)
   - executor: SafeSubprocessExecutor
   - media_validator: Validação de mídia

---

## 🔑 Decisões Arquiteturais Importantes

### 1. Migração GLM-4.6V → Groq Vision
**Quando:** Janeiro 2026  
**Por quê:**
- Groq é mais rápido (latência menor)
- Mais confiável (menos falhas)
- Gratuito (tier free generoso)
- Mesma API para chat e vision

**Impacto:** Código GLM ainda existe mas não é usado.

### 2. Memória RAG e alimentação de normas (2026-02-05)
**O quê:** Memória persistente em `src/dados/memory.json` (workspace.tools.impl.rag_memory). Em 429 (rate limit Groq), se Kimi (NVIDIA) não estiver disponível, o agente busca na memória por termos como "NR-29" ou "NR" e devolve trecho relevante (~1200 caracteres), truncando em fronteira de frase e adicionando "(Resumo truncado.)".

**Scripts de alimentação:**
- `scripts/feed_nr29_to_memory.py` — injeta resumo estruturado da NR-29 na memória.
- `scripts/feed_nr29_oficial.py` — lê `scripts/nr29_oficial_dou.txt`, divide por seções (29.1, 29.2, …) e injeta texto oficial. Uso: `PYTHONPATH=src python scripts/feed_nr29_oficial.py [caminho_opcional]`.

**Arquivo de memória:** `config.DATA_DIR` (ex.: `src/dados/`) + `memory.json`.

### 3. Dois Diretórios de Trabalho
**Desenvolvimento:** `/home/brunoadsba/Assistente-Digital/assistente`  
**Execução:** `/home/brunoadsba/clawd/moltbot-setup`

**Por quê:** Histórico do projeto (migração em andamento)

**Workflow:**
1. Desenvolve em `/Assistente-Digital/assistente`
2. Testa localmente
3. Copia para `/clawd/moltbot-setup`
4. Executa de lá (tem .env e venv)

**TODO:** Consolidar em um único diretório.

### 4. Gerenciamento de Instâncias (2026-01-31)
**Problema:** Múltiplas instâncias do bot rodando simultaneamente causavam conflitos no Telegram API.

**Sintomas:**
- Respostas demoravam até 6 minutos
- Erro: `Conflict: terminated by other getUpdates request`
- Bot processava em 3s mas entregava em 6min

**Causa Raiz:**
- clawdbot-gateway.service (instância automática no boot)
- bot_simple.py (instância manual)
- Telegram API rejeita múltiplas conexões do mesmo token

**Solução Implementada:**
Scripts de gerenciamento em `/home/brunoadsba/clawd/moltbot-setup/scripts/`:

1. **start_bot_safe.sh** - Inicialização segura
   - Mata todas as instâncias existentes
   - Inicia apenas 1 instância
   - Salva PID e aguarda inicialização

2. **stop_bot.sh** - Parada segura
   - Para gracefulmente
   - Mata instâncias restantes
   - Limpa PID file

3. **healthcheck.sh** - Monitoramento
   - Verifica se há múltiplas instâncias
   - Verifica erros recentes no log
   - Reporta status do bot

**Como Usar:**
```bash
cd /home/brunoadsba/clawd/moltbot-setup

# Iniciar bot (seguro)
./scripts/start_bot_safe.sh

# Verificar status
./scripts/healthcheck.sh

# Parar bot
./scripts/stop_bot.sh
```

**Serviços Conflitantes:**
- clawdbot-gateway.service foi desabilitado
- Bot deve rodar apenas via bot_simple.py
- Apenas 1 instância permitida por token

### 5. Storage Simples (SQLite + JSON)
**Por quê:**
- Uso pessoal (não precisa escalar)
- Sem dependências externas
- Fácil de debugar

**Limitações conhecidas:**
- Lembretes em /tmp (volátil)
- Sem backup automático
- Não escala

### 6. ffmpeg Exit Code 8
**Descoberta:** Builds Ubuntu/Debian do ffmpeg retornam exit code 8 com `--version`.

**Por quê:**
- Exit code 8 = "sem operação de conversão"
- Comportamento específico da distribuição
- Não é bug, é comportamento normal

**Impacto:**
- Testes com `check=True` falham incorretamente
- Solução: Validar por output, não por exit code

**Código:**
```python
# Validação robusta
result = subprocess.run(['ffmpeg', '--version'], capture_output=True, timeout=5)
output = result.stdout.decode() + result.stderr.decode()
success = (result.returncode == 0 or 
           (result.returncode == 8 and 'ffmpeg' in output.lower()))
```

**Documentado em:** `docs/INSIGHTS.md`

### 7. Análise de Vídeo Otimizada
**Estratégia:** 3 frames (início, meio, fim) em vez de todos

**Por quê:**
- Tempo: 30-60s vs 2-3min
- Custo: 3 imagens vs 10+
- Qualidade: Suficiente para resumo

**Trade-off aceito:** Menos detalhes, mais velocidade.

---

## 🛠️ Ferramentas Implementadas (15)

### Web & Search
1. **web_search** - DuckDuckGo
2. **rag_search** - Busca na memória
3. **save_memory** - Salva na memória

### Filesystem
4. **read_file** - Lê arquivo
5. **write_file** - Escreve arquivo
6. **list_directory** - Lista diretório

### Code & Git
7. **search_code** - Busca em código (grep)
8. **git_status** - Status do Git
9. **git_diff** - Diff do Git

### Extras
10. **get_weather** - OpenWeatherMap
11. **get_news** - NewsAPI
12. **create_reminder** - Email + Telegram
13. **create_chart** - matplotlib
14. **generate_image** - IA (não configurado)
15. **analyze_youtube_video** - Análise de vídeo YouTube (frames + transcrição)

**Padrão:** Todas retornam `{"success": bool, "data": any}` ou `{"success": bool, "error": str}`

---

## 🔒 Segurança

### Implementado (2026-01-31)
- ✅ **Autenticação por whitelist** (`security/auth.py`) - user_id validation
- ✅ **Decorator @require_auth** - Protege handlers sensíveis
- ✅ **Rate limiting** (`security/rate_limiter.py`) - 20 msgs/min, 5 media/min, 3 YouTube/5min
- ✅ **Rate limiting no Agent** - Verificação no método `agent.run()`
- ✅ **SecureFileManager** (`security/file_manager.py`) - Arquivos temporários seguros com auto-cleanup
- ✅ **SafeSubprocessExecutor** (`security/executor.py`) - Execução assíncrona com whitelist e injection prevention
- ✅ **Sanitização de filenames** - Proteção contra path traversal
- ✅ **Validação de MIME types** - Validação real usando python-magic
- ✅ **Configuração centralizada** (`config/settings.py`) - Sem hardcoded paths
- ✅ **.env protegido** (chmod 600)
- ✅ **Retry com backoff** (`utils/retry.py`) - Resiliência a falhas de API

### Módulos de Segurança

```
security/
├── __init__.py              # Exporta todos os módulos
├── auth.py                  # Autenticação (@require_auth)
├── rate_limiter.py          # Rate limiting por usuário
├── sanitizer.py             # Sanitização de inputs
├── media_validator.py       # Validação de arquivos de mídia
├── file_manager.py          # SecureFileManager (NOVO)
└── executor.py              # SafeSubprocessExecutor (NOVO)
```

### Como Usar

**Proteger handler:**
```python
from security.auth import require_auth

@require_auth
async def handle_sensitive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Apenas usuários autorizados (ALLOWED_USERS) podem acessar
    pass
```

**Arquivos temporários seguros:**
```python
from security import secure_files

async with secure_files.temp_file(suffix='.mp4') as path:
    # Arquivo criado em /tmp/moltbot_secure/
    # Auto-deletado ao sair do contexto (mesmo se der erro)
    await process_file(path)
```

**Subprocessos seguros:**
```python
from security import SafeSubprocessExecutor

success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video), "-vframes", "1", str(frame)
])
# Só permite: ffmpeg, ffprobe, tesseract, python
# Bloqueia: ; && || | > < ` $ etc
```

**Configuração segura:**
```python
from config import config

# Paths configuráveis via env vars
base_dir = config.BASE_DIR       # MOLTBOT_DIR ou default
 temp_dir = config.TEMP_DIR      # MOLTBOT_TEMP ou /tmp/moltbot_secure
```

### Checklist de Segurança

| Aspecto | Status | Implementação |
|---------|--------|---------------|
| Autenticação | ✅ | Whitelist de user_ids |
| Autorização | ✅ | @require_auth decorator |
| Rate Limiting | ✅ | Por usuário e global |
| Input Validation | ✅ | Sanitização de filenames |
| Path Traversal | ✅ | Proteção via SecureFileManager |
| Command Injection | ✅ | SafeSubprocessExecutor whitelist |
| File Cleanup | ✅ | Context managers garantem cleanup |
| MIME Validation | ✅ | python-magic para validação real |
| Config Management | ✅ | Centralizado em config/settings.py |
| Error Handling | ✅ | Try/except em todas as operações |

**Nível atual:** Seguro para uso pessoal e pequena escala  
**Status:** Todas as melhorias críticas implementadas conforme `ajustes.md`

---

## 🧪 Testes e Validação

### Status dos Testes (Atualizado: 2026-01-31)

#### ✅ Testes de Funcionalidades Via Terminal - 7/7 PASSARAM (100%)
Testes executados em ambiente real (venv311) verificando funcionalidades core:

| # | Funcionalidade | Status | Evidência |
|---|---------------|--------|-----------|
| 1 | **Web Search (DuckDuckGo)** | ✅ OK | Busca executada com sucesso |
| 2 | **RAG Search (Memória)** | ✅ OK | Encontrou entradas na memória pessoal |
| 3 | **Save Memory** | ✅ OK | Salvou informação de teste |
| 4 | **Search Code** | ✅ OK | 88 matches de "async def" |
| 5 | **Filesystem (R/W/List)** | ✅ OK | Todas operações funcionando |
| 6 | **Git (Status/Diff)** | ✅ OK | Status e diff operacionais |
| 7 | **Tool Registry** | ✅ OK | 8 ferramentas registradas |

**Comando para executar (a partir da raiz do repo):**
```bash
# Ative o venv e instale dependências (pip install -r requirements.txt)
PYTHONPATH=src python -m pytest tests/ -v
```

#### ✅ Testes E2E Originais
- ✅ **28/28 testes E2E (100%)** - Sistema totalmente validado
- ✅ Bot rodando e operacional
- ✅ 15 ferramentas funcionais
- ✅ APIs validadas (Groq + Telegram)
- ✅ Segurança ativa

### Arquivos de Teste Disponíveis
```
tests/
├── test_bot_completo.py       # Teste via terminal (7 funcionalidades) ✅ NOVO
├── test_bot_simples.py        # Teste simplificado (4 funcionalidades)
├── test_bot_funcionalidades.py # Teste completo (11 funcionalidades)
├── test_e2e.py                # Teste end-to-end original
└── test_e2e_simple.py         # Teste E2E simplificado
```

### Notas Importantes
- **venv311:** Bot DEVE rodar dentro do venv311
- **ffmpeg:** Retorna exit code 8 (normal em Ubuntu/Debian)
- **Validação:** Por output, não apenas exit code
- **Resultado esperado:** 12/12 no teste rápido, 28/28 no completo

---

## 📁 Estrutura de Diretórios

O código-fonte fica em `src/`. Na raiz: documentação, testes, config e scripts.

```
assistente/
├── README.md                  # Início rápido
├── MEMORY.md                  # Este arquivo
├── .env.example               # Exemplo de configuração
├── requirements.txt           # Dependências
├── docs/                      # 📚 Documentação
│   ├── ARCHITECTURE.md        # Arquitetura completa
│   ├── AUDITORIA_PROJETO.md   # Relatório de auditoria
│   ├── PLANO_IMPLEMENTACAO_AUDITORIA.md
│   ├── DOCS_INDEX.md          # Índice navegável
│   ├── security/              # Docs de segurança
│   └── ...
├── scripts/                   # 🔧 Scripts (start.sh, stop.sh)
├── tests/                     # 🧪 Testes (test_e2e_simple.py, test_security.py, ...)
│
└── src/                       # Código-fonte (modularizado)
    ├── bot_simple.py          # Bot principal (160 linhas) - setup e registro
    ├── agent_setup.py         # Setup do agente e TTS
    ├── commands.py            # Comandos do bot (/start, /clear, /status)
    ├── handlers/              # Handlers por tipo de mídia
    │   ├── __init__.py
    │   ├── message.py         # Mensagens de texto
    │   ├── photo.py           # Fotos
    │   ├── video.py           # Vídeos
    │   ├── voice.py           # Voz
    │   ├── audio.py           # Áudio
    │   └── document.py         # Documentos
    ├── config/
    │   ├── settings.py        # Config centralizada
    │   └── moltbot.json
    ├── security/              # auth, rate_limiter, sanitizer, file_manager, executor, media_validator
    ├── utils/                 # retry.py
    └── workspace/
        ├── core/              # agent.py, tools.py, sandbox.py (legado)
        ├── tools/             # web_search, filesystem, code_tools, rag_tools, youtube_analyzer, ...
        ├── storage/           # sqlite_store.py
        ├── memory/            # memory_manager, fact_store
        ├── runs/              # RunManager
        └── agent/             # IDENTITY, POLICIES, CONTEXT_PACK
```

**Execução:** a partir da raiz, com `PYTHONPATH=src` (ex.: `PYTHONPATH=src python src/bot_simple.py` ou `cd src && python bot_simple.py`).

---

## 🚀 Como Começar (Onboarding)

### 1. Setup Inicial (15 min)

```bash
# Clone o projeto
cd /home/brunoadsba/Assistente-Digital/assistente

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure .env
cp .env.example .env
vim .env  # Adicione suas API keys
chmod 600 .env

# Teste
python tests/test_e2e.py
```

### 2. Entenda a Arquitetura (30 min)

Leia nesta ordem:
1. `README.md` - Overview
2. `docs/ARCHITECTURE.md` - Arquitetura detalhada
3. `bot_simple.py` - Código principal

### 3. Primeiro Teste (10 min)

```bash
# Execute localmente
python bot_simple.py

# No Telegram, envie:
# "oi" → Deve responder
# Envie uma foto → Deve analisar
```

### 4. Gerenciamento do Bot (15 min)

```bash
# Iniciar bot (MÉTODO CORRETO - usa script seguro)
cd /home/brunoadsba/clawd/moltbot-setup
./scripts/start_bot_safe.sh

# Verificar status
./scripts/healthcheck.sh

# Parar bot
./scripts/stop_bot.sh

# IMPORTANTE: NUNCA inicie bot manualmente (python bot_simple.py &)
# Isso pode criar múltiplas instâncias e causar conflitos
# SEMPRE use os scripts de gerenciamento
```

**⚠️ AVISO CRÍTICO:**
- Bot deve rodar apenas 1 instância por vez
- Não use `python bot_simple.py &` manualmente
- Não execute bot em background sem os scripts
- Sempre use `./scripts/start_bot_safe.sh`

### 5. Adicione Sua Primeira Ferramenta (30 min)

Siga: `docs/DEVELOPMENT.md` → "Adicionar Nova Funcionalidade"

---

## 🔄 Workflow de Desenvolvimento

### Desenvolvimento Local
```bash
cd /home/brunoadsba/Assistente-Digital/assistente
source venv/bin/activate

# Edite código
vim bot_simple.py

# Teste
python tests/test_e2e.py
python bot_simple.py  # Teste manual
```

### Deploy para Produção
```bash
# 1. Pare bot atual
pkill -f bot_simple.py

# 2. Copie alterações
cp bot_simple.py /home/brunoadsba/clawd/moltbot-setup/

# 3. Inicie
cd /home/brunoadsba/clawd/moltbot-setup
./start_bot.sh

# 4. Verifique logs
tail -f bot.log
```

---

## 🐛 Debugging

### Logs
```bash
# Logs em tempo real
tail -f /home/brunoadsba/clawd/moltbot-setup/bot.log

# Buscar erros
grep -i error bot.log

# Buscar por user_id
grep "user_id=6974901522" bot.log
```

### Problemas Comuns

**Bot não responde:**
- Verifique se está rodando: `ps aux | grep bot_simple`
- Veja logs: `tail -50 bot.log`
- Verifique user_id em `security/auth.py`
- Execute healthcheck: `./scripts/healthcheck.sh`

**Múltiplas instâncias (CONFLITO):**
- Sintoma: Erro `Conflict: terminated by other getUpdates request`
- Sintoma: Respostas demoram minutos
- Solução: `./scripts/stop_bot.sh && ./scripts/start_bot_safe.sh`
- Verifique: `./scripts/healthcheck.sh` (deve mostrar "1 instância")
- Verifique se clawdbot-gateway está rodando: `systemctl --user status clawdbot-gateway`
- Se necessário: `systemctl --user disable --now clawdbot-gateway`

**Erro de API:**
- Verifique .env: `cat .env | grep API_KEY`
- Teste Groq: `python -c "from groq import Groq; ..."`

**Tool calling falha:**
- Veja logs do Agent em `workspace/core/agent.py`
- Adicione prints para debug

---

## 📊 Métricas do Projeto

### Código
- **Arquivos Python:** 37 (atualizado com novos módulos de segurança)
- **Linhas de código:** ~4.200 (incluindo melhorias de segurança)
- **Handlers:** 6
- **Ferramentas:** 15
- **Modelos de IA:** 3 (Chat, Vision, Audio)
- **Módulos de Segurança:** 6 (auth, rate_limiter, sanitizer, media_validator, file_manager, executor)
- **Utilitários:** 1 (retry decorators)
- **Configuração:** 1 (settings centralizado)

### Documentação
- **Arquivos:** 9 principais
- **Tamanho:** 120KB
- **Linhas:** 4.573
- **Cobertura:** 100%

### Performance
- **Mensagem de texto:** < 2s
- **Análise de imagem:** 3-5s
- **Vídeo do Telegram:** 10-20s
- **Vídeo do YouTube:** 30-60s
- **Transcrição de áudio:** 5-10s

---

## 🔑 Variáveis de Ambiente (.env)

### Obrigatórias
```bash
TELEGRAM_TOKEN=...        # Bot do Telegram
GROQ_API_KEY=...          # IA principal
```

### Opcionais
```bash
ELEVENLABS_API_KEY=...    # Text-to-Speech
EMAIL_ADDRESS=...         # Lembretes por email
SMTP_PASSWORD=...         # Senha do email
OPENWEATHER_API_KEY=...   # Clima
NEWS_API_KEY=...          # Notícias

# Configuração de paths (novos)
MOLTBOT_DIR=...           # Diretório base do projeto (default: diretório atual)
MOLTBOT_TEMP=...          # Diretório de arquivos temporários (default: /tmp/moltbot_secure)
ALLOWED_USERS=...         # IDs autorizados separados por vírgula (ex: "123456789,987654321")
```

### Legado (não usado)
```bash
GLM_API_KEY=...           # Substituído por Groq Vision
KIMI_API_KEY=...
OPENROUTER_API_KEY=...
```

---

## 🎯 Funcionalidades Principais

### 1. Chat Inteligente
- Modelo: Llama 3.3 70B
- Tool calling automático
- 15 ferramentas disponíveis

### 2. Análise de Mídia
- **Imagens:** Groq Vision (Llama 4 Scout)
- **Vídeos Telegram:** Frame + áudio
- **Vídeos YouTube:** 3 frames (início, meio, fim)
- **Áudio:** Whisper Large v3 Turbo

### 3. Análise de Documentos
- **Excel/CSV:** Análise profissional com IA
- **Word:** Extração de texto
- **OCR:** Tesseract

### 4. Ferramentas de Dev
- Filesystem (read, write, list)
- Git (status, diff)
- Code search (grep)

### 5. Segurança e Estabilidade (NOVO - 2026-01-31)
- **SecureFileManager:** Arquivos temporários com auto-cleanup
- **SafeSubprocessExecutor:** Execução segura de comandos (ffmpeg, etc)
- **Rate Limiting:** Proteção contra abuso (20 msgs/min)
- **Retry com Backoff:** Resiliência a falhas de API
- **Config Centralizada:** Sem hardcoded paths

### 6. Extras
- Web search (DuckDuckGo)
- Memória RAG
- Lembretes (Email + Telegram)
- Clima, notícias, gráficos

---

## 🚨 Pontos de Atenção

### 1. Segurança
**Status:** ✅ Implementada (2026-01-31)  
**Melhorias:** SecureFileManager, SafeSubprocessExecutor, Rate Limiting, Retry decorators  
**Nível:** Seguro para uso pessoal e pequena escala

### 2. Dois Diretórios
**Status:** Temporário  
**Ação:** Consolidar em um único diretório

### 3. Storage Volátil
**Status:** Lembretes em /tmp  
**Ação:** Migrar para banco de dados

### 4. Sem Testes Unitários
**Status:** Apenas E2E  
**Ação:** Adicionar testes unitários

### 5. Sem CI/CD
**Status:** Deploy manual  
**Ação:** Implementar GitHub Actions

---

## 📚 Documentação Completa

### Para Usuários
- `README.md` - Início rápido
- `docs/FEATURES.md` - Todas as funcionalidades

### Para Desenvolvedores
- `MEMORY.md` - Este arquivo (contexto completo)
- `docs/ARCHITECTURE.md` - Arquitetura
- `docs/DEVELOPMENT.md` - Como desenvolver
- `docs/TOOLS_REFERENCE.md` - Ferramentas

### Para Integradores
- `docs/API_REFERENCE.md` - APIs e limites

### Navegação
- `docs/DOCS_INDEX.md` - Índice completo

---

## 🔮 Roadmap Futuro

### ✅ Concluído (2026-01-31)
- [x] **Melhorias de Segurança:** SecureFileManager, SafeSubprocessExecutor, Rate Limiting
- [x] **Estabilidade:** Retry decorators, Config centralizada, Asyncio puro
- [x] **Remoção de hardcoded paths:** Configuração via env vars

### Curto Prazo (1-2 semanas)
- [ ] Consolidar diretórios de trabalho (Assistente-Digital vs clawd)
- [ ] Adicionar testes unitários para novos módulos de segurança
- [ ] Implementar cache Redis para resultados de OCR
- [ ] Melhorar logging estruturado (JSON)

### Médio Prazo (1-2 meses)
- [ ] Migrar storage de SQLite para PostgreSQL
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Containerizar com Docker Compose
- [ ] Adicionar monitoramento (Prometheus/Grafana)
- [ ] Implementar streaming para downloads grandes

### Longo Prazo (3-6 meses)
- [ ] Orquestração com Kubernetes
- [ ] Horizontal scaling com múltiplas instâncias
- [ ] Message queue (RabbitMQ/Redis) para processamento assíncrono
- [ ] API REST para integrações externas
- [ ] Suporte a múltiplos usuários simultâneos

---

## 💡 Dicas para Novos Desenvolvedores

### 1. Comece Pequeno
Adicione uma ferramenta simples primeiro (ex: calculadora).

### 2. Use os Padrões
Todas as ferramentas seguem o mesmo padrão:
```python
async def minha_ferramenta(param: str) -> dict:
    try:
        resultado = fazer_algo(param)
        return {"success": True, "resultado": resultado}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 3. Teste Sempre
Execute `python tests/test_e2e.py` antes de commit.

### 4. Leia os Logs
Os logs são seus amigos: `tail -f bot.log`

### 5. Consulte a Documentação
Tudo está documentado em `docs/`.

---

## 📝 Nota sobre Contribuições

**Este é um projeto pessoal e privado** para uso do Bruno. Não aceita contribuições externas.

A documentação completa e os padrões de excelência são mantidos para:
- Facilitar manutenção futura
- Servir como referência pessoal
- Garantir qualidade do código
- Permitir evolução organizada

### Padrões Mantidos
- **Commits:** feat, fix, docs, style, refactor, test, chore
- **Código:** PEP 8
- **Docstrings:** Google style
- **Type hints:** Sempre que possível

---

## 📞 Contatos e Recursos

### Projeto
- **Bot:** @br_bruno_bot
- **User ID:** 6974901522
- **Diretório:** `/home/brunoadsba/Assistente-Digital/assistente`

### APIs
- **Groq:** https://console.groq.com
- **ElevenLabs:** https://elevenlabs.io
- **Telegram Bot API:** https://core.telegram.org/bots/api

### Documentação Externa
- **python-telegram-bot:** https://docs.python-telegram-bot.org
- **Groq Docs:** https://console.groq.com/docs
- **FFmpeg:** https://ffmpeg.org/documentation.html

---

## 🎓 Conceitos-Chave

### Tool Calling
O LLM decide automaticamente quais ferramentas usar baseado na mensagem do usuário.

### Agent Loop
Loop de até 5 iterações onde o LLM pode chamar múltiplas ferramentas sequencialmente.

### Registry Pattern
Todas as ferramentas são registradas em um registry central para fácil extensão.

### Async/Await
Todo o código é assíncrono para melhor performance.

---

## ✅ Checklist de Onboarding

- [ ] Leu README.md
- [ ] Leu MEMORY.md (este arquivo)
- [ ] Setup do ambiente concluído
- [ ] Teste E2E passou
- [ ] Executou bot localmente
- [ ] Testou no Telegram
- [ ] Leu ARCHITECTURE.md
- [ ] Entendeu o Agent loop
- [ ] Entendeu o Tool Registry
- [ ] Adicionou primeira ferramenta (opcional)
- [ ] Leu DEVELOPMENT.md
- [ ] Conhece o workflow de deploy

---

## 🎉 Bem-vindo ao Projeto!

Você agora tem todo o contexto necessário para trabalhar no Assistente Digital. 

**Próximos passos:**
1. Execute o teste E2E
2. Rode o bot localmente
3. Explore o código
4. Adicione sua primeira feature

**Dúvidas?** Consulte `docs/DOCS_INDEX.md` para navegação completa.

---

**Última atualização:** 2026-01-31  
**Versão:** 1.1  
**Mantenedor:** Bruno (user_id: 6974901522)

---

## 📝 Atualizações Recentes (2026-01-31)

### Melhorias de Segurança e Estabilidade Implementadas

**Componentes Criados:**

| Componente | Arquivo | Problema que Resolve |
|------------|---------|---------------------|
| **SecureFileManager** | `security/file_manager.py` | Arquivos temporários não deletados / Vazamento de memória |
| **SafeSubprocessExecutor** | `security/executor.py` | Command injection / Processos travados / Bloqueio do bot |
| **Retry Decorator** | `utils/retry.py` | Falhas temporárias de API / Instabilidade de rede |
| **Config Centralizada** | `config/settings.py` | Valores hardcoded espalhados / Dificuldade de manutenção |

#### 1. SecureFileManager
```python
from security import secure_files

# Uso: Cria arquivo temporário seguro com auto-cleanup
async with secure_files.temp_file(suffix='.mp4') as path:
    await process_video(path)
    # Arquivo é automaticamente deletado ao sair do contexto
```

**Funcionalidades:**
- Context manager garante limpeza automática (mesmo em caso de erro)
- Sanitização de filenames contra path traversal
- Validação real de MIME types usando python-magic
- Whitelist de extensões: mp4, mp3, jpg, png, xlsx, csv, etc
- Limite de tamanho: 50MB
- Diretório seguro: `/tmp/moltbot_secure` (criado automaticamente)

#### 2. SafeSubprocessExecutor
```python
from security import SafeSubprocessExecutor

# Uso: Executa comandos de forma assíncrona e segura
success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video_path), "-vframes", "1", str(frame_path)
])
if not success:
    logger.error(f"Erro: {stderr}")
```

**Funcionalidades:**
- Execução assíncrona (não bloqueia o bot)
- Whitelist de comandos: ffmpeg, ffprobe, tesseract, python
- Prevenção de command injection (bloqueia `;`, `&&`, `||`, etc)
- Timeout configurável (padrão: 30s)
- Tratamento especial para exit code 8 do FFmpeg (normal em Ubuntu)

#### 3. Retry Decorator
```python
from utils import retry_with_backoff

@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
async def call_groq_api():
    return await groq_client.chat.completions.create(...)
    # Se falhar, tenta automaticamente mais 2 vezes com delays: 1s → 2s → 4s
```

**Funcionalidades:**
- Exponential backoff (delays dobram a cada tentativa)
- Jitter aleatório para evitar thundering herd
- Configurável: max_retries, initial_delay, max_delay, exceções
- Suporte para funções async e sync

#### 4. Configuração Centralizada
```python
from config import config

# Uso: Acesse configurações de qualquer lugar
print(config.BASE_DIR)           # Via env MOLTBOT_DIR
print(config.TEMP_DIR)           # Via env MOLTBOT_TEMP
print(config.GROQ_MODEL_VISION)  # "meta-llama/llama-4-scout-17b-16e-instruct"
print(config.MAX_FILE_SIZE_MB)   # 50
```

**Funcionalidades:**
- Dataclass frozen (imutável)
- Valores via variáveis de ambiente ou defaults
- Paths configuráveis: BASE_DIR, TEMP_DIR, DATA_DIR
- Modelos de API, limites, rate limiting, segurança

#### 5. Rate Limiting no Agent
```python
# No handler de mensagens, passe o user_id:
response = await agent.run(user_message, history, user_id=update.effective_user.id)

# Se usuário exceder limite (20 mensagens/min), retorna:
# "⏱️ Muitas requisições. Aguarde um momento. Requisições restantes: X"
```

#### 6. Migração para Asyncio Puro
**Antes:**
```python
# Sistema de lembretes usando threading (problemático)
reminder_thread = threading.Thread(target=monitor_reminders, daemon=True)
reminder_thread.start()
```

**Depois:**
```python
# Sistema de lembretes usando asyncio (moderno)
reminder_task = asyncio.create_task(notifier.start_monitoring())
# Signal handling para graceful shutdown
# Cleanup adequado de recursos
```

**Arquivos Modificados:**
- `security/__init__.py` - Exporta novos módulos
- `utils/__init__.py` - Exporta retry decorators
- `config/__init__.py` - Exporta config settings
- `workspace/core/agent.py` - Adicionado rate limiting
- `bot_simple.py` - Migrado para asyncio puro (main() → async def main())

**Benefícios:**
- ✅ Zero arquivos temporários residuais (auto-cleanup)
- ✅ Proteção contra command injection
- ✅ Resiliência a falhas de API (retry automático)
- ✅ Configuração centralizada e flexível
- ✅ Rate limiting por usuário
- ✅ Sistema de lembretes moderno e estável

---

### Gerenciamento de Instâncias Resolvido

**Problema:**
- Múltiplas instâncias do bot causavam conflitos no Telegram API
- Respostas demoravam até 6 minutos (processamento: 3s)
- Erro: `Conflict: terminated by other getUpdates request`

**Causa Raiz:**
- clawdbot-gateway.service (instância automática via systemd)
- bot_simple.py (instância manual)
- Telegram API rejeita múltiplas conexões do mesmo token

**Solução Implementada:**
Scripts de gerenciamento em `/home/brunoadsba/clawd/moltbot-setup/scripts/`:
1. start_bot_safe.sh - Mata instâncias antigas e inicia apenas 1
2. stop_bot.sh - Para todas as instâncias de forma segura
3. healthcheck.sh - Monitora e alerta sobre múltiplas instâncias

**Serviços:**
- clawdbot-gateway.service foi desabilitado
- Bot deve rodar apenas via bot_simple.py com scripts de gerenciamento

**Documentação:**
- MEMORY.md atualizado com seção "Gerenciamento de Instâncias"
- docs/INSTANCE_MANAGEMENT.md criado (12KB, guia completo)
- README.md atualizado com alertas sobre múltiplas instâncias
- docs/DOCS_INDEX.md atualizado com nova documentação

**Como usar corretamente:**
```bash
cd /home/brunoadsba/clawd/moltbot-setup

# SEMPRE inicie assim (CORRETO)
./scripts/start_bot_safe.sh

# SEMPRE pare assim (CORRETO)
./scripts/stop_bot.sh

# SEMPRE verifique assim
./scripts/healthcheck.sh
```

**Resultado:** Apenas 1 instância rodando, entrega instantânea, sem conflitos.

**Para mais detalhes:** Veja [docs/INSTANCE_MANAGEMENT.md](/home/brunoadsba/clawd/moltbot-setup/docs/INSTANCE_MANAGEMENT.md)

---

## 📝 Notas sobre Testes

**Teste E2E:** Execute sempre dentro do venv311 para garantir que todas as dependências sejam encontradas:

```bash
cd /home/brunoadsba/clawd/moltbot-setup
source venv311/bin/activate
# Execute testes aqui
```

**Resultado esperado - Teste Rápido:** 9/10 testes (90%) ✅
(obs: yt_dlp pode falhar fora do venv, mas bot usa venv311 corretamente)

**Resultado esperado - Teste Completo (E2E):** 28/28 testes (100%) ✅

### Segfault em alguns ambientes

Em certos ambientes (ex.: WSL2, Python do sistema com extensões específicas), ao rodar `pytest` pode ocorrer **segmentation fault** (segfault) em:

- **Importação:** se `security/file_manager.py` chamar `logging.warning()` na carga do módulo (quando `python-magic` não está instalado). Contorno: o aviso na importação foi removido; o aviso só ocorre ao usar `validate_mime_type` sem python-magic.
- **Durante os testes:** chamadas a `logging.warning()` (ex.: em `rate_limiter`) ou uso do **event loop asyncio** (testes marcados com `@pytest.mark.asyncio`) podem disparar segfault por bug em extensão nativa ou no próprio ambiente.

**O que fazer:**

1. Rodar a suíte no **venv do projeto** (venv ou venv311), com `pip install -r requirements.txt` e `PYTHONPATH=src python -m pytest tests/ -v`.
2. Se o segfault persistir, rodar só testes síncronos para validar o mínimo:  
   `PYTHONPATH=src python -m pytest tests/test_e2e_simple.py::test_sqlite_store tests/test_security.py::test_sanitize_youtube_url_valid tests/test_security.py::test_sanitize_youtube_url_invalid tests/test_security.py::test_validate_path_allowed tests/test_security.py::test_validate_path_traversal_rejected -v`
3. Em último caso, executar a suíte em outro ambiente (outra máquina, CI ou container) para garantir os testes assíncronos e E2E completo.
