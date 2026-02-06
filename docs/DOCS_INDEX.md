# 📚 Índice da Documentação - Assistente Digital

Guia de navegação da documentação do Assistente Digital de Bruno, organizado em **documentos ativos** (fonte de verdade atual) e **documentos históricos/legado**.

---

## 1. Documentos Ativos (fonte de verdade)

### 1.1 Visão geral e operação

- **[README.md](../README.md)** – Início rápido do bot (.env, make, estrutura, status).
- **[COMECE_AQUI.md](COMECE_AQUI.md)** – Atalho operacional para comandos do dia a dia.

### 1.2 Arquitetura, features e desenvolvimento

- **[MEMORY.md](../MEMORY.md)** – Contexto completo, decisões arquiteturais, segurança e roadmap.
- **[ARCHITECTURE.md](ARCHITECTURE.md)** – Arquitetura detalhada do sistema.
- **[FEATURES.md](FEATURES.md)** – Funcionalidades com exemplos de uso.
- **[DEVELOPMENT.md](DEVELOPMENT.md)** – Guia de desenvolvimento (estrutura modular, como estender).
- **[TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)** – Referência das ferramentas (tool calling).
- **[API_REFERENCE.md](API_REFERENCE.md)** – Modelos de IA, APIs externas, variáveis de ambiente.
- **[TESTING.md](TESTING.md)** – Guia de testes e validação (E2E, via terminal, notas de segfault).

### 1.3 Segurança

- **[security/SECURITY_INDEX.md](security/SECURITY_INDEX.md)** – Índice de segurança.
- **[security/SECURITY_IMPLEMENTED.md](security/SECURITY_IMPLEMENTED.md)** – Segurança implementada.
- **[security/SECURITY_SUMMARY.md](security/SECURITY_SUMMARY.md)** – Resumo executivo.
- **[security/SECURITY_AUDIT_REPORT.md](security/SECURITY_AUDIT_REPORT.md)** – Relatório detalhado (ver também seção de históricos).
- **[security/IMPLEMENTATION_PLAN.md](security/IMPLEMENTATION_PLAN.md)** – Plano de implementação.

### 1.4 Status e roadmap

- **[STATUS_ATUAL.md](STATUS_ATUAL.md)** – Snapshot histórico de 2026‑02‑04 com nota de atualização.  
  - Para o **estado vigente do sistema** e roadmap atual, usar `README.md` e `MEMORY.md` como referência principal.

### 1.5 Código legado / histórico

- Diretório `obsoleto/` na raiz do projeto – contém implementações antigas (ex.: sandbox, protótipos de bot, exemplos de Browserless) mantidas apenas para referência histórica.  
  - O código em `obsoleto/` **não faz parte** do caminho oficial de execução do bot; os entrypoints atuais são `src/bot_simple.py`, `src/handlers/*` e `src/workspace/core/agent.py`.

---

## 2. Auditoria e Plano de Implementação (histórico focado)

- **[AUDITORIA_PROJETO.md](AUDITORIA_PROJETO.md)** – Relatório de auditoria técnica (2026-02-05).
- **[PLANO_IMPLEMENTACAO_AUDITORIA.md](PLANO_IMPLEMENTACAO_AUDITORIA.md)** – Plano de implementação baseado na auditoria.

---

## 3. 🚀 Início Rápido

### Para Usuários

**Projeto bagunçado ou não sabe por onde começar:** **[COMECE_AQUI.md](COMECE_AQUI.md)** – um único guia com comandos do dia a dia e onde achar o resto.

Depois:
- [`README.md`](../README.md) – guia rápido do bot, .env, estrutura.
- [`FEATURES.md`](FEATURES.md) – funcionalidades e exemplos.
- Todas as funcionalidades
- Exemplos de uso
- Dicas e truques

---

## 4. 📖 Documentação Principal (resumo)

### 1. README.md - Início Rápido
**Tamanho:** 12KB | **Tempo de leitura:** 10 min

**Conteúdo:**
- ✅ Quick Start (iniciar, parar, verificar status)
- ✅ Teste E2E
- ✅ Lista de funcionalidades
- ✅ Configuração (.env)
- ✅ Comandos úteis
- ✅ Troubleshooting básico
- ✅ Estrutura do projeto
- ✅ Informações do bot

**Para quem:**
- Novos usuários
- Setup inicial
- Referência rápida

---

