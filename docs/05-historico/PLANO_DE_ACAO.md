# 🎯 Plano de Ação - Implementação das Melhorias

**Plano estruturado para implementar as melhorias do Assistente Digital**
**Baseado em:** [ANALISE_CRITICA.md](ANALISE_CRITICA.md)

---

## 📋 Executive Summary

Este plano detalha a implementação de melhorias no Assistente Digital, priorizando:
1. **Correções urgentes** que afetam usabilidade e opensource
2. **Melhorias importantes** para zero custo e manutenibilidade
3. **Funcionalidades desejáveis** para automação pessoal

**Investimento total estimado:** 5-7 dias de trabalho distribuídos em 3 meses
**Resultado:** Sistema 100% opensource, self-contained, zero custo operacional

---

## 🚨 FASE 1: URGENTE (Semana 1)

**Objetivo:** Corrigir problemas críticos que impactam usabilidade e filosofia opensource

### Dia 1-2: Consolidação de Diretórios

**Tarefa:** Unificar `/Assistente-Digital/assistente/` e `/clawd/moltbot-setup/` em um único diretório

**Estrutura proposta:**
```
/home/brunoadsba/assistente/                    # NOVO diretório único
├── src/                                        # Código fonte (atual workspace/)
│   ├── bot/
│   ├── workspace/
│   ├── security/
│   ├── utils/
│   └── config/
├── venv/                                       # Ambiente virtual
├── data/                                       # SQLite, JSONs persistentes
│   ├── moltbot.db
│   ├── reminders.json
│   └── memory/
├── tmp/                                        # Arquivos temporários
├── scripts/                                    # Start/stop/healthcheck
├── tests/                                      # Testes
├── docs/                                       # Documentação
├── .env                                        # Configurações
├── .env.example                                # Exemplo de config
├── requirements.txt                            # Dependências
└── README.md                                   # Início rápido
```

**Passos:**
1. Criar estrutura de diretórios nova
2. Copiar código fonte de `workspace/` → `src/`
3. Copiar `.env` de `/clawd/moltbot-setup/`
4. Copiar venv (ou criar novo e instalar dependências)
5. Atualizar todos os paths hardcoded
6. Testar execução
7. Atualizar documentação

**Sucesso:**
- Bot inicia com `./scripts/start.sh` no novo diretório
- Testes passam: `python tests/test_bot_completo.py`
- Zero referências aos diretórios antigos

**Dependências:** Nenhuma (pode ser primeira tarefa)

---

### Dia 3-4: Migração de Scripts Externos

**Tarefa:** Mover scripts de `~/.clawdbot/` para dentro do projeto

**Scripts a migrar:**
- `~/.clawdbot/skills/custom/moltbot-web-search/scripts/web_search_ddg.py`
- `~/.clawdbot/skills/custom/moltbot-rag/scripts/rag_simple.py`

**Estrutura nova:**
```
src/workspace/tools/impl/
├── __init__.py
├── web_search_ddg.py          # Migrado de ~/.clawdbot/
└── rag_simple.py              # Migrado de ~/.clawdbot/
```

**Refatoração:**
```python
# ANTES (workspace/tools/web_search.py)
result = subprocess.run(
    ["python3", os.path.expanduser("~/.clawdbot/skills/custom/moltbot-web-search/scripts/web_search_ddg.py"), query],
    ...
)

# DEPOIS
from workspace.tools.impl.web_search_ddg import search_ddg
result = search_ddg(query, max_results=max_results)
```

**Passos:**
1. Copiar scripts para `src/workspace/tools/impl/`
2. Refatorar para funções Python puras (sem subprocess)
3. Atualizar imports em web_search.py e rag_tools.py
4. Remover dependências de subprocess
5. Testar funcionalidades
6. Documentar novo local

**Sucesso:**
- Web search funciona sem chamar subprocess externo
- RAG funciona sem chamar subprocess externo
- Scripts estão versionados no git
- Projeto é 100% self-contained

**Dependências:** Fase 1.1 (consolidação de diretórios)

---

### Dia 5: Fix Lembretes em /tmp

**Tarefa:** Mover storage de lembretes de `/tmp/` para diretório persistente

**Mudança:**
```python
# ANTES (workspace/tools/extra_tools.py)
reminders_file = '/tmp/moltbot_reminders.json'

# DEPOIS
from pathlib import Path
DATA_DIR = Path.home() / ".assistente" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
reminders_file = DATA_DIR / "reminders.json"
```

**Passos:**
1. Identificar todos os usos de `/tmp/moltbot_reminders.json`
2. Criar constante DATA_DIR em config/settings.py
3. Atualizar todas as referências
4. Criar diretório se não existir
5. Testar criação e persistência de lembretes
6. Verificar se dados sobrevivem reboot

