## Plano de Melhoria do Bot (Uso Pessoal, Multi‑LLM e Limites de Tokens)

### 1. Objetivo

Organizar as próximas evoluções do Assistente Digital mantendo o **foco em uso pessoal (um único usuário)**, reduzindo riscos de erros operacionais e melhorando o uso de **múltiplas LLMs com limites de tokens/quotas**.

---

### 2. Fase 1 – Consolidar ambiente e operação

**Meta:** evitar divergência de código, múltiplas instâncias e confusão de ambientes.

1. **Escolher diretório oficial do projeto**
   - Definir um único diretório como fonte da verdade do código (ex.: `Assistente-Digital/assistente`).
   - Ajustar `config/settings.py` (`MOLTBOT_DIR`, `DATA_DIR`, `TEMP_DIR`) para apontar para esse diretório.

2. **Padronizar scripts de start/stop/status**
   - Garantir que todos os comandos (`make start/stop/status`) usem sempre os scripts seguros (`start_bot_safe.sh`, `stop_bot.sh`, `healthcheck.sh`), apontando para o diretório oficial.
   - Remover ou desestimular rotas alternativas antigas (execução manual em outros diretórios).

3. **Unificar ambiente Python**
   - Escolher um único `venv` (ex.: `venv` ou `venv311`) para testes e produção.
   - Atualizar `README.md`, `MEMORY.md` e scripts para usar sempre esse venv.

4. **Eliminar cópia manual de código para execução**
   - Rodar o bot diretamente do diretório oficial.
   - Se ainda for necessário sync para outro local, criar script explícito (ex.: `make deploy-local`) documentado.

---

### 3. Fase 2 – Multi‑LLM e limites de tokens

**Meta:** reduzir dependência de um único provedor de LLM e controlar melhor consumo de tokens por dia/contexto.

#### 3.1. Roteador de LLMs (`llm_router`)

1. **Criar módulo de roteamento**
   - Novo arquivo sugerido: `src/workspace/core/llm_router.py`.
   - Interface única para o Agent:
     - `async def chat(messages, tools=None, tool_choice="auto", max_tokens=None, user_id=None) -> LLMResponse`.

2. **Implementar clientes por provedor**
   - `GroqChatClient`: encapsula chamadas atuais (chat + tool calling).
   - `NvidiaKimiClient`: encapsula fallback atual (Kimi K2.5).
   - Opcional: espaço para futuro terceiro provedor (ex.: OpenRouter), mantendo a mesma interface.

3. **Configurar provedores e modelos em `config/settings.py`**
   - Lista ordenada de provedores: `LLM_PROVIDERS_ORDER = ["groq", "nvidia"]`.
   - Constantes de modelos por tipo:
     - `GROQ_MODEL_CHAT`, `GROQ_MODEL_VISION`, `GROQ_MODEL_WHISPER`.
     - `NVIDIA_MODEL_CHAT` (Kimi K2.5), etc.
   - Metadados por provedor:
     - se suporta tool calling,
     - limites de tokens por requisição (aprox.),
     - timeouts.

#### 3.2. Controle de quota/limite diário

4. **Registrar consumo de tokens por provedor/dia**
   - Criar tabela em SQLite ou JSON em `DATA_DIR` com:
     - `provider`, `date`, `input_tokens`, `output_tokens`.
   - Após cada chamada, registrar estimativa de tokens consumidos (pelo menos aproximada via contagem de caracteres).

5. **Expor limites via configuração**
   - Novas configs, por exemplo:
     - `LLM_GROQ_DAILY_LIMIT_TOKENS`
     - `LLM_NVIDIA_DAILY_LIMIT_TOKENS`
   - Valores ajustáveis via `.env`.

6. **Política de seleção de provedor**
   - Fluxo básico:
     1. Ler `LLM_PROVIDERS_ORDER`.
     2. Filtrar provedores com **saldo de tokens diário** e não marcados como degradados.
     3. Escolher o primeiro que suporta o tipo de chamada (com/sem tools).
     4. Em erro 429/5xx, marcar provedor como degradado por N minutos e tentar o próximo.

