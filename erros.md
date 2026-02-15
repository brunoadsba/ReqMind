# Erros atuais do bot (teste via Telegram)

Documento para outra LLM ou desenvolvedor resolver o problema de fallbacks e leitura de arquivos quando a API Groq retorna 429.

---

## 1. Contexto

- **App:** Bot Telegram do projeto `assistente` (ReqMind/assistente).
- **Teste:** Usuário envia mensagem pelo Telegram; o bot processa via `handlers/message.py` → `agent.run()` → Groq (e fallbacks em caso de 429).

---

## 2. Comportamento observado

**Entrada (I):**  
`Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas.`

**Saída (O):**  
`Limite de uso da API atingido no momento. Tente novamente em cerca de 1 minuto. Quando retomar, tente: «O que você sabe sobre mim?» ou «Quais minhas preferências?». Perguntas que exigem leitura de arquivos não podem ser atendidas enquanto a API estiver indisponível.`

**Esperado:** O bot deveria (a) usar um fallback (Kimi ou GLM) e responder com um resumo do MEMORY.md, ou (b) pelo menos ler o arquivo e devolver conteúdo/resumo quando a API principal está em 429.

---

## 3. Causa raiz (resumo)

1. **Groq retorna 429** (rate limit / tokens per day).
2. **Fallbacks Kimi e GLM não estão produzindo resposta** no ambiente de execução (Docker): ou as chaves não chegam ao processo, ou as chamadas falham (timeout, rede, cota, formato de resposta).
3. **Fallback de memória (FactStore) é ignorado de propósito** quando a pergunta é “ler/resumir arquivo” (`_user_asked_to_read_file`), para não devolver fatos sobre o usuário em vez do conteúdo do arquivo.
4. **Não há caminho alternativo para “ler arquivo” em 429:** o agente não chama a tool `read_file` quando está em modo 429; só tenta Kimi → GLM → RAG (docs) → FactStore (exceto se for pergunta de arquivo) → mensagem de limite.

Resultado: em 429 + pergunta de leitura de arquivo, o usuário recebe só a mensagem de limite.

---

## 4. Fluxo de código relevante

- **Handler:** `src/handlers/message.py` → `handle_message()` chama `agent.run(user_message, history, user_id=...)`.
- **Agente:** `src/workspace/core/agent.py`:
  - `run()` monta `messages` e chama `llm_router.chat(messages, tools=schemas, ...)` (Groq).
  - Em `except Exception as e`:
    - `error_msg = str(e)`.
    - Se `_is_rate_limit_error(error_msg)`:
      - Ativa circuit breaker (`_groq_cooldown_until`).
      - Tenta **Kimi** (`nvidia_kimi_chat`) se `NVIDIA_API_KEY` existe e limite diário NVIDIA não atingido.
      - Tenta **GLM** (`glm_chat`) se `GLM_API_KEY` existe.
      - Tenta RAG de documentos (ex.: NR-29).
      - Se **não** for pergunta de leitura de arquivo (`_user_asked_to_read_file(user_message)`), tenta FactStore / fatos recentes.
      - Senão, retorna `rate_msg` (+ texto sobre leitura de arquivos).
  - Há um segundo caminho: quando o primeiro erro é tratado como **tool error** (`is_tool_error`), o agente tenta de novo **sem tools**; se essa segunda chamada der 429, entra em outro bloco que também tenta Kimi → GLM → memória e depois `rate_msg`.

- **Kimi:** `src/workspace/core/nvidia_kimi.py` → `chat_completion_sync(api_key, messages, ...)` → POST para NVIDIA NIM (Kimi K2.5). Retorna `None` em falha.
- **GLM:** `src/workspace/core/glm_client.py` → `chat_completion_sync(api_key, messages, ...)` → POST para Zhipu (ou `GLM_API_BASE_URL`) com modelo `glm-4.7-flash`. Usa `content` ou `reasoning_content` da resposta. Retorna `None` em falha.

- **Detecção de 429:** `_is_rate_limit_error(msg)` considera: `429`, `rate_limit`, `rate limit`, `rate_limit_exceeded`, `tokens per day`, `tpd`.

- **Detecção de “pergunta de arquivo”:** `_user_asked_to_read_file(msg)` considera: "leia o arquivo", "conteúdo do arquivo", "resuma o arquivo", ".md", ".txt", etc. Quando True, o agente **não** usa FactStore em 429 e adiciona a frase sobre “perguntas que exigem leitura de arquivos”.

---

## 5. Por que os fallbacks podem não estar funcionando