**Sucesso:**
- Lembretes persistem após reboot
- Diretório `~/.assistente/data/` criado automaticamente
- Zero referências a /tmp para dados persistentes

**Dependências:** Fase 1.1 (consolidação de diretórios)

---

### Dia 6-7: Documentação e Testes

**Tarefa:** Atualizar documentação e validar todas as mudanças

**Atividades:**
1. Atualizar README.md com novo estrutura
2. Atualizar MEMORY.md com paths novos
3. Atualizar docs/ARCHITECTURE.md se necessário
4. Executar todos os testes: `python tests/test_bot_completo.py`
5. Testar E2E: `python tests/test_e2e_simple.py`
6. Criar script de migração (opcional)

**Sucesso:**
- Todos os testes passam
- Documentação reflete nova estrutura
- Bot funciona normalmente no novo diretório

**Dependências:** Todas as tarefas da Fase 1

---

## ⚠️ FASE 2: IMPORTANTE (Semanas 2-4)

**Objetivo:** Melhorar manutenibilidade e eliminar custos/limitações

### Semana 2: Refatoração de Código

**Tarefa:** Modularizar bot_simple.py (757 linhas)

**Estrutura nova:**
```
src/bot/
├── __init__.py
├── main.py                    # Entry point (~100 linhas)
├── config.py                  # Configurações do bot
├── handlers/
│   ├── __init__.py
│   ├── message.py            # handle_message (~150 linhas)
│   ├── media.py              # handle_photo, video, audio, voice (~200 linhas)
│   └── document.py           # handle_document (~150 linhas)
├── utils.py                   # Funções auxiliares
└── middleware/                # Decoradores (@require_auth, rate limiting)
    ├── __init__.py
    └── auth.py
```

**Passos:**
1. Criar estrutura de diretórios
2. Extrair handlers para arquivos separados
3. Mover lógica de inicialização para main.py
4. Extrair funções auxiliares para utils.py
5. Atualizar imports
6. Testar cada handler isoladamente
7. Testar integração completa

**Sucesso:**
- Cada arquivo < 200 linhas
- Responsabilidade única por módulo
- Testes passam
- Bot funciona normalmente

**Dependências:** Fase 1 completa

---

### Semana 3: Substituição de APIs (Parte 1)

**Tarefa 1:** Substituir ElevenLabs por Piper TTS (Text-to-Speech local)

**Implementação:**
```python
# NOVO: workspace/tools/piper_tts.py
import subprocess
from pathlib import Path

async def text_to_speech(text: str, output_path: Path) -> dict:
    """Usa Piper TTS local"""
    model = Path.home() / ".piper" / "pt_BR-faber-medium.onnx"
    
    process = await asyncio.create_subprocess_exec(
        "piper", "--model", str(model), "--output_file", str(output_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate(text.encode())
    
    if process.returncode == 0:
        return {"success": True, "audio_path": str(output_path)}
    else:
        return {"success": False, "error": stderr.decode()}
```

**Instalação:**
```bash
# Instalar Piper
pip install piper-tts

# Baixar modelo PT-BR
mkdir -p ~/.piper
cd ~/.piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR-faber-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR-faber-medium.onnx.json
```

**Sucesso:**
- Piper TTS instalado e funcionando
- ElevenLabs removido
- Qualidade de voz aceitável
- Zero custo, ilimitado

---

**Tarefa 2:** Substituir OpenWeather por Open-Meteo

**Implementação:**
```python
# NOVO: workspace/tools/weather.py
import aiohttp

async def get_weather(city: str) -> dict:
    """Usa Open-Meteo (API grátis, sem key)"""
    # Geocoding
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        ) as resp:
            data = await resp.json()
            lat = data['results'][0]['latitude']
            lon = data['results'][0]['longitude']
        
        # Weather
        async with session.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        ) as resp:
            weather = await resp.json()
            
    return {
        "success": True,
        "weather": {
            "cidade": city,
            "temperatura": f"{weather['current_weather']['temperature']}°C",
            "descricao": weather_codes[weather['current_weather']['weathercode']]
        }
    }
```

**Sucesso:**
- Open-Meteo funciona sem API key
- Dados de clima retornados corretamente
- OpenWeather removido
- Zero custo, ilimitado

---

### Semana 4: Substituição de APIs (Parte 2) + Storage

**Tarefa 1:** Substituir NewsAPI por RSS feeds

