
# 🤖 Assistente Digital - Bot Telegram com IA

Assistente pessoal avançado com múltiplas funcionalidades de IA, análise de mídia e automação.

**Versão:** 1.3 | **Status:** ✅ Produção | **Testes:** 48/48 passando | ⚡ **Cache Inteligente**

📖 **Documentação 5S:** Comece por **[COMECE_AQUI.md](COMECE_AQUI.md)** ou veja o [guia de documentação](DOCUMENTACAO_5S.md)

---

## Guia rápido – Bot (iniciar, parar, status)

**Pré-requisitos:** [Docker](https://docs.docker.com/get-docker/) instalado e arquivo `.env` na raiz do projeto com pelo menos `TELEGRAM_TOKEN` e `GROQ_API_KEY`. Opcional: `NVIDIA_API_KEY` para fallback quando o Groq atingir o limite (429); `ELEVENLABS_API_KEY` para respostas em áudio (TTS). Copie `.env.example` para `.env` e preencha as chaves.

### Forma oficial: rodar apenas com Docker

O bot deve ser iniciado **somente via Docker** (ambiente estável, sem segfault do Python no host e reproduzível em qualquer máquina).

| Comando | Descrição |
|---------|-----------|
| `make start-docker` | Inicia o bot (com build se necessário) |
| `make stop-docker` | Para o bot |
| `make status-docker` | Verifica se está rodando |
| `make logs` | Mostra logs em tempo real |
| `make test` | Executa testes E2E (48 testes) |
| `make backup` | Instruções de backup |
| `make help` | Lista todos os comandos |

Na primeira vez, `make start-docker` faz o build da imagem e sobe o container com `.env` e volume `dados/` para persistência. Use **apenas uma instância** por token (evite conflito no Telegram).

**Alternativa sem Docker:** em alguns ambientes é possível usar `make start` / `make stop` / `make status` (venv no host). Em WSL/PPA isso pode causar Segmentation fault; nesse caso use sempre Docker.

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
- **Sistema Híbrido de Normas Regulamentadoras (NRs):** 6 NRs em memória (NR-1, NR-5, NR-6, NR-10, NR-29, NR-35) para respostas instantâneas; outras NRs consultadas via web search automático no site do Ministério do Trabalho
- Perguntas só de data/hora respondidas direto (sem agente, economia de tokens)
- Mensagem de rate limit com tempo estimado de espera (ex.: "em cerca de 6 minutos") quando não há fallback
- Respostas em áudio (TTS) opcionais: requer `ELEVENLABS_API_KEY`; sem a chave, o bot responde só em texto e informa que o áudio está indisponível
- Memória persistente (RAG) e memória estruturada via `FactStore`, com **sanitização de dados sensíveis** (senhas/tokens não são armazenados); alimentação de NRs via scripts em `scripts/feed_nr*.py` (NR-1, NR-5, NR-6, NR-10, NR-29, NR-35)
- Web search (DuckDuckGo)
- **Sistema Híbrido NRs:** NRs frequentes em memória (instantâneo), NRs raras via web search (sempre atualizado)
- **Cache Inteligente LRU** - Respostas 90% mais rápidas para queries frequentes
- Para testar no Telegram sem estourar limite: use [teste-pratico-minimo.md](teste-pratico-minimo.md) (6 prompts) ou [teste-pratico.md](teste-pratico.md) em blocos com pausa

### Análise de Mídia
- Imagens (Groq Vision)
- Vídeos do YouTube (yt-dlp + Groq)
- Vídeos do Telegram (ffmpeg + Groq)
- Transcrição de áudio (Whisper Turbo)

### Ferramentas (14 no total)
- Operações de arquivo (read/write/list)
- Git status/diff
- Busca em código
- Clima, notícias, lembretes, gráficos, geração de imagens

### Segurança
- Autenticação de usuários
- Whitelist de IDs autorizados
- Credenciais protegidas (chmod 600)

---

## 🔒 Segurança (v1.2)

### Módulos Implementados
- ✅ **SecureFileManager** - Arquivos temp com auto-cleanup
- ✅ **SafeSubprocessExecutor** - Execução segura de comandos
- ✅ **Rate Limiting** - 20 msgs/min, 5 media/min
- ✅ **Retry com Backoff** - Resiliência a falhas de API
- ✅ **Path Validation** - Proteção contra path traversal
- ✅ **Sanitização** - Dados sensíveis não são armazenados

### Usuário Autorizado
- **User ID:** 6974901522
- **Bot:** @br_bruno_bot

### Adicionar Novo Usuário

1. Descubra o user_id (envie mensagem e veja o log)
2. Edite `security/auth.py` ou use env var:
```bash
export ALLOWED_USERS="6974901522,123456789"
```
3. Reinicie o bot: `make stop-docker` e depois `make start-docker`

---

## 📊 Estrutura do Projeto

O código-fonte fica em `src/`. Na raiz: documentação, testes e scripts.

```
assistente/
├── README.md                   # Este arquivo
├── COMECE_AQUI.md             # Guia prático de uso
├── MEMORY.md                  # Contexto técnico completo
├── CHANGELOG.md               # Histórico de mudanças
├── OTIMIZACAO_PERFORMANCE.md  # Relatório de otimizações v1.3
├── docker-compose.yml         # Docker com restart automático
├── .env.example               # Exemplo de variáveis de ambiente
├── Makefile                   # Comandos úteis
│
├── docs/                      # Documentação 5S organizada
│   ├── 01-essencial/          # 📖 Leia primeiro
│   │   ├── COMECE_AQUI.md     # Guia de primeiros passos
│   │   ├── DOCS_INDEX.md      # Índice mestre
│   │   └── COMPARATIVO_OPENCLAW_REQMIND.md  # Troubleshooting
│   ├── 02-guias/              # 📚 Como fazer
│   │   ├── DEVELOPMENT.md     # Guia de desenvolvimento
│   │   ├── FEATURES.md        # Funcionalidades
│   │   └── TESTING.md         # Guia de testes
│   ├── 03-referencia/         # 📋 Consulta rápida
│   │   ├── API_REFERENCE.md   # APIs e integrações
│   │   └── TOOLS_REFERENCE.md # Ferramentas disponíveis
│   ├── 04-arquitetura/        # 🏗️ Design do sistema
│   │   └── ARCHITECTURE.md    # Arquitetura completa
│   ├── 05-historico/          # 📜 Contexto e decisões
│   └── security/              # 🔒 Documentação de segurança
│
├── src/                       # Código-fonte
│   ├── bot_simple.py          # Entry point do bot
│   ├── commands.py            # Comandos (/start, /status, /lembretes)
│   ├── handlers/              # Handlers de mensagens
│   ├── workspace/             # Core: agent, tools, storage, memory
│   │   └── core/
│   │       └── cache.py       # Sistema de cache LRU (NOVO v1.3)
│   ├── security/              # Módulos de segurança
│   └── config/                # Configurações
│
├── tests/                     # Testes (48 testes E2E)
├── scripts/                   # Scripts utilitários
├── fallbacks.py               # Gerenciador de fallbacks LLM
└── utilitarios.py             # Ferramentas de diagnóstico
```
```

**Execução:** na raiz do repo, com `PYTHONPATH=src` (ex.: `PYTHONPATH=src python src/bot_simple.py` ou `cd src && python bot_simple.py`).

### Padrão do projeto
- **`.gitignore`** – Ignora `.env`, `venv/`, `__pycache__`, logs, `bot.pid`, `src/workspace/memory/facts.jsonl` e artefatos (nunca commitar secrets).
- **`pyproject.toml`** – Metadados do projeto, configuração do pytest e Ruff.
- **`Makefile`** – Comandos oficiais do bot: `make start-docker`, `make stop-docker`, `make status-docker`. Demais: `make install`, `make test`, `make lint`, `make clean`, `make backup`. Ver: `make help`.
- **CI (GitHub Actions)** – `.github/workflows/tests.yml` roda testes e lint em push/PR.

---

## 📚 Documentação (Metodologia 5S)

A documentação está organizada usando a **metodologia 5S** para fácil navegação:

### 🎯 Documentação Essencial (Leia Primeiro)
- **[COMECE_AQUI.md](COMECE_AQUI.md)** - Guia prático do que pedir ao bot
- **[DOCUMENTACAO_5S.md](DOCUMENTACAO_5S.md)** - Guia de navegação da documentação
- **[docs/01-essencial/DOCS_INDEX.md](docs/01-essencial/DOCS_INDEX.md)** - Índice mestre
- **[docs/01-essencial/COMPARATIVO_OPENCLAW_REQMIND.md](docs/01-essencial/COMPARATIVO_OPENCLAW_REQMIND.md)** - Troubleshooting

### 📚 Guias Práticos
- **[docs/02-guias/DEVELOPMENT.md](docs/02-guias/DEVELOPMENT.md)** - Guia de desenvolvimento
- **[docs/02-guias/FEATURES.md](docs/02-guias/FEATURES.md)** - Funcionalidades e exemplos
- **[docs/02-guias/TESTING.md](docs/02-guias/TESTING.md)** - Guia de testes

### 📋 Referência Técnica
- **[docs/03-referencia/API_REFERENCE.md](docs/03-referencia/API_REFERENCE.md)** - APIs e integrações
- **[docs/03-referencia/TOOLS_REFERENCE.md](docs/03-referencia/TOOLS_REFERENCE.md)** - Ferramentas disponíveis
- **[docs/04-arquitetura/ARCHITECTURE.md](docs/04-arquitetura/ARCHITECTURE.md)** - Arquitetura do sistema

### 🔒 Segurança
- **[docs/security/](docs/security/)** - Documentação completa de segurança

### 🧹 Organização 5S
- **Seiri** (Separar): 8 documentos essenciais separados de 40+ históricos
- **Seiton** (Organizar): Estrutura em 5 pastas numeradas
- **Seiso** (Limpar): Documentos duplicados removidos
- **Seiketsu** (Padronizar): Template consistente em todos
- **Shitsuke** (Manter): Checklist mensal de qualidade

---

## 🧪 Testes

```bash
# Executar todos os testes E2E
make test

# Ou dentro do Docker
docker exec assistente-bot python -m pytest tests/ -v
```

**Resultado:** 48/48 testes passando ✅
- Testes de segurança: 8/8 ✅
- Testes de funcionalidades: 14/14 ✅
- Testes E2E: 6/6 ✅
- Testes de LLM Router: 3/3 ✅
- Testes de cache: 2/2 ✅ (NOVO v1.3)

## 🎯 Status do Projeto

- **Versão:** 1.3
- **Status:** ✅ Estável em produção
- **Testes:** 48/48 passando (100%)
- **Performance:** ⚡ 90% mais rápido com cache
- **Última atualização:** 2026-02-06

### Funcionalidades Implementadas
- ✅ Bot Telegram com IA (Groq + Fallbacks)
- ✅ 15 ferramentas integradas
- ✅ **Cache Inteligente LRU** - Respostas 90% mais rápidas
- ✅ Memória persistente (FactStore + RAG)
- ✅ Sistema de lembretes (Telegram + Email)
- ✅ Notícias automáticas às 07h
- ✅ Análise de mídia (imagem, vídeo, áudio)
- ✅ Segurança completa (v1.2)
- ✅ Fallbacks robustos (Kimi/GLM com retry)

## 🐛 Troubleshooting

### Bot não responde
```bash
# Verificar se está rodando
make status-docker

# Ver logs
make logs
# ou
docker logs -f assistente-bot

# Verificar envs no container
docker exec assistente-bot env | grep -E 'TELEGRAM|GROQ'
```

### "Limite de uso da API atingido" (429)
O bot tentará automaticamente:
1. Groq → 2. Kimi (NVIDIA) → 3. GLM → 4. Memória RAG

Se não houver fallback configurado, aguarde 1-2 minutos.

### Lembretes não chegam
- Verifique se o bot está rodando: `make status-docker`
- Verifique SMTP no `.env` (para email)
- Use `/lembretes` para verificar lembretes pendentes

---

## 📝 Documentação Adicional

- **[COMECE_AQUI.md](COMECE_AQUI.md)** - Guia prático do que pedir ao bot
- **[MEMORY.md](MEMORY.md)** - Contexto técnico completo
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças
- **[deploy_config.md](deploy_config.md)** - Configuração de deploy
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura do sistema
- **[docs/FEATURES.md](docs/FEATURES.md)** - Referência de features

---

**Mantenedor:** Bruno (user_id: 6974901522)  
**Bot:** @br_bruno_bot

Ou apenas os testes rápidos (suíte estável, usada por `make test`):

```bash
PYTHONPATH=src python -m pytest tests/test_e2e_simple.py tests/test_security.py -v
```

Testes adicionais: `tests/test_e2e.py`, `tests/test_llm_router.py`, `tests/test_bot_completo.py`.  
Veja [docs/TESTING.md](docs/TESTING.md) para documentação completa. Para prompts de teste no Telegram, use [teste-pratico.md](teste-pratico.md).

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

**Última atualização:** 2026-02-06  
**Versão:** 1.2  
**Status:** Produção