### 2. ARCHITECTURE.md - Arquitetura do Sistema
**Tamanho:** 20KB | **Tempo de leitura:** 30 min

**Conteúdo:**
- 🏗️ Visão geral da arquitetura
- 🔄 Fluxo de dados
- 🤖 Componentes principais (Bot, Agent, Tools)
- 📊 Diagramas de arquitetura
- 🎨 Análise de mídia (imagens, vídeos, áudio)
- 🔧 Padrões de projeto
- ⚡ Performance e escalabilidade
- 🔒 Segurança

**Para quem:**
- Desenvolvedores
- Arquitetos de software
- Quem quer entender como funciona

---

### 3. FEATURES.md - Guia Completo de Funcionalidades
**Tamanho:** 19KB | **Tempo de leitura:** 40 min

**Conteúdo:**
- 💬 Chat inteligente
- 🖼️ Análise de imagens
- 🎬 Análise de vídeos (Telegram e YouTube)
- 🎤 Transcrição de áudio
- 🔊 Text-to-Speech
- 📄 Análise de documentos (Excel, CSV, Word, OCR)
- 💻 Ferramentas de desenvolvimento
- 🌐 Web search
- 🧠 Memória persistente (RAG); alimentação NR-29 (scripts feed_nr29_*); fallback RAG em 429
- ⏰ Sistema de lembretes
- 🌤️ Ferramentas extras (clima, notícias, gráficos)
- 📝 Comandos do bot

**Para quem:**
- Usuários que querem explorar todas as capacidades
- Referência de funcionalidades
- Exemplos práticos

---

### 4. API_REFERENCE.md - Referência de APIs
**Tamanho:** 14KB | **Tempo de leitura:** 25 min

**Conteúdo:**
- 🤖 Modelos de IA (Groq, ElevenLabs)
  - Chat (Llama 3.3 70B)
  - Vision (Llama 4 Scout 17B)
  - Audio (Whisper Large v3 Turbo)
  - Text-to-Speech
- 🌐 APIs externas (OpenWeatherMap, NewsAPI)
- ⚙️ Configuração (.env)
- 📊 Limites e quotas
- ❌ Códigos de erro
- 💡 Exemplos completos

**Para quem:**
- Desenvolvedores
- Integração com APIs
- Troubleshooting de APIs

---

### 5. TOOLS_REFERENCE.md - Referência de Ferramentas
**Tamanho:** 11KB | **Tempo de leitura:** 20 min

**Conteúdo:**
- 🔧 14 ferramentas disponíveis
- 📝 Parâmetros e retornos
- 💡 Exemplos de uso
- 🛠️ Como adicionar nova ferramenta
- ✅ Boas práticas
- ⚠️ Limitações

**Categorias:**
- Web & Search (web_search)
- Memória RAG (rag_search, save_memory)
- Filesystem (read_file, write_file, list_directory)
- Code & Git (search_code, git_status, git_diff)
- Extras (weather, news, reminders, charts, images)

**Para quem:**
- Desenvolvedores
- Quem quer adicionar ferramentas
- Referência técnica

---

### 6. TESTING.md - Guia de Testes e Validação ⭐ NOVO
**Tamanho:** 12KB | **Tempo de leitura:** 15 min

**Conteúdo:**
- 🧪 Status de testes (7/7 funcionalidades core passaram)
- 📊 Resultados detalhados por funcionalidade
- 🔧 Como executar testes via terminal
- 📁 Estrutura de arquivos de teste
- 🎯 Testes E2E (28/28 passando)
- 🚨 Troubleshooting de testes
- 📈 Histórico de execuções

**Funcionalidades Testadas:**
- Web Search (DuckDuckGo)
- RAG Search (memória pessoal)
- Save Memory
- Search Code
- Filesystem (read/write/list)
- Git (status/diff)
- Tool Registry

**Para quem:**
- Desenvolvedores
- QA e testadores
- Quem quer verificar se tudo funciona
- Referência antes de deploy

---

### 7. DEVELOPMENT.md - Guia de Desenvolvimento
**Tamanho:** 14KB | **Tempo de leitura:** 30 min

**Conteúdo:**
- 🛠️ Setup do ambiente
- 📁 Estrutura do código (modularizada: handlers/, commands.py, agent_setup.py)
- ➕ Adicionar nova funcionalidade
- ➕ Adicionar novo handler de mídia (estrutura modularizada)
- 🧪 Testes (E2E, unitários, manuais)
- 🚀 Deploy (dev, produção, Docker)
- ✅ Boas práticas
- 🐛 Debugging
- 🤝 Contribuindo