- **Variáveis de ambiente no Docker:** O bot é iniciado com `docker run --env-file .env`. Se `NVIDIA_API_KEY` ou `GLM_API_KEY` não estiverem em `.env` ou estiverem com nome/valor errado (espaços, aspas), os fallbacks são pulados. Logs adicionados: `fallback_429 nvidia_key_presente=... glm_key_presente=...`, `fallback_kimi_pulado sem_nvidia_key`, `fallback_glm_pulado sem_glm_key`.
- **Kimi falha:** Timeout (20s), limite diário NVIDIA, rede, ou resposta sem `content`. Log: `Fallback Kimi K2.5 falhou: ...`.
- **GLM falha:** Timeout (25s), URL/modelo errado, rede, ou resposta vazia (`content` e `reasoning_content` vazios). Log: `Fallback GLM falhou: ...`.
- **Ordem:** Sempre Kimi primeiro, depois GLM. Se Kimi estiver configurado mas falhar, GLM é tentado; se ambos falharem, cai em RAG/memória ou em `rate_msg`.

---

## 6. Como diagnosticar

1. Reproduzir: enviar pelo Telegram uma mensagem que dispare o agente (ex.: “Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas”) quando o Groq estiver em 429.
2. Ver logs do container:  
   `docker logs assistente-bot --tail 150`
3. Procurar:
   - `llm_rate_limit provider=groq` → confirma 429.
   - `fallback_429 nvidia_key_presente=... glm_key_presente=...` → indica se as chaves estão presentes no processo.
   - `fallback_kimi_pulado sem_nvidia_key` / `fallback_glm_pulado sem_glm_key` → chave ausente.
   - `tentando_fallback_glm` → GLM foi tentado.
   - `Fallback Kimi K2.5 falhou:` / `Fallback GLM falhou:` → exceção/erro na chamada.
4. Se as chaves estiverem presentes e ainda assim a resposta for a mensagem de limite, inspecionar o texto da exceção (Kimi/GLM) nos logs e a resposta HTTP (status, body) dos clientes em `nvidia_kimi.py` e `glm_client.py`.

---

## 7. O que precisa ser resolvido

**A. Fazer os fallbacks funcionarem em 429 (prioritário)**  
- Garantir que `NVIDIA_API_KEY` e/ou `GLM_API_KEY` cheguem ao processo no Docker (`.env` correto, sem aspas/espacos desnecessários).  
- Se as chaves estiverem corretas e Kimi/GLM ainda falharem: tratar timeout, status HTTP e corpo da resposta nos clientes; ajustar URL/modelo do GLM se o provedor for outro; considerar retry com backoff.  
- Opcional: em 429, logar resposta bruta (ou status code) de Kimi/GLM para diagnóstico.

**B. Melhorar o caso “ler arquivo” em 429**  
- **Opção 1:** Em 429, quando `_user_asked_to_read_file(user_message)` for True, **chamar a tool `read_file`** para o arquivo mencionado (extrair path da mensagem, ex.: MEMORY.md), e devolver algo como: “API indisponível no momento. Conteúdo do arquivo solicitado (sem resumo): …” com o texto lido (ou truncado), em vez de só a mensagem de limite.  
- **Opção 2:** Manter o comportamento atual (só mensagem de limite) mas garantir que pelo menos um dos fallbacks (Kimi ou GLM) funcione, para que a outra LLM possa responder (e eventualmente chamar tools se o fallback suportar no futuro).

---

## 8. Arquivos principais

| Arquivo | Uso |
|--------|-----|
| `src/handlers/message.py` | Entrada da mensagem Telegram → `agent.run()` |
| `src/workspace/core/agent.py` | Loop do agente, 429, fallbacks Kimi/GLM, RAG, FactStore, `_user_asked_to_read_file`, `_is_rate_limit_error` |
| `src/workspace/core/llm_router.py` | Chamada Groq (origem do 429) |
| `src/workspace/core/nvidia_kimi.py` | Fallback Kimi (síncrono, sem tools) |
| `src/workspace/core/glm_client.py` | Fallback GLM (síncrono, sem tools) |
| `src/workspace/tools/filesystem.py` | `read_file` (path validado por `config.BASE_DIR` / allowlist) |
| `src/config/settings.py` | `config.BASE_DIR`, etc. |
| `.env` | `GROQ_API_KEY`, `NVIDIA_API_KEY`, `GLM_API_KEY` (e opcionalmente `GLM_API_BASE_URL`, `GLM_MODEL`) |

---

## 9. Reprodução mínima

1. Colocar o Groq em 429 (muitas requisições ou limite TPD).
2. No Telegram, enviar: `Leia o conteúdo do arquivo MEMORY.md e resuma os principais blocos em até 10 linhas.`
3. Observar: a resposta é a mensagem de limite com a frase sobre “perguntas que exigem leitura de arquivos”.
4. Corrigir: fazer Kimi ou GLM responder em 429 **ou** implementar leitura de arquivo em 429 para perguntas de arquivo (conforme seção 7).

---

## 10. Verificação da correção

- Com 429 forçado (ou ao atingir limite), enviar a mesma pergunta pelo Telegram.
- **Sucesso:** resposta com conteúdo útil (resumo do MEMORY.md vindo do fallback **ou** conteúdo do arquivo lido por `read_file` em 429).
- **Logs:** `llm_resposta_fallback provider=nvidia` ou `provider=glm`, ou log explícito de “read_file em 429 para arquivo X”.
