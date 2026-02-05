# 🛡️ PLANO DE IMPLEMENTAÇÃO - CORREÇÕES DE SEGURANÇA

> **⚠️ NOTA IMPORTANTE (2026-01-31):**
> Muitas das correções deste plano já foram **IMPLEMENTADAS na v1.1**!
>
> ✅ **Já Implementado:**
> - SecureFileManager (arquivos temporários seguros)
> - SafeSubprocessExecutor (execução segura de comandos)
> - Retry com backoff (resiliência a falhas)
> - Config centralizada (sem hardcoded paths)
> - Rate limiting no Agent (proteção por usuário)
> - Asyncio puro (sistema de lembretes modernizado)
>
> 📚 **Ver documentação atualizada em:**
> - `MEMORY.md` → Seção "Melhorias de Segurança e Estabilidade"
> - `ARCHITECTURE.md` → Seção "Módulos de Segurança (v1.1)"
> - `API_REFERENCE.md` → Seção "APIs Internas (Novas)"
>
> Este plano continua válido para auditoria e referência.

---

## ⚡ FASE 1: CONTENÇÃO IMEDIATA (EXECUTAR AGORA)

### 1. Parar o Bot
```bash
cd /home/brunoadsba/clawd/moltbot-setup
pkill -9 -f bot_simple.py
chmod 000 bot_simple.py  # Impede execução acidental
```

### 2. Proteger Credenciais
```bash
# Proteger .env
chmod 600 .env
chown brunoadsba:brunoadsba .env

# Verificar
ls -la .env
# Deve mostrar: -rw------- 1 brunoadsba brunoadsba
```

### 3. Rotacionar Tokens (URGENTE)
1. **Telegram Bot Token:**
   - Acesse @BotFather no Telegram
   - Envie `/mybots`
   - Selecione seu bot
   - Clique em "API Token"
   - Clique em "Revoke current token"
   - Copie o novo token
   - Atualize `.env`

2. **Groq API Key:**
   - Acesse https://console.groq.com/keys
   - Revogue a chave atual
   - Crie nova chave
   - Atualize `.env`

3. **Outras APIs:**
   - Repita para KIMI, OpenRouter, GLM

### 4. Auditoria de Logs
```bash
# Verificar acessos suspeitos
cd /home/brunoadsba/clawd/moltbot-setup
grep -i "read_file\|write_file\|list_directory" bot.log | tail -50
grep -i "error\|exception" bot.log | tail -50

# Verificar usuários que acessaram
grep "Mensagem recebida" bot.log | cut -d' ' -f8 | sort | uniq
```

---

## 🔒 FASE 2: IMPLEMENTAÇÃO DE CONTROLES (24-48h)

### 1. Configurar Autenticação

**Passo 1:** Descobrir seu User ID
```bash
# Inicie o bot temporariamente e envie uma mensagem
# O log mostrará seu user_id
```

**Passo 2:** Editar `security/auth.py`
```python
ALLOWED_USERS = [
    123456789,  # Substitua pelo seu user_id real
]

ADMIN_ID = 123456789  # Seu user_id
```

**Passo 3:** Aplicar autenticação no bot
```bash
# Editar bot_simple.py e adicionar @require_auth em todos os handlers
```

### 2. Implementar Filesystem Seguro