**Para quem:**
- Desenvolvedores
- Contribuidores
- Quem quer estender o bot
- Quem precisa entender a estrutura modularizada

---

### 8. Gerenciamento de instâncias

Se existir `INSTANCE_MANAGEMENT.md` ou documentação equivalente em `scripts/`, consulte para:
- múltiplas instâncias,
- scripts start/stop/healthcheck,
- fluxo de trabalho,
- troubleshooting de delay e conflitos de token.

---

## 5. 🔒 Documentação de Segurança

### 🛡️ Módulos de Segurança Implementados (v1.1 - 2026-01-31)

#### ARCHITECTURE.md → Seção "Módulos de Segurança"
Documentação completa da arquitetura dos novos módulos de segurança:
- SecureFileManager (arquivos temporários seguros)
- SafeSubprocessExecutor (execução segura de comandos)
- Retry Decorator (resiliência a falhas)
- Config Centralizada (sem hardcoded paths)
- Rate Limiting no Agent
- Migração para Asyncio Puro

#### FEATURES.md → Seção "12. Segurança e Estabilidade"
Guia de funcionalidades de segurança com exemplos práticos:
- SecureFileManager (auto-cleanup de arquivos)
- SafeSubprocessExecutor (comandos seguros)
- Retry com Backoff (resiliência)
- Rate Limiting (proteção contra abuso)
- Configuração Centralizada
- Asyncio Puro (estabilidade)

#### API_REFERENCE.md → Seção "APIs Internas (Novas)"
Referência completa das APIs dos novos módulos:
- SecureFileManager API (temp_file, sanitize_filename, validate_mime_type)
- SafeSubprocessExecutor API (run, whitelist)
- Retry Decorator API (retry_with_backoff)
- Config API (config object, variáveis de ambiente)

### 📚 Documentação de Segurança (Legado - Pre-v1.1)

#### SECURITY_IMPLEMENTED.md
Segurança básica implementada (autenticação, rate limiting, proteção de credenciais).

#### SECURITY_INDEX.md
Índice de toda documentação de segurança.

#### SECURITY_AUDIT_REPORT.md
Análise forense completa de vulnerabilidades (20+ páginas).

#### SECURITY_SUMMARY.md
Resumo executivo de segurança.

#### IMPLEMENTATION_PLAN.md
Plano de implementação de melhorias de segurança.

**Nota:** Módulos de segurança v1.1 foram implementados conforme este plano. A documentação acima (ARCHITECTURE, FEATURES, API_REFERENCE) contém informações atualizadas.

---

## 6. 📝 Outros Documentos

### YOUTUBE-ANALYZER-IMPLEMENTADO.md
Documentação da implementação do analisador de YouTube (legado).

### .env.example
Exemplo de configuração de variáveis de ambiente.

### requirements.txt
Dependências Python do projeto.

### test_e2e.py
Script de teste end-to-end.

---

## 7. 🗺️ Mapa de Navegação

### Quero começar a usar o bot
```
README.md → Teste E2E → FEATURES.md
```

### Quero entender como funciona
```
README.md → ARCHITECTURE.md → TOOLS_REFERENCE.md
```

### Quero desenvolver/contribuir
```
DEVELOPMENT.md → ARCHITECTURE.md → TOOLS_REFERENCE.md → API_REFERENCE.md
```

### Quero adicionar nova funcionalidade
```
DEVELOPMENT.md (Adicionar Nova Funcionalidade) → TOOLS_REFERENCE.md (Como adicionar)
```

### Quero integrar com APIs
```
API_REFERENCE.md → .env.example
```

### Tenho um problema
```
README.md (Troubleshooting) → Logs (tail -f bot.log)
```

---

## 8. 📊 Estatísticas da Documentação

| Documento | Tamanho | Linhas | Tempo Leitura |
|-----------|---------|--------|---------------|
| README.md | 12KB | 400 | 10 min |
| ARCHITECTURE.md | 20KB | 650 | 30 min |
| FEATURES.md | 19KB | 600 | 40 min |
| API_REFERENCE.md | 14KB | 500 | 25 min |
| TOOLS_REFERENCE.md | 11KB | 560 | 20 min |
| DEVELOPMENT.md | 14KB | 650 | 30 min |
| **TOTAL** | **90KB** | **3.360** | **2h 35min** |

