# Comparativo: OpenClaw vs ReqMind (assistente)

Modelo mental do OpenClaw aplicado ao projeto ReqMind/assistente para ver o que temos e o que falta.

**Versão do Documento:** 1.3 (Atualizado em 2026-02-06)  
**Status:** ✅ Todos os itens obrigatórios completos

---

## Modelo OpenClaw (resumo)

OpenClaw são **três coisas**:

1. **Motor local** – roda na sua máquina/servidor  
2. **Gateway** – permite que UIs e ferramentas falem com o motor  
3. **Habilidades (skills)** – definem o que o agente pode fazer  

**Fluxo:** `UI (navegador) → Gateway local → Cérebro do agente → Habilidades → Ações no mundo`  

Se uma camada faltar, tudo parece “quebrado”. Erros comuns não são de IA: comando não encontrado (Node/PATH), não autorizado (token do gateway), health check (serviço parado). **Infraestrutura primeiro, IA em segundo.**

---

## Mapeamento no ReqMind (assistente)

| Camada OpenClaw | No ReqMind | Tem? | Observação |
|-----------------|------------|------|------------|
| **Motor local** | Processo que roda o agente: `bot_simple.py` + `agent.py` + `llm_router` + Tool Registry. Roda em Docker ou venv. | Sim | Um único processo; motor e “cérebro” (Agent + LLM) no mesmo processo. |
| **Gateway** | Ponto por onde a “UI” fala com o motor. No ReqMind é a **conexão com o Telegram** (long polling ou webhook): handlers recebem mensagens e chamam `agent.run()`. | Sim (implícito) | O próprio bot é o gateway: não existe um serviço de gateway separado. Só uma “UI” (cliente Telegram). |
| **Habilidades** | Conjunto de ferramentas que o agente pode usar: web_search, read_file, write_file, list_directory, git_status, get_weather, etc. (14–15 tools). | Sim | Registry em `workspace/core/tools.py`; implementações em `workspace/tools/`. |

**Fluxo real ReqMind:**  
`Telegram (UI) → Bot (gateway implícito) → Agent → LLM (Groq/Kimi/GLM) → Tool Registry → Habilidades → Resposta`

---

## O que temos (v1.3 - Atualizado)

- **Motor:** Processo único (Docker ou `make start`) com bot + agente + LLM + tools.  
- **Gateway:** Telegram como único canal; bot recebe mensagens e repassa ao agente.  
- **Habilidades:** 15 tools registradas (arquivo, código, Git, web, clima, notícias, lembretes, gráficos, etc.).  
- **Cache Inteligente:** Sistema LRU para respostas frequentes (90% mais rápido).  
- **Autenticação:** `TELEGRAM_TOKEN` + `ALLOWED_USERS` (whitelist).  
- **Infraestrutura documentada:** README, MEMORY.md, Docker, Makefile, scripts start/stop/status/health.  
- **Fallbacks de LLM:** Kimi (NVIDIA) e GLM com retry/backoff; web_search como fallback principal.  
- **Segurança:** auth, rate limit, sanitização de paths, SafeSubprocessExecutor, SecureFileManager.  
- **Health Check:** `make health` verifica as 3 camadas (motor, env, habilidades).

---

## Status de Implementação (v1.3) - ITENS OBRIGATÓRIOS COMPLETOS ✅

