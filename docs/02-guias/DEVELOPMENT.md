# 👨‍💻 Guia de Desenvolvimento - Assistente Digital

Guia completo para desenvolvedores que desejam contribuir ou estender o Assistente Digital.

## Índice

1. [Setup do Ambiente](#setup-do-ambiente)
2. [Estrutura do Código](#estrutura-do-código)
3. [Adicionar Nova Funcionalidade](#adicionar-nova-funcionalidade)
4. [Testes](#testes)
5. [Deploy](#deploy)
6. [Boas Práticas](#boas-práticas)

---

## Setup do Ambiente

### Requisitos

- Python 3.12+
- ffmpeg
- tesseract-ocr
- Git

### Instalação

```bash
# 1. Clone o repositório e entre na pasta
cd assistente

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
# Edite .env: TELEGRAM_TOKEN, GROQ_API_KEY (obrigatórios). Opcional: NVIDIA_API_KEY (fallback em 429). Sem NVIDIA, em 429 o bot responde a partir da memória RAG (ex.: NR-29), se houver conteúdo em src/dados/memory.json.

# 5. Teste a instalação
PYTHONPATH=src python -m pytest tests/ -v
```

### Dependências Principais

```txt
python-telegram-bot==20.7  # Bot do Telegram
groq==0.4.1                # LLM, Vision, Whisper
yt-dlp==2024.12.23         # Download do YouTube
requests==2.31.0           # HTTP requests
chromadb==0.4.22           # Vector database (RAG)
pandas                     # Análise de dados
python-docx                # Word documents
pytesseract                # OCR
matplotlib                 # Gráficos
elevenlabs                 # Text-to-Speech
```

---

## Estrutura do Código (Modularizada)

O código está em `src/`. Na raiz ficam `docs/`, `tests/` e `scripts/`.

```
src/
├── bot_simple.py              # 🎯 Setup e registro (160 linhas)
│   ├── main()                 # Inicialização e ciclo de vida
│   └── Factories              # Injeção de dependências nos handlers
│
├── agent_setup.py             # Setup do agente e utilitários
│   ├── create_agent_no_sandbox()  # Cria agente com todas as ferramentas
│   └── text_to_speech()       # Conversão texto → áudio (ElevenLabs)
│
├── commands.py                # Comandos do bot
│   ├── start()                # /start
│   ├── make_clear_handler()   # /clear (factory)
│   └── make_status_handler()  # /status (factory)
│
├── handlers/                  # Handlers por tipo de mídia
│   ├── __init__.py            # Exports
│   ├── message.py             # Mensagens de texto, YouTube, TTS
│   ├── photo.py               # Análise de imagens
│   ├── video.py               # Análise de vídeos
│   ├── voice.py               # Transcrição de voz
│   ├── audio.py               # Transcrição de áudio
│   └── document.py            # Excel, CSV, Word, Markdown, OCR
│
├── workspace/
│   ├── core/
│   │   ├── agent.py           # 🤖 Agente autônomo
│   │   ├── tools.py           # 🔧 Registry de ferramentas
│   │   └── sandbox.py         # Sandbox (legado, não usado)
│   ├── tools/                 # web_search, rag_tools, filesystem, code_tools, youtube_analyzer, reminder_notifier, extra_tools
│   ├── storage/               # sqlite_store.py
│   ├── memory/                # memory_manager, fact_store
│   ├── runs/                  # RunManager
│   └── scripts/               # rag_manager, web_search, task_executor, notebooklm_query
│
├── security/                  # auth, rate_limiter, sanitizer, file_manager, executor, media_validator
├── config/                    # settings.py (config centralizada)
└── utils/                     # retry.py
```

**Benefícios da modularização:**
- ✅ Código organizado por responsabilidade
- ✅ Manutenção mais fácil (cada handler em seu arquivo)
- ✅ Testes isolados por handler
- ✅ Reutilização de código (factories para injeção de dependências)
- ✅ Escalabilidade (adicionar novos handlers sem alterar arquivo principal)

---

## Adicionar Nova Funcionalidade

### Exemplo: Ferramenta de Tradução

#### 1. Criar o Arquivo da Ferramenta

```python
# src/workspace/tools/translator.py

import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

async def translate_text(text: str, target_lang: str = "pt") -> dict:
    """Traduz texto para outro idioma"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        logger.info(f"Texto traduzido para {target_lang}")
        
        return {
            "success": True,
            "original": text,
            "translated": translated,
            "target_language": target_lang
        }
    except Exception as e:
        logger.error(f"Erro na tradução: {e}")
        return {"success": False, "error": str(e)}

# Schema para tool calling
TRANSLATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "translate_text",
        "description": "Traduz texto para outro idioma",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto a ser traduzido"
                },
                "target_lang": {
                    "type": "string",
                    "description": "Idioma de destino (pt, en, es, fr, etc)",
                    "default": "pt"
                }
            },
            "required": ["text"]
        }
    }
}
```

#### 2. Registrar no Bot

```python
# src/agent_setup.py

from workspace.tools.translator import translate_text, TRANSLATE_SCHEMA

def create_agent_no_sandbox():
    registry = ToolRegistry()
    
    # Ferramentas existentes
    registry.register("web_search", web_search, WEB_SEARCH_SCHEMA)
    # ...
    
    # Nova ferramenta
    registry.register("translate_text", translate_text, TRANSLATE_SCHEMA)
    
    return Agent(registry)
```

**Nota:** Com a modularização, o registro de ferramentas está em `src/agent_setup.py`, não mais em `bot_simple.py`.

#### 3. Adicionar Dependência

```bash
# requirements.txt
deep-translator==1.11.4
```

```bash
pip install deep-translator
```

#### 4. Testar

```
Você: Traduza "Hello World" para português
Bot: [usa tool: translate_text("Hello World", "pt")]
     Tradução: "Olá Mundo"
```

---

### Exemplo: Adicionar Novo Handler de Mídia

Com a estrutura modularizada, adicionar um novo handler é simples:

#### 1. Criar o Handler

```python
# src/handlers/sticker.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from security.auth import require_auth
from workspace.storage.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


@require_auth
async def handle_sticker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    store: SQLiteStore,
):
    """Handler para stickers"""
    logger.info("Sticker recebido")
    
    await update.message.chat.send_action("typing")
    
    try:
        sticker = update.message.sticker
        emoji = sticker.emoji or "😊"
        
        # Sua lógica aqui
        response = f"Sticker recebido! {emoji}"
        
        await update.message.reply_text(response)
        store.add_message("user", f"[STICKER] {emoji}")
        store.add_message("assistant", response)
        
    except Exception as e:
        logger.error(f"Erro ao processar sticker: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro ao processar o sticker. Tente novamente.")
```

#### 2. Exportar no __init__.py

```python
# src/handlers/__init__.py

from .sticker import handle_sticker

__all__ = [
    # ... handlers existentes
    "handle_sticker",
]
```

#### 3. Registrar no bot_simple.py

```python
# src/bot_simple.py

from handlers import handle_sticker

def make_sticker_handler(store: SQLiteStore):
    """Factory para criar handler de sticker com dependências injetadas"""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_sticker(update, context, store)
    return handler

# No main():
app.add_handler(MessageHandler(filters.STICKER, make_sticker_handler(store)))
```

---

**Nota:** O exemplo acima mostra a estrutura modularizada atual. A estrutura antiga (tudo em `bot_simple.py`) foi refatorada para melhor organização e manutenibilidade.

---

## Testes

### Teste E2E

```bash
cd assistente   # raiz do repositório
PYTHONPATH=src python -m pytest tests/ -v
```

### Teste Manual

```bash
# Na raiz do repo: ative o venv e inicie o bot
source venv/bin/activate
PYTHONPATH=src python src/bot_simple.py
```

### Teste de Ferramenta Específica

```python
# test_translator.py

import asyncio
from workspace.tools.translator import translate_text

async def test():
    result = await translate_text("Hello World", "pt")
    print(result)
    assert result["success"] == True
    assert "Olá" in result["translated"]

asyncio.run(test())
```

### Teste de Handler

```python
# test_handler.py

from telegram import Update, Message, User, Chat
from bot_simple import handle_message

# Mock update
update = Update(
    update_id=1,
    message=Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=6974901522, type="private"),
        from_user=User(id=6974901522, is_bot=False, first_name="Bruno"),
        text="Olá"
    )
)

# Testa handler
await handle_message(update, None)
```

---

## Deploy

### Desenvolvimento

```bash
# 1. Editar código
# Edite o código em src/ (ex.: src/bot_simple.py)

# 2. Testar
PYTHONPATH=src python -m pytest tests/ -v

# 3. Testar manualmente
PYTHONPATH=src python src/bot_simple.py
```

### Produção

```bash
# 1. Parar bot atual
pkill -f "python.*bot_simple"

# 2. Copiar alterações (src/, scripts/, .env) para o servidor de deploy

# 3. Iniciar nova versão (no servidor)
# ./scripts/start.sh ou ./start_bot.sh, conforme disponível

# 4. Verificar logs
tail -f bot.log
```

### Docker (Futuro)

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-por \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Inicia bot
ENV PYTHONPATH=/app/src
CMD ["python", "src/bot_simple.py"]
```

```bash
# Build
docker build -t assistente-digital .

# Run
docker run -d \
  --name assistente \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  assistente-digital
```

---

## Boas Práticas

### 1. Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info
logger.info("Operação iniciada")

# Warning
logger.warning("Situação incomum detectada")

# Error
logger.error(f"Erro ao processar: {e}", exc_info=True)
```

### 2. Tratamento de Erros

```python
try:
    resultado = operacao_perigosa()
    return {"success": True, "resultado": resultado}
except ValueError as e:
    logger.error(f"Valor inválido: {e}")
    return {"success": False, "error": "Valor inválido"}
except Exception as e:
    logger.error(f"Erro inesperado: {e}", exc_info=True)
    return {"success": False, "error": str(e)}
```

### 3. Async/Await

```python
# ✅ Correto
async def minha_funcao():
    resultado = await operacao_async()
    return resultado

# ❌ Errado
def minha_funcao():
    resultado = operacao_async()  # Retorna coroutine, não resultado
    return resultado
```

### 4. Type Hints

```python
from typing import Dict, List, Optional

async def processar(
    texto: str,
    opcoes: Optional[Dict[str, any]] = None
) -> Dict[str, any]:
    """Processa texto com opções"""
    pass
```

### 5. Docstrings

```python
async def minha_funcao(parametro: str) -> dict:
    """
    Descrição breve da função.
    
    Args:
        parametro: Descrição do parâmetro
    
    Returns:
        Dict com 'success' e 'resultado' ou 'error'
    
    Raises:
        ValueError: Se parâmetro for inválido
    
    Example:
        >>> result = await minha_funcao("teste")
        >>> print(result["success"])
        True
    """
    pass
```

### 6. Constantes

```python
# No topo do arquivo
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".txt", ".md", ".json"]
DEFAULT_TIMEOUT = 30

# Uso
if size > MAX_FILE_SIZE:
    return {"success": False, "error": "Arquivo muito grande"}
```

### 7. Validação de Inputs

```python
def validar_parametros(texto: str, limite: int) -> Optional[str]:
    """Valida parâmetros e retorna erro se inválido"""
    if not texto or len(texto) == 0:
        return "Texto não pode ser vazio"
    
    if limite < 1 or limite > 100:
        return "Limite deve estar entre 1 e 100"
    
    return None  # Válido

# Uso
erro = validar_parametros(texto, limite)
if erro:
    return {"success": False, "error": erro}
```

### 8. Timeouts

```python
import subprocess

# Subprocess
result = subprocess.run(
    cmd,
    timeout=30,
    capture_output=True,
    check=True
)

# Requests
response = requests.get(url, timeout=10)

# Async
await asyncio.wait_for(operacao(), timeout=30)
```

---

## 🛡️ Desenvolvimento Seguro (v1.1)

### Módulos de Segurança Disponíveis

O projeto inclui módulos de segurança que devem ser usados ao desenvolver novas funcionalidades:

#### 1. SecureFileManager

**Quando usar:** Sempre que precisar criar arquivos temporários.

```python
from security import secure_files

# ❌ Antes (inseguro)
import tempfile
temp_path = f"/tmp/meu_arquivo_{id}.mp4"
# Arquivo pode não ser deletado em caso de erro

# ✅ Depois (seguro)
async with secure_files.temp_file(suffix='.mp4') as temp_path:
    await download_video(temp_path)
    await process_video(temp_path)
    # Arquivo automaticamente deletado ao sair do contexto
```

**Benefícios:**
- Auto-cleanup garantido (mesmo em caso de erro)
- Sanitização de filenames contra path traversal
- Validação real de MIME types
- Diretório seguro com permissões restritas

---

#### 2. SafeSubprocessExecutor

**Quando usar:** Sempre que precisar executar comandos externos (ffmpeg, etc).

```python
from security import SafeSubprocessExecutor

# ❌ Antes (inseguro)
import subprocess
subprocess.run(["ffmpeg", "-i", user_input, "output.mp4"], shell=True)
# Vulnerável a command injection

# ✅ Depois (seguro)
success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video_path), "-vframes", "1", str(frame_path)
])

if not success:
    logger.error(f"Erro: {stderr}")
```

**Benefícios:**
- Whitelist de comandos permitidos
- Bloqueio de command injection
- Execução assíncrona (não bloqueia o bot)
- Timeout automático (30s padrão)

---

#### 3. Retry Decorator

**Quando usar:** Ao fazer chamadas a APIs externas.

```python
from utils import retry_with_backoff

# ❌ Antes (sem resiliência)
async def call_api():
    return await groq_client.chat.completions.create(...)
# Falha imediatamente se API estiver instável

# ✅ Depois (com retry)
@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
async def call_api():
    return await groq_client.chat.completions.create(...)
# Tenta novamente automaticamente com backoff
```

**Benefícios:**
- Exponential backoff (1s → 2s → 4s)
- Jitter aleatório para evitar thundering herd
- Configurável: max_retries, delays, exceções

---

#### 4. Configuração Centralizada

**Quando usar:** Para acessar configurações do sistema.

```python
from config import config

# ❌ Antes (hardcoded)
BASE_DIR = os.getenv("BASE_DIR", "/app")  # ou path do deploy
TEMP_DIR = "/tmp"

# ✅ Depois (configurável)
BASE_DIR = config.BASE_DIR      # Via env MOLTBOT_DIR
TEMP_DIR = config.TEMP_DIR      # Via env MOLTBOT_TEMP
MAX_SIZE = config.MAX_FILE_SIZE_MB  # 50
```

**Variáveis de Ambiente:**
```bash
# Diretório de execução (onde está src/ e .env)
# ASSISTENTE_DIR=/caminho/para/assistente
MOLTBOT_TEMP=/tmp/moltbot_secure
ALLOWED_USERS=6974901522,123456789
```

---

### Checklist de Segurança para Novas Funcionalidades

- [ ] Usar `secure_files.temp_file()` para arquivos temporários
- [ ] Usar `SafeSubprocessExecutor.run()` para comandos externos
- [ ] Adicionar `@retry_with_backoff` para chamadas de API
- [ ] Usar `config.settings` ao invés de hardcoded paths
- [ ] Validar todos os inputs do usuário
- [ ] Usar timeouts em operações externas
- [ ] Tratar exceções apropriadamente
- [ ] Adicionar logging para operações importantes
- [ ] Testar em ambiente de desenvolvimento antes de deploy

---

## Debugging

### Logs

```bash
# Ver logs em tempo real
tail -f bot.log   # na pasta onde o bot é executado

# Buscar erros
grep -i error bot.log

# Buscar por user_id
grep "user_id=6974901522" bot.log

# Últimas 100 linhas
tail -100 bot.log
```

### Python Debugger

```python
# Adicionar breakpoint
import pdb; pdb.set_trace()

# Ou (Python 3.7+)
breakpoint()
```

### Print Debugging

```python
print(f"DEBUG: variavel = {variavel}")
print(f"DEBUG: type = {type(variavel)}")
print(f"DEBUG: dir = {dir(variavel)}")
```

---

## Contribuindo

### Workflow

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie branch** para feature: `git checkout -b feature/nova-funcionalidade`
4. **Desenvolva** e teste
5. **Commit**: `git commit -m "feat: adiciona nova funcionalidade"`
6. **Push**: `git push origin feature/nova-funcionalidade`
7. **Pull Request** para branch main

### Convenções de Commit

```
feat: Nova funcionalidade
fix: Correção de bug
docs: Documentação
style: Formatação
refactor: Refatoração
test: Testes
chore: Manutenção
```

### Code Review

- ✅ Código limpo e legível
- ✅ Documentação atualizada
- ✅ Testes passando
- ✅ Sem warnings
- ✅ Segue boas práticas

---

## Recursos

### Documentação
- `README.md` - Início rápido
- `ARCHITECTURE.md` - Arquitetura
- `FEATURES.md` - Funcionalidades
- `API_REFERENCE.md` - APIs
- `TOOLS_REFERENCE.md` - Ferramentas

### Links Úteis
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Groq Docs:** https://console.groq.com/docs
- **Python Telegram Bot:** https://docs.python-telegram-bot.org

### Comunidade
- **Issues:** GitHub Issues
- **Discussões:** GitHub Discussions

---

## FAQ

**Q: Como adicionar suporte a novo tipo de arquivo?**  
A: Adicione handler em `handle_document()` com lógica específica.

**Q: Como melhorar a análise de vídeos?**  
A: Aumente número de frames em `youtube_analyzer.py` ou use modelo melhor.

**Q: Como adicionar nova API externa?**  
A: Crie ferramenta em `src/workspace/tools/`, adicione schema e registre no bot (create_agent_no_sandbox).

**Q: Como debugar tool calling?**  
A: Adicione logs em `Agent.run()` para ver quais tools são chamadas.

**Q: Como otimizar performance?**  
A: Use cache, reduza qualidade de mídia, limite número de iterações.

---

## Próximos Passos

- [ ] Implementar testes unitários
- [ ] Adicionar CI/CD
- [ ] Containerizar com Docker
- [ ] Implementar cache Redis
- [ ] Migrar para PostgreSQL
- [ ] Adicionar monitoramento (Prometheus)
- [ ] Implementar rate limiting avançado
- [ ] Adicionar mais ferramentas

---

**Happy Coding!** 🚀