**Implementação:**
```python
# NOVO: workspace/tools/news_rss.py
import feedparser

FEEDS = {
    "tecnologia": "https://g1.globo.com/rss/g1/tecnologia/",
    "brasil": "https://g1.globo.com/rss/g1/brasil/",
    # Adicionar mais feeds
}

async def get_news_rss(topic: str = "brasil", limit: int = 5) -> dict:
    """Busca notícias via RSS (zero custo)"""
    feed_url = FEEDS.get(topic, FEEDS["brasil"])
    feed = feedparser.parse(feed_url)
    
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "titulo": entry.title,
            "fonte": feed.feed.title,
            "url": entry.link,
            "data": entry.published[:10] if hasattr(entry, 'published') else "N/A"
        })
    
    return {"success": True, "articles": articles}
```

**Sucesso:**
- RSS feeds funcionando
- NewsAPI removido
- Zero custo, ilimitado

---

**Tarefa 2:** Unificar Storage

**Opção A - SQLite apenas:**
```python
# Criar tabela de lembretes no SQLite
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    datetime TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Opção B - JSON apenas (mais simples para uso pessoal):**
```python
# Mover tudo para JSON
DATA_DIR / "conversations.json"  # Ao invés de SQLite
DATA_DIR / "reminders.json"      # Já existe
DATA_DIR / "memory.json"         # Ao invés de RAG externo
```

**Recomendação:** Opção B (JSON) para uso pessoal único - mais simples, fácil de debugar, não requer migrations.

**Sucesso:**
- Um único sistema de storage
- Dados em formato legível
- Fácil backup (copiar arquivos JSON)

**Dependências:** Fase 1 completa

---

## 💡 FASE 3: DESEJÁVEL (Meses 2-3)

**Objetivo:** Adicionar automações pessoais e melhorar UX

### Mês 2: Automações e Offline Mode

**Tarefa 1:** Ferramentas de Automação Pessoal

```python
# NOVO: workspace/tools/personal_automation.py

async def backup_dotfiles() -> dict:
    """Backup de arquivos de configuração"""
    dotfiles = [".bashrc", ".vimrc", ".gitconfig", ".ssh/config"]
    backup_dir = Path.home() / ".assistente" / "backups" / datetime.now().strftime("%Y%m%d")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for dotfile in dotfiles:
        src = Path.home() / dotfile
        if src.exists():
            dst = backup_dir / dotfile.replace(".", "")
            shutil.copy2(src, dst)
    
    return {"success": True, "backup_dir": str(backup_dir)}

async def daily_summary() -> dict:
    """Resumo diário: clima, lembretes, notícias"""
    # Agregar múltiplas fontes
    weather = await get_weather("Ilhéus")
    reminders = await get_today_reminders()
    news = await get_news_rss("brasil", limit=3)
    
    return {
        "success": True,
        "summary": {
            "weather": weather,
            "reminders": reminders,
            "news": news
        }
    }

async def organize_downloads() -> dict:
    """Organiza ~/Downloads por tipo de arquivo"""
    downloads = Path.home() / "Downloads"
    categories = {
        "pdf": ["*.pdf"],
        "images": ["*.jpg", "*.png", "*.gif"],
        "archives": ["*.zip", "*.tar.gz", "*.rar"],
        "documents": ["*.doc", "*.docx", "*.txt"]
    }
    
    for category, patterns in categories.items():
        (downloads / category).mkdir(exist_ok=True)
        for pattern in patterns:
            for file in downloads.glob(pattern):
                if file.is_file():
                    shutil.move(str(file), str(downloads / category / file.name))
    
    return {"success": True}
```

---

**Tarefa 2:** Modo Offline com Ollama

```python
# NOVO: workspace/core/agent_local.py
from ollama import AsyncClient

class LocalAgent:
    """Agente que usa modelos locais via Ollama"""
    
    def __init__(self):
        self.client = AsyncClient()
        self.model = "llama3.2"  # ou "mistral", "codellama"
    
    async def chat(self, message: str, history: list = None) -> str:
        """Chat com modelo local"""
        messages = history or []
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat(
            model=self.model,
            messages=messages
        )
        
        return response.message.content

# Fallback no agent principal
async def run(self, message: str, history: list = None, user_id: int = None):
    try:
        # Tentar Groq primeiro
        return await self._groq_chat(message, history)
    except Exception as e:
        logger.warning(f"Groq falhou: {e}, usando fallback local")
        # Fallback para Ollama
        local_agent = LocalAgent()
        return await local_agent.chat(message, history)
```

**Instalação:**
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo
ollama pull llama3.2
```

---

### Mês 3: Interface Web e Integrações

**Tarefa 1:** Interface Web Minimalista

```python
# NOVO: src/web/app.py
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def dashboard():
    """Painel principal com status"""
    return render_template("dashboard.html")

@app.route("/api/status")
def api_status():
    """API com status do bot"""
    return jsonify({
        "bot_running": check_bot_status(),
        "last_message": get_last_message_time(),
        "reminders_count": count_reminders(),
        "memory_size": get_memory_size()
    })

@app.route("/api/logs")
def api_logs():
    """Últimas linhas do log"""
    return jsonify({"logs": get_recent_logs(lines=100)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
```

