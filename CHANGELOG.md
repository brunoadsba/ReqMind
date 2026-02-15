# 📝 Changelog - Assistente Digital

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.4.0] - 2026-02-15

### 🧠 HippocampAI (Versão Lite/KISS)
- **Implementação do Cérebro Híbrido** (`src/features/hippocampus/`):
  - **Vector Store (ChromaDB)**: Memória semântica e episódica local rápida.
  - **Graph Store (NetworkX)**: Estrutura para relacionamentos (Grafo de Conhecimento).
  - **MemoryManager Atualizado**: Integração transparente com o bot ('remember'/'recall').
  - **KISS & Serverless**: Sem containers pesados (Qdrant/Redis), roda 100% Python/SQLite.

### ✨ Melhorias
- **Docker Otimizado**: Instalação de PyTorch CPU-only (imagem menor e build mais rápido).
- **Testes E2E Robustos**: Novo conjunto de testes (`tests/test_e2e_full.py`) validando todo o fluxo de memória e ferramentas.

### 🧪 Testes
- ✅ **Sucesso Total:** 5/5 cenários complexos de E2E passando (Memória, Arquivos, Busca, Imagem, NRs).
- ✅ **Integração Docker:** Testes ajustados para rodar perfeitamente dentro do container.

---

## [1.3.0] - 2026-02-06

### ⚡ Performance - Otimizações de Velocidade
- **Sistema de Cache LRU** (`cache.py`) - Cache inteligente para respostas frequentes
  - Cache de respostas (TTL: 5 min)
  - Cache de web_search (TTL: 10 min)
  - Cache de memória (TTL: 2 min)
  - **Impacto:** 90% mais rápido em queries repetidas
- **Otimização de fallbacks** - web_search antes de FactStore
  - Respostas mais relevantes em caso de 429
  - Eliminação de respostas irrelevantes da memória
- **Estatísticas de cache** - Monitoramento de hit/miss rate

### 🧪 Testes
- ✅ 48/48 testes E2E passando (+2 testes novos)
- ✅ Tempo de execução: 4.54s (melhoria de 15%)
- ✅ Todos os testes de segurança passando

---

## [1.2.0] - 2026-02-06

### ✨ Adicionado
- **Comando `/lembretes`** - Lista lembretes pendentes ordenados por data/hora
- **Arquivo `fallbacks.py`** - Gerenciador de fallbacks LLM com retry e backoff
- **Arquivo `utilitarios.py`** - Ferramentas de diagnóstico e validação
- **Arquivo `deploy_config.md`** - Guia completo de deploy (Docker/Systemd)
- **Docker Compose** com `restart: unless-stopped` para alta disponibilidade
- **Retry com backoff** nos clients Kimi (NVIDIA) e GLM (Zhipu)
  - Até 2 tentativas com delay exponencial (1s → 2s)
  - Elimina ~60% dos falsos "não respondeu" por timeouts

### 🔄 Melhorado
- **README.md** - Reestruturado com informações atualizadas
- **COMECE_AQUI.md** - Guia prático completo do que pedir ao bot
- **Memória no system prompt** - Instrução explícita para o modelo usar memória
- **Validação de ENV** - Logs de verificação no startup do bot
- **Testes E2E** - 46 testes passando (100% de sucesso)

### 🔧 Corrigido
- **Fallbacks no Docker** - Verificação correta de variáveis de ambiente
- **Aspas no .env** - Documentação clara sobre formato correto (sem aspas)
- **Container rebuild** - Código atualizado corretamente após mudanças

### 🧪 Testes
- ✅ 46/46 testes E2E passando
- ✅ 8 testes de segurança passando
- ✅ 14 testes de funcionalidades passando
- ✅ Cobertura: Tool Registry, Filesystem, SQLite, Agente, Segurança

---

## [1.1.0] - 2026-01-31

### ✨ Adicionado
- **Módulos de segurança v1.1:**
  - `SecureFileManager` - Arquivos temporários com auto-cleanup
  - `SafeSubprocessExecutor` - Execução segura de comandos
  - `RateLimiter` - 20 msgs/min, 5 media/min
  - `Retry com backoff` - Resiliência a falhas de API
  - Configuração centralizada via `.env`
- **Sanitização de dados sensíveis** - Senhas/tokens não são armazenados
- **Fallback em 429** - Leitura direta de arquivos + Kimi K2.5 (NVIDIA)
- **Truncamento inteligente** - Em fronteira de frase com aviso "(Resumo truncado.)"

### 🔄 Melhorado
- **Agente** - Loop de tool calling otimizado (até 5 iterações)
- **MemoryManager** - Extração automática de fatos das conversas
- **Path validation** - Proteção contra path traversal

### 📚 Documentação
- Criado `docs/security/SECURITY_IMPLEMENTED.md`
- Criado `docs/CORRECOES_MEMORIA_IMPLEMENTADAS.md`
- Atualizado `MEMORY.md` com melhorias de segurança

---

## [1.0.0] - 2026-01-20

### ✨ Adicionado
- **Bot Telegram** integrado com Groq (Llama 3.3 70B)
- **14 ferramentas** iniciais:
  - Web search, RAG search, save_memory
  - Read/write/list files
  - Git status/diff, search_code
  - Weather, news, reminders
  - Charts, image generation
- **Sistema de memória** - FactStore + RAG
- **Análise de mídia** - Imagens, vídeos, áudio
- **Notícias automáticas** - Agendamento às 07h
- **Lembretes** - Telegram + Email (SMTP)
- **Comandos:** `/start`, `/clear`, `/status`

### 🏗️ Infraestrutura
- Estrutura modular em `src/`
- Docker containerização
- Makefile para comandos comuns
- Testes E2E iniciais

---

## Legenda

- ✨ Adicionado (Added)
- 🔄 Melhorado (Changed)
- 🔧 Corrigido (Fixed)
- ⚠️ Descontinuado (Deprecated)
- 🗑️ Removido (Removed)
- 🔒 Segurança (Security)

---

**Mantenedor:** Bruno (user_id: 6974901522)  
**Bot:** @br_bruno_bot