**Criar:** `workspace/tools/filesystem_secure.py`
```python
"""Filesystem Tools - Versão Segura"""
import os
import logging
from pathlib import Path
from security.sanitizer import validate_path

logger = logging.getLogger(__name__)

# Diretórios permitidos
ALLOWED_DIRS = [
    "/home/brunoadsba/clawd/moltbot-setup/workspace/data",
    "/tmp/moltbot"
]

# Extensões permitidas
ALLOWED_READ_EXTS = {'.txt', '.md', '.json', '.py', '.js', '.html', '.css'}
ALLOWED_WRITE_EXTS = {'.txt', '.md', '.json'}

# Tamanho máximo
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def read_file(path: str) -> dict:
    """Lê arquivo com validações de segurança"""
    # Valida path
    valid, result = validate_path(path, ALLOWED_DIRS)
    if not valid:
        logger.warning(f"Path inválido: {path} - {result}")
        return {"success": False, "error": result}
    
    # Verifica extensão
    ext = Path(result).suffix.lower()
    if ext not in ALLOWED_READ_EXTS:
        return {"success": False, "error": f"Extensão não permitida: {ext}"}
    
    # Verifica tamanho
    try:
        size = os.path.getsize(result)
        if size > MAX_FILE_SIZE:
            return {"success": False, "error": f"Arquivo muito grande: {size/1024/1024:.1f}MB"}
    except Exception as e:
        return {"success": False, "error": f"Erro ao verificar arquivo: {e}"}
    
    # Lê arquivo
    try:
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Arquivo lido: {result}")
        return {"success": True, "content": content, "path": result}
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return {"success": False, "error": str(e)}

async def write_file(path: str, content: str) -> dict:
    """Escreve arquivo com validações"""
    valid, result = validate_path(path, ALLOWED_DIRS)
    if not valid:
        logger.warning(f"Path inválido: {path} - {result}")
        return {"success": False, "error": result}
    
    ext = Path(result).suffix.lower()
    if ext not in ALLOWED_WRITE_EXTS:
        return {"success": False, "error": f"Extensão não permitida: {ext}"}
    
    if len(content) > MAX_FILE_SIZE:
        return {"success": False, "error": "Conteúdo muito grande"}
    
    try:
        os.makedirs(os.path.dirname(result), exist_ok=True)
        with open(result, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Arquivo escrito: {result}")
        return {"success": True, "message": f"Arquivo salvo em {result}"}
    except Exception as e:
        logger.error(f"Erro ao escrever arquivo: {e}")
        return {"success": False, "error": str(e)}

async def list_directory(path: str) -> dict:
    """Lista diretório com validações"""
    valid, result = validate_path(path, ALLOWED_DIRS)
    if not valid:
        return {"success": False, "error": result}
    
    try:
        items = os.listdir(result)
        files = [i for i in items if os.path.isfile(os.path.join(result, i))]
        directories = [i for i in items if os.path.isdir(os.path.join(result, i))]
        return {
            "success": True,
            "path": result,
            "files": sorted(files),
            "directories": sorted(directories),
            "total": len(items)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 3. Proteger YouTube Analyzer

**Editar:** `workspace/tools/youtube_analyzer.py`

Adicionar no início:
```python
from security.sanitizer import sanitize_youtube_url, sanitize_filename, safe_subprocess
from security.media_validator import validate_video
```

Substituir `_download_video`:
```python
def _download_video(self, youtube_url: str, output_path: str) -> bool:
    """Baixa vídeo do YouTube com validações"""
    try:
        # Valida URL
        valid, clean_url = sanitize_youtube_url(youtube_url)
        if not valid:
            logger.error(f"URL inválida: {youtube_url}")
            return False
        
        # Sanitiza output path
        safe_output = sanitize_filename(os.path.basename(output_path))
        safe_path = os.path.join(os.path.dirname(output_path), safe_output)
        
        # Executa yt-dlp com proteções
        cmd = ["yt-dlp", "-f", "worst", "-o", safe_path, clean_url]
        safe_subprocess(cmd, timeout=120, check=True)
        
        # Valida arquivo baixado
        valid, msg = validate_video(safe_path)
        if not valid:
            os.unlink(safe_path)
            logger.error(f"Vídeo inválido: {msg}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar vídeo: {e}")
        return False
```

Substituir `_extract_frames`:
```python
def _extract_frames(self, video_path: str, output_dir: str, fps: float = 0.2) -> list:
    """Extrai frames com proteções"""
    try:
        frame_pattern = os.path.join(output_dir, "frame_%03d.jpg")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps={fps}",
            "-q:v", "5",
            frame_pattern
        ]
        safe_subprocess(cmd, timeout=60, check=True)
        
        frames = sorted([
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith("frame_") and f.endswith(".jpg")
        ])
        return frames[:10]  # Máximo 10 frames
    except Exception as e:
        logger.error(f"Erro ao extrair frames: {e}")
        return []