| Aspecto | OpenClaw | ReqMind v1.3 | Status |
|--------|----------|--------------|--------|
| ✅ **Modelo mental** | “É três coisas; infra primeiro.” | MEMORY.md e ARCHITECTURE descrevem componentes, mas não explicam em um só lugar “motor / gateway / habilidades” e que a quebra costuma ser de camada. | Seção única (ex.: “Como funciona na realidade”) com as 3 camadas e fluxo, e “se falhou, qual camada?”. |
| **Gateway explícito e reutilizável** | Gateway é um serviço ao qual várias UIs e ferramentas se conectam. | Gateway = bot Telegram no mesmo processo. Não há API HTTP (ou outro protocolo) para outra UI (ex.: painel web) ou ferramenta externa falar com o mesmo agente. | Gateway opcional (ex.: API HTTP ou WebSocket) para além do Telegram, se quiser “várias UIs” como no OpenClaw. |
| ✅ **Health check** | Erros de health = serviço não rodando ou mal configurado. | Temos `make status-docker`, `docker logs`, e checagem manual. Não há um único comando ou endpoint que teste: processo ativo, Telegram conectado, Groq (e/ou fallbacks) acessível, tools carregando. | Comando ou script “health” que verifique cada camada (processo, Telegram, LLM, tools) e devolva qual falhou. |
| ✅ **Diagnóstico** | “Mande a linha de erro e o OS; digo qual camada está faltando.” | erros.md/erros descrevem o problema de 429/fallback; não há um guia genérico de operador: “erro X → provável camada Y”. | Guia curto (ex.: em README ou COMECE_AQUI): tabela sintoma → camada provável (motor/gateway/LLM/habilidades) e o que checar. |
| ⚪ **Múltiplas UIs (opcional)** | UI de controle no navegador + gateway. | Uma única “UI”: app Telegram. | Não é obrigatório; só relevante se quiser painel web ou outro cliente além do Telegram. |

---

## Como funciona na realidade (modelo de 3 camadas)

O assistente pode ser visto como **três camadas**. Se algo falhar, a causa costuma ser uma delas (infraestrutura), não “a IA”.

| Camada | O que é | No ReqMind |
|--------|--------|------------|
| **1. Motor** | Processo que roda o cérebro do agente (LLM + tools). | Container Docker `assistente-bot` ou processo `bot_simple.py`. |
| **2. Gateway** | Canal por onde a UI fala com o motor. | Conexão do bot com o Telegram (long polling). |
| **3. Habilidades** | O que o agente pode fazer (tools). | Registry em `workspace/core/tools.py`; 14–15 ferramentas. |

**Fluxo:** `Telegram (UI) → Gateway (bot) → Motor (agent + LLM) → Habilidades (tools) → Resposta`

### Se falhou, qual camada?

| Sintoma | Camada provável | O que checar |
|---------|-----------------|--------------|
| Bot não inicia; "comando não encontrado" ou erro de Python | Motor | Container rodando? `make status-docker`. `.env` e dependências: `make install`, variáveis no Docker: `docker exec assistente-bot env \| grep -E 'TELEGRAM|GROQ'`. |
| Bot inicia mas não responde no Telegram; 409 Conflict | Gateway | Uma única instância por token? `make instancias`; parar outras com `make stop-docker` ou no outro PC. Token correto no `.env`. |
| Bot responde "limite de API" ou erro ao chamar ferramenta | Motor (LLM) ou Habilidades | 429: ver `erros.md` (fallbacks Kimi/GLM). Erro em tool: logs `docker logs assistente-bot` para "Executando: read_file" ou "tool_executada". |
| Resposta genérica ou errada (ex.: resumo de arquivo inventado) | Habilidades / prompt | Conteúdo retornado pela tool está sendo usado? Ver CONTEXT_PACK e regras em POLICIES/STYLE (resumo de arquivo). |

Use `make health` para verificar as camadas de uma vez (processo, env, carregamento do agente/tools).

---

## Resumo

✅ **Status v1.3 - TODOS OS ITENS OBRIGATÓRIOS COMPLETOS**

- ✅ **Temos:** motor (bot+agent+LLM), gateway implícito (Telegram), habilidades (tools), **cache LRU (v1.3)**, auth, fallbacks com retry/backoff, segurança, health check e documentação completa.
- ✅ **Completos:** (1) Modelo de 3 camadas documentado; (2) Health check unificado (`make health`); (3) Guia de diagnóstico "erro → camada".
- ⚪ **Opcionais:** (4) Gateway extra/API ou painel web — **só se quiser** múltiplos clientes além do Telegram.

Tratar o assistente como **infraestrutura em camadas** (motor / gateway / habilidades) ajuda a não atribuir tudo à "IA" quando o problema é serviço parado, env não carregado no Docker ou fallback não configurado.