**Template HTML:**
```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Assistente Digital - Dashboard</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
        .status { padding: 10px; border-radius: 5px; }
        .online { background: #90EE90; }
        .offline { background: #FFB6C1; }
    </style>
</head>
<body>
    <h1>🤖 Assistente Digital</h1>
    <div id="status" class="status">Carregando...</div>
    <pre id="logs"></pre>
    <script>
        async function updateStatus() {
            const resp = await fetch('/api/status');
            const data = await resp.json();
            document.getElementById('status').className = 'status ' + (data.bot_running ? 'online' : 'offline');
            document.getElementById('status').textContent = data.bot_running ? '🟢 Online' : '🔴 Offline';
        }
        setInterval(updateStatus, 5000);
        updateStatus();
    </script>
</body>
</html>
```

---

## 📊 Dependencies Graph

```
FASE 1 (Semana 1)
├── [1.1] Consolidação de Diretórios (Dias 1-2)
│   └── [1.2] Migração de Scripts (Dias 3-4) [DEPENDE: 1.1]
│   └── [1.3] Fix Lembretes (Dia 5) [DEPENDE: 1.1]
└── [1.4] Documentação (Dias 6-7) [DEPENDE: 1.1, 1.2, 1.3]

FASE 2 (Semanas 2-4) [DEPENDE: FASE 1 COMPLETA]
├── Semana 2: [2.1] Refatoração bot_simple.py
├── Semana 3: 
│   ├── [2.2] ElevenLabs → Piper TTS
│   └── [2.3] OpenWeather → Open-Meteo
└── Semana 4:
    ├── [2.4] NewsAPI → RSS
    └── [2.5] Unificar Storage

FASE 3 (Meses 2-3) [DEPENDE: FASE 2 COMPLETA]
├── Mês 2:
│   ├── [3.1] Automações Pessoais
│   └── [3.2] Offline Mode (Ollama)
└── Mês 3:
    ├── [3.3] Interface Web
    └── [3.4] Integrações adicionais
```

---

## ✅ Success Metrics

### Fase 1 (URGENTE)
- [ ] Bot inicia no novo diretório
- [ ] Testes passam: 7/7 via terminal
- [ ] Scripts estão versionados no git
- [ ] Lembretes persistem após reboot
- [ ] Documentação atualizada

### Fase 2 (IMPORTANTE)
- [ ] bot_simple.py modularizado (< 200 linhas por arquivo)
- [ ] ElevenLabs removido, Piper funcionando
- [ ] OpenWeather removido, Open-Meteo funcionando
- [ ] NewsAPI removido, RSS funcionando
- [ ] Storage unificado
- [ ] Zero APIs freemium com limites

### Fase 3 (DESEJÁVEL)
- [ ] Automações pessoais funcionando
- [ ] Fallback offline funcional
- [ ] Interface web acessível
- [ ] Backup de dotfiles automatizado

---

## 📅 Timeline Resumida

| Fase | Período | Tarefas | Entregável |
|------|---------|---------|------------|
| **1 - URGENTE** | Semana 1 | 4 tarefas | Sistema consolidado e self-contained |
| **2 - IMPORTANTE** | Semanas 2-4 | 5 tarefas | Código modular, zero custo APIs |
| **3 - DESEJÁVEL** | Meses 2-3 | 4 tarefas | Automações, offline, web UI |

**Total:** 13 tarefas distribuídas em ~90 dias

---

## 🚨 Risk Mitigation

| Risco | Mitigação |
|-------|-----------|
| Piper TTS não funciona bem | Manter ElevenLabs como fallback temporário |
| Ollama lento em hardware limitado | Usar apenas como fallback, não principal |
| Refatoração quebra funcionalidades | Testar cada handler isoladamente antes |
| Diretório novo não funciona | Manter diretório antigo até validação completa |
| RSS feeds indisponíveis | Adicionar múltiplas fontes de fallback |

---

## 📝 Next Steps (Imediatos)

1. **Aprovar este plano** com stakeholders (Bruno)
2. **Criar branch** `feat/fase-1-consolidacao` para iniciar
3. **Backup completo** antes de começar
4. **Agendar checkpoints** diários durante Fase 1
5. **Preparar ambiente** de teste isolado

---

## 🔗 Documentos Relacionados

- [ANALISE_CRITICA.md](ANALISE_CRITICA.md) - Análise detalhada
- [MEMORY.md](../MEMORY.md) - Contexto do projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura atual

---

**Plano criado em:** 2026-01-31
**Versão:** 1.0
**Status:** Aguardando aprovação para início da Fase 1