```

### 4. Atualizar bot_simple.py

**Adicionar no início:**
```python
from security.auth import require_auth
from security.rate_limiter import message_limiter, media_limiter, youtube_limiter
```

**Aplicar decorators:**
```python
@require_auth
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limiting
    if not message_limiter.is_allowed(user_id):
        await update.message.reply_text(
            "⏱️ Muitas requisições. Aguarde um momento."
        )
        return
    
    # ... resto do código
```

**Aplicar em TODOS os handlers:**
- `handle_message`
- `handle_photo`
- `handle_video`
- `handle_voice`
- `handle_audio`

### 5. Criar Diretórios Seguros
```bash
mkdir -p /home/brunoadsba/clawd/moltbot-setup/workspace/data
mkdir -p /tmp/moltbot
chmod 700 /tmp/moltbot
```

---

## 🧪 FASE 3: TESTES (48-72h)

### 1. Testes de Autenticação
```
1. Envie mensagem de usuário não autorizado
   Esperado: "❌ Acesso negado"

2. Adicione seu user_id em ALLOWED_USERS
   Esperado: Bot responde normalmente
```

### 2. Testes de Path Traversal
```
Envie: read_file("../../../../etc/passwd")
Esperado: "Path fora de diretórios permitidos"

Envie: read_file("/home/brunoadsba/clawd/moltbot-setup/.env")
Esperado: "Path fora de diretórios permitidos"
```

### 3. Testes de Rate Limiting
```
Envie 25 mensagens rapidamente
Esperado: Após 20, receber "Muitas requisições"
```

### 4. Testes de YouTube
```
Envie: https://youtube.com/watch?v=test; whoami
Esperado: "URL do YouTube inválida"

Envie: https://youtube.com/watch?v=dQw4w9WgXcQ
Esperado: Análise normal do vídeo
```

---

## 📊 FASE 4: MONITORAMENTO (Contínuo)

### 1. Verificar Logs Diariamente
```bash
tail -100 bot.log | grep -i "warning\|error\|denied"
```

### 2. Monitorar Uso de Recursos
```bash
ps aux | grep bot_simple
df -h /tmp
```

### 3. Atualizar Dependências Mensalmente
```bash
pip list --outdated
pip install --upgrade yt-dlp python-telegram-bot
```

---

## ✅ CHECKLIST FINAL

### Antes de Reativar o Bot
- [x] ✅ **Módulos de segurança v1.1 implementados (2026-01-31)**
  - [x] SecureFileManager (auto-cleanup de arquivos)
  - [x] SafeSubprocessExecutor (comandos seguros)
  - [x] Retry com backoff (resiliência)
  - [x] Config centralizada (env vars)
  - [x] Rate limiting no Agent (por usuário)
- [ ] Todas as credenciais rotacionadas
- [ ] .env com permissões 600
- [ ] ALLOWED_USERS configurado
- [ ] Autenticação aplicada em todos os handlers
- [ ] Filesystem seguro implementado (custom)
- [ ] YouTube analyzer protegido
- [ ] Diretórios seguros criados
- [ ] Testes de segurança executados
- [ ] Logs auditados

### Após Reativar
- [ ] Testar com usuário autorizado
- [ ] Testar com usuário não autorizado
- [ ] Verificar logs por 24h
- [ ] Monitorar uso de recursos
- [ ] Documentar incidentes

---

## 🆘 EM CASO DE INCIDENTE

### Se Detectar Acesso Não Autorizado:
1. Parar bot imediatamente: `pkill -9 -f bot_simple.py`
2. Rotacionar TODAS as credenciais
3. Auditar logs: `grep "user_id" bot.log`
4. Verificar arquivos modificados: `find . -mtime -1`
5. Restaurar de backup se necessário

### Contatos de Emergência:
- Admin: [SEU TELEGRAM]
- Suporte: [EMAIL/TELEFONE]

---

**IMPORTANTE:** Não pule nenhuma etapa. Segurança é um processo, não um produto.