7. **Comportamento quando todos os provedores estiverem indisponíveis**
   - Se a pergunta estiver claramente coberta pelo RAG (ex.: normas, NR‑29), usar `rag_search` e responder com o conteúdo da memória.
   - Caso contrário, responder explicitamente que o limite diário de uso foi atingido e sugerir tentar novamente mais tarde.

#### 3.3. Controle de contexto e tamanho de prompt

8. **Utilitário de truncamento de histórico**
   - Criar função de utilidade (por exemplo em `agent.py` ou módulo auxiliar) que:
     - receba histórico de mensagens, limites de contexto e tamanho máximo de resposta,
     - devolva subconjunto/truncamento do histórico respeitando fronteira de mensagens ou resumo.

9. **Integrar truncamento no `Agent.run()`**
   - Antes de chamar `llm_router.chat`, sempre passar pelo truncador de contexto.
   - Configurar limites em `config/settings.py` (ex.: `MAX_CONTEXT_TOKENS_CHAT` por modelo).

---

### 4. Fase 3 – Storage e lembretes

**Meta:** manter simplicidade, mas evitar perda de dados e dependência de `/tmp`.

1. **Migrar lembretes para storage persistente**
   - Trocar `/tmp/moltbot_reminders.json` por:
     - arquivo JSON em `DATA_DIR` **ou**
     - tabela `reminders` no SQLite já existente.
   - Atualizar o sistema de lembretes para ler/escrever nesse storage persistente.

2. **Padronizar dados em `DATA_DIR`**
   - Garantir que:
     - `memory.json` (RAG),
     - banco SQLite,
     - lembretes
     fiquem sob `config.DATA_DIR`.

3. **Script/comando simples de backup**
   - Adicionar alvo no `Makefile` (ex.: `make backup`) que:
     - cria `backups/AAAAMMDD-HHMM/`,
     - copia `DATA_DIR` para dentro desse diretório.
   - Solução leve, suficiente para uso pessoal.

---

### 5. Fase 4 – Testes mínimos e observabilidade

**Meta:** garantir que as mudanças em multi‑LLM e storage não quebrem o bot sem aviso.

1. **Testes unitários para o roteador de LLMs**
   - Novos testes (ex.: `tests/test_llm_router.py`):
     - escolhe provedor correto conforme saldo diário,
     - marca provedor como degradado em 429/5xx,
     - cai para próximo provedor,
     - comporta‑se corretamente quando todos estão indisponíveis.

2. **Testes para lembretes com storage persistente**
   - Validar:
     - criação,
     - leitura,
     - disparo em horário correto,
     - remoção após envio.

3. **Ajustar comandos de teste oficiais**
   - Padronizar `make test` para rodar:
     - testes E2E simples,
     - testes de segurança,
     - novos testes de `llm_router` e lembretes.
   - Manter, se necessário, um alvo separado (`make test-full`) para a suíte mais pesada.

4. **Logs específicos para rotação de LLMs**
   - Incluir, nos logs:
     - provedor escolhido (“groq”, “nvidia”, etc.),
     - motivo de fallback (quota, erro, indisponibilidade),
     - estimativa de tokens consumidos na chamada.
   - Facilita calibração futura dos limites (`LLM_*_DAILY_LIMIT_TOKENS`).

---

### 6. Fase 5 – Refinos opcionais

1. **Melhorias graduais no RAG**
   - Quando fizer sentido, usar embeddings locais (por exemplo com Chromadb já listado em dependências) mantendo o foco em volume pequeno/médio.

2. **Empacotamento leve**
   - Docker simples apenas para garantir reprodutibilidade entre máquinas/ambientes, sem transformar o projeto em serviço público.

---

### 7. Ordem sugerida de execução

1. Consolidar diretório oficial, venv e scripts de start/stop (Fase 1).
2. Introduzir `llm_router` e adaptar o `Agent` para usá‑lo inicialmente só com Groq.
3. Ativar rotação entre Groq e NVIDIA com controle de tokens/quotas (Fase 2 completa).
4. Migrar lembretes para storage persistente e criar `make backup` (Fase 3).
5. Adicionar testes específicos para `llm_router` e lembretes, além de logs de rotação de LLMs (Fase 4).

