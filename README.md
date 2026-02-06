# 🤖 Assistente Digital - Bot Telegram com IA

Assistente pessoal avançado com múltiplas funcionalidades de IA, análise de mídia e automação.

**Projeto bagunçado?** Abra **[docs/COMECE_AQUI.md](docs/COMECE_AQUI.md)** – um único guia com o que importa.

---

## Guia rápido – Bot (iniciar, parar, status)

**Pré-requisitos:** ter `venv` ativado (ou usar o Python do venv), arquivo `.env` na raiz com pelo menos `TELEGRAM_TOKEN` e `GROQ_API_KEY`. Opcional: `NVIDIA_API_KEY` para fallback quando o Groq atingir o limite (429) — o bot usará Kimi K2.5 via NVIDIA. Copie `.env.example` para `.env` e preencha as chaves.

| Ação | Comando |
|------|---------|
| Iniciar o bot | `make start` |
| Encerrar o bot | `make stop` |
| Ver se o bot está rodando | `make status` |
| Rodar testes estáveis | `make test` |
| Ver todos os comandos make | `make help` |

Iniciar manualmente (sem script): na raiz do projeto, `PYTHONPATH=src ./venv/bin/python src/bot_simple.py`. Use apenas uma instância por token (evite conflito no Telegram).

---

## 🚀 Quick Start - Notícias Diárias das 07h

### Como Iniciar o Agendamento

O agendamento de notícias é iniciado automaticamente quando o bot é iniciado. Não é necessário nenhuma ação manual para começar a receber notícias às 07h.

### Comandos de Controle

```bash
# Verificar status do agendamento
/noticias status

# Desligar agendamento
/noticias off

# Ver notícias programadas
/noticias schedule
Horário: 07:00
```

### Fontes Disponíveis

Você pode escolher quais fontes usar diariamente:

1. **Boca News** - Notícias do Ilhéus 24h
2. **Boca News** - Notícias do Boca News
3. **Fábio Roberto** - Notícias do Fábio Roberto Notícias
4. **O Tabuleiro** - Notícias do O Tabuleiro
5. **Ilhéus Net** - Notícias do Ilhéus Net
6. **Blog do Gusmão** - Notícias do Blog do Gusmão
7. **Jornal Foco** - Notícias do Jornal Foco
8. **Folha de Ilhéus** - Notícias do Folha de Ilhéus
9. **G1 Bahia** - Notícias do G1 Bahia Ilhéus
10. **Pimenta Blog** - Notícias do Pimenta Blog

### Como Funciona

O sistema agrega automaticamente as principais notícias das fontes locais de Ilhéus e envia um resumo consolidado para o Telegram todos os dias às 07h da manhã (BRT).

**Fluxo:**
1. O bot verifica as fontes disponíveis (Boca News, Fábio Roberto, O Tabuleiro, Ilhéus Net, Jornal Foco, Blog do Gusmão, G1 Bahia, Pimenta Blog, etc.)
2. Coleta as últimas 10 notícias de cada fonte
3. Formata um resumo consolidado (com cabeçalho, listagem por fonte, links)
4. Envia o resumo para seu Telegram às 07:00

### Comandos Disponíveis

| Comando | Descrição |
|----------|-----------|-------------|
| `/noticias` | Mostra resumo de hoje |
| `/noticias [fontes]` | Lista fontes disponíveis |
| `/noticias [fonte]` | Consulta notícias de uma fonte específica |
| `/noticias schedule` | Agenda envio automático às 07h |
| `/noticias on` | Liga agendamento automático |
| `/noticias off` | Desliga agendamento |

---

## 📋 Funcionalidades