---

## 9. 🎯 Documentação por Persona

### 👤 Usuário Final
**Objetivo:** Usar o bot no dia a dia

**Leia:**
1. README.md (Quick Start)
2. FEATURES.md (Funcionalidades)

**Tempo:** 50 minutos

---

### 👨‍💻 Desenvolvedor
**Objetivo:** Entender e contribuir com o código

**Leia:**
1. README.md (Overview)
2. ARCHITECTURE.md (Como funciona)
3. DEVELOPMENT.md (Como desenvolver)
4. TOOLS_REFERENCE.md (Ferramentas)

**Tempo:** 2 horas

---

### 🏗️ Arquiteto de Software
**Objetivo:** Avaliar arquitetura e escalabilidade

**Leia:**
1. ARCHITECTURE.md (Arquitetura completa)
2. API_REFERENCE.md (Integrações)
3. SECURITY_AUDIT_REPORT.md (Segurança)

**Tempo:** 1h 30min

---

### 🔌 Integrador de APIs
**Objetivo:** Integrar com APIs externas

**Leia:**
1. API_REFERENCE.md (APIs e limites)
2. TOOLS_REFERENCE.md (Como adicionar)
3. DEVELOPMENT.md (Boas práticas)

**Tempo:** 1h 15min

---

## 10. 🔍 Busca Rápida

### Conceitos

| Conceito | Documento | Seção |
|----------|-----------|-------|
| Agent | ARCHITECTURE.md | Componentes Principais → Agent |
| Tool Calling | ARCHITECTURE.md | Agent → Fluxo de Execução |
| Groq Vision | API_REFERENCE.md | Modelos de IA → Vision |
| Kimi K2.5 / NVIDIA fallback | API_REFERENCE.md | Modelos de IA → NVIDIA (Kimi K2.5) |
| Rate limit 429 | API_REFERENCE.md, README.md, FEATURES.md | Groq; fallback Kimi e RAG |
| YouTube Analyzer | ARCHITECTURE.md | Análise de Mídia → Vídeos do YouTube |
| RAG | FEATURES.md | Memória Persistente |
| Lembretes | FEATURES.md | Sistema de Lembretes |
| Segurança | security/SECURITY_IMPLEMENTED.md | - |
| Segfault em testes | MEMORY.md | Notas sobre Testes |

### Tarefas

| Tarefa | Documento | Seção |
|--------|-----------|-------|
| Iniciar bot | README.md | Quick Start |
| Adicionar ferramenta | DEVELOPMENT.md | Adicionar Nova Funcionalidade |
| Configurar .env | README.md | Configuração |
| Testar bot | README.md / TESTING.md | Teste E2E: `PYTHONPATH=src python -m pytest tests/ -v` |
| Debugar erro | DEVELOPMENT.md | Debugging |
| Obter API key | API_REFERENCE.md | Configuração → Obter API Keys |
| Adicionar usuário | README.md | Segurança → Adicionar Novo Usuário |

---

## 11. 📞 Suporte

### Problemas Técnicos
1. Consulte `README.md` → Troubleshooting
2. Veja logs: `tail -f bot.log`
3. Execute testes: `PYTHONPATH=src python -m pytest tests/ -v` (ver TESTING.md e MEMORY.md para segfault)

### Dúvidas sobre Funcionalidades
1. Consulte `FEATURES.md`
2. Veja exemplos práticos

### Dúvidas sobre Desenvolvimento
1. Consulte `DEVELOPMENT.md`
2. Veja `ARCHITECTURE.md` para entender o fluxo

---

## 12. 🎉 Conclusão

A documentação do Assistente Digital está completa e organizada para atender diferentes perfis de usuários:

- ✅ **Usuários:** README + FEATURES
- ✅ **Desenvolvedores:** DEVELOPMENT + ARCHITECTURE + TOOLS_REFERENCE
- ✅ **Integradores:** API_REFERENCE
- ✅ **Arquitetos:** ARCHITECTURE + SECURITY

**Total:** 90KB de documentação, 3.360 linhas, cobrindo todos os aspectos do sistema.

---

**Última atualização:** 2026-02-06  
**Versão:** 1.3  
**Status:** Completo. Documentos ativos e históricos explicitados; estado atual do sistema centralizado em `README.md` e `MEMORY.md`.  