### Chat e IA
- Chat com IA (Groq - Llama 3.3 70B); em caso de limite da API (429), fallback para **Kimi K2.5** via NVIDIA (`NVIDIA_API_KEY`) e, se indisponível, **resposta a partir da memória RAG** (ex.: NR-29), com truncamento em fronteira de frase e aviso "(Resumo truncado.)"
- Perguntas só de data/hora respondidas direto (sem agente, economia de tokens)
- Mensagem de rate limit com tempo estimado de espera (ex.: "em cerca de 6 minutos") quando não há fallback
- Memória persistente (RAG) e memória estruturada via `FactStore`, com **sanitização de dados sensíveis** (senhas/tokens não são armazenados); alimentação de normas (ex.: NR-29) via `scripts/feed_nr29_to_memory.py` e `scripts/feed_nr29_oficial.py`
- Web search (DuckDuckGo)

### Análise de Mídia
- Imagens (Groq Vision)
- Vídeos do YouTube (yt-dlp + Groq)
- Vídeos do Telegram (ffmpeg + Groq)
- Transcrição de áudio (Whisper Turbo)

### Ferramentas
- Operações de arquivo (read/write/list)
- Git status/diff
- Busca em código

### Segurança
- Autenticação de usuários
- Whitelist de IDs autorizados
- Credenciais protegidas (chmod 600)

---

## 🔒 Segurança (v1.1)

### Usuário Autorizado
- **User ID:** 6974901522
- **Bot:** @br_bruno_bot

### Módulos de Segurança Implementados

#### ✅ SecureFileManager
Arquivos temporários com auto-cleanup garantido.
```python
from security import secure_files
async with secure_files.temp_file(suffix='.mp4') as path:
    await process_video(path)
    # Auto-deletado ao sair do contexto
```

#### ✅ SafeSubprocessExecutor
Execução segura de comandos (ffmpeg, etc).
```python
from security import SafeSubprocessExecutor
success, stdout, stderr = await SafeSubprocessExecutor.run([
    "ffmpeg", "-i", str(video), "-vframes", "1", str(frame)
])
```

#### ✅ Retry com Backoff
Resiliência a falhas de API.
```python
from utils import retry_with_backoff
@retry_with_backoff(max_retries=3)
async def call_api():
    return await api.request()
```

#### ✅ Rate Limiting
Proteção contra abuso: 20 msgs/min, 5 media/min.

#### ✅ Configuração Centralizada
Sem hardcoded paths, via variáveis de ambiente:
```bash
MOLTBOT_DIR=/path/to/project
MOLTBOT_TEMP=/tmp/moltbot_secure
ALLOWED_USERS=123456789,987654321
```

### Adicionar Novo Usuário

1. Descubra o user_id (envie mensagem e veja o log)
2. Edite `security/auth.py` ou use env var:
```bash
export ALLOWED_USERS="6974901522,123456789"
```
3. Reinicie o bot: `make stop` e depois `make start`

---

## 📊 Estrutura do Projeto

O código-fonte fica em `src/`. Na raiz: documentação, testes e scripts.

```
assistente/
├── README.md                  # Início rápido
├── MEMORY.md                  # Contexto completo para desenvolvedores
├── .env.example               # Exemplo de variáveis de ambiente
├── requirements.txt
├── docs/                      # Documentação (ARCHITECTURE, FEATURES, TESTING, security/, etc.)
├── scripts/                   # start.sh, stop.sh; feed_nr29_to_memory.py, feed_nr29_oficial.py (RAG)
├── tests/                     # test_e2e_simple.py, test_security.py, test_bot_completo.py, ...
└── src/                       # Código-fonte
    ├── bot_simple.py          # Bot principal (~760 linhas)
    ├── config/                # settings.py (config centralizada)
    ├── security/              # auth, rate_limiter, sanitizer, file_manager, executor, media_validator
    ├── utils/                 # retry.py
    └── workspace/             # core/ (agent, tools), tools/, storage/, memory/, runs/, agent/
```

**Execução:** na raiz do repo, com `PYTHONPATH=src` (ex.: `PYTHONPATH=src python src/bot_simple.py` ou `cd src && python bot_simple.py`).

### Padrão do projeto
- **`.gitignore`** – Ignora `.env`, `venv/`, `__pycache__`, logs e artefatos (nunca commitar secrets).
- **`pyproject.toml`** – Metadados do projeto, configuração do pytest e Ruff.
- **`Makefile`** – Comandos: `make start`, `make stop`, `make status`, `make install`, `make test`, `make lint`, `make clean`. Ver: `make help`.
- **CI (GitHub Actions)** – `.github/workflows/tests.yml` roda testes e lint em push/PR.

---

## 📚 Documentação

### Documentação principal
- `README.md` - Início rápido
- `MEMORY.md` - Contexto completo do projeto (estrutura, segurança, testes, segfault)
- `docs/DOCS_INDEX.md` - Índice navegável de toda a documentação

### Documentação técnica
- `docs/ARCHITECTURE.md` - Arquitetura do sistema
- `docs/FEATURES.md` - Funcionalidades
- `docs/TESTING.md` - Testes e validação
- `docs/DEVELOPMENT.md` - Guia de desenvolvimento
- `docs/API_REFERENCE.md` - Referência de APIs
- `docs/TOOLS_REFERENCE.md` - Ferramentas
- `docs/security/` - Segurança (SECURITY_INDEX, SECURITY_IMPLEMENTED, etc.)
- `docs/AUDITORIA_PROJETO.md` - Relatório de auditoria
- `docs/PLANO_IMPLEMENTACAO_AUDITORIA.md` - Plano de implementação

---

## 🎯 Status Atual

- ✅ Bot rodando com 1 instância estável
- ✅ Scripts de gerenciamento funcionais
- ✅ Sistema de agendamento de notícias implementado
- ✅ Funções específicas por site criadas
- ✅ Documentação atualizada
- ✅ **Testes via terminal: 7/7 funcionalidades passaram (100%)**
  - Web Search, RAG Search, Save Memory ✅
  - Search Code, Filesystem (R/W/List) ✅
  - Git Status/Diff, Tool Registry ✅
- ✅ **Fallback em rate limit (429):** Kimi K2.5 (NVIDIA) e, na sequência, resposta a partir da memória RAG (ex.: NR-29), com truncamento em fronteira de frase
- ✅ **Melhorias de segurança v1.1 implementadas**
  - SecureFileManager (auto-cleanup)
  - SafeSubprocessExecutor (comandos seguros)
  - Retry com backoff (resiliência)
  - Rate limiting (proteção contra abuso)
  - Configuração centralizada

**Próximos passos:**
1. ✅ Testar funcionalidades via terminal (CONCLUÍDO - 7/7 passaram)
2. Testar comando `/noticias`
3. Verificar agendamento automático às 07h
4. Adicionar mais fontes se desejado

### 🧪 Como Testar

A partir da raiz do repositório (com venv ativado e dependências instaladas):

```bash
# Testes unitários e E2E (path portável)
PYTHONPATH=src python -m pytest tests/ -v
```

Ou apenas os testes rápidos:

```bash
PYTHONPATH=src python -m pytest tests/test_e2e_simple.py tests/test_security.py -v
```

Veja [docs/TESTING.md](docs/TESTING.md) para documentação completa de testes.

---

## 💡 Dicas de Uso

1. **Notícias Automáticas:** Você receberá um resumo diário às 07h da manhã automaticamente sem precisar perguntar.

2. **Fontes Disponíveis:** Você pode escolher quais fontes usar diariamente editando o arquivo `.env`.

3. **Comandos Rápidos:**
   - `/noticias today` - Força um resumo agora
   - `/noticias status` - Verifica status do agendamento
   - `/noticias off` - Desliga agendamento automático (caso queira controlar manualmente)

---

## 📞 Suporte

Se tiver dúvidas ou precisar de ajuda, consulte a documentação disponível em `docs/` ou envie uma mensagem para o assistente.

---

**Última atualização:** 2026-02-05  
**Versão:** 1.1  
**Status:** Produção
