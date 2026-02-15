# Análise crítica: teste-pratico.md vs result.json (limite de API)

**Data:** 2026-02-06  
**Contexto:** Testes realizados a partir de `teste-pratico.md`; export do chat em `result.json`. O limite de chamadas da API (Groq) foi atingido durante os testes.

---

## 1. O que foi executado (ordem no chat)

| # | Seção teste-pratico | Prompt (resumido) | Resultado |
|---|---------------------|-------------------|-----------|
| 1 | - | `/start` | OK – mensagem de boas-vindas |
| 2 | 1.1 Chat básico | Memória RAG e onde é usada no bot | OK – resposta longa e correta |
| 3 | 1.2 Resposta em áudio | Resumo 30s em áudio | **Falha** – texto OK; áudio: "Não foi possível gerar o áudio" |
| 4 | 1.3 Contexto pessoal | O que você sabe sobre mim? | **Falha** – "não tenho informações suficientes" (memória não usada) |
| 5 | 2.1 Busca web | Python 3.12, resumo em tópicos | OK |
| 6 | 2.2 Busca web | Notícias de tecnologia, 5 bullets | OK |
| 7 | 3.1 Salvar memória | Preferências (direto, pt-BR, código, segurança do trabalho) | OK |
| 8 | 3.2 Resgatar memória | O que tem salvo sobre preferências? | OK – listou as preferências |
| 9 | 3.3 RAG NR-29 | Principais pontos NR-29 segurança portuária | OK – resumo coerente (pode ser conhecimento do modelo ou RAG) |
| 10 | 4.1 Listar diretório | Arquivos do diretório atual + docs | **Parcial** – resposta plausível mas estrutura errada (clawd, ReqMind, assistente como “arquivos”; README, STYLE, IDENTITY) |
| 11 | 4.2 Ler arquivo | Ler MEMORY.md e resumir em 10 linhas | **Limite de API** – "Limite de uso da API atingido. Tente novamente em cerca de 31 minutos." |

Ou seja: o limite foi atingido **na 11ª interação** (leitura de MEMORY.md). Tudo que vem depois no `teste-pratico.md` (mais arquivos, Git, mídia, transcrição, clima, gráficos, imagens, segurança) **não chegou a ser testado** nessa sessão.

---

## 2. Análise crítica

### 2.1 Limite de API (Groq)

- **Causa:** Várias mensagens seguidas, cada uma com contexto grande (histórico + tool calling + respostas longas), consomem muitos tokens. O tier free do Groq tem limite de requisições/minuto (e possivelmente diário).
- **Efeito:** Sessão de teste interrompida antes de cobrir a maior parte do `teste-pratico.md`.
- **Recomendações:**
  - **teste-pratico.md:** Dividir em blocos (ex.: “Bloco A: 1–3”, “Bloco B: 4–5”) e sugerir pausa de 1–2 minutos entre blocos, ou rodar em dias/horários diferentes.
  - **Quotas no código:** Já existem `LLM_GROQ_DAILY_LIMIT_TOKENS` e fallback Kimi/RAG; garantir que, ao atingir limite, a mensagem exibida seja clara e que o fallback seja tentado quando fizer sentido (ex.: perguntas que podem ser respondidas por RAG).
  - **Uso em teste:** Para bater ponto a ponto no doc, considerar rodar poucos prompts por sessão (ex.: 5–7) e depois pausar.

### 2.2 Resposta em áudio (TTS)

- **Observado:** O modelo respondeu em texto dizendo que não pode produzir áudio; em seguida a aplicação enviou "Não foi possível gerar o áudio." (fluxo de TTS falhou).
- **Provável causa:** ElevenLabs não configurado (`ELEVENLABS_API_KEY`) ou falha na chamada (rede, cota, formato).
- **Recomendações:**
  - Documentar em `teste-pratico.md` que “resposta em áudio” depende de ElevenLabs configurado.
  - Se TTS falhar, evitar enviar duas mensagens (texto do modelo + “não foi possível áudio”); unificar em uma única mensagem de erro ou resposta em texto.

### 2.3 “O que você sabe sobre mim?”

- **Observado:** Bot respondeu que não tem informações suficientes sobre o usuário, mesmo após ter sido rodado `init_user_memory.py` com fatos sobre Bruno.
- **Provável causa:** O contexto de memória (FactStore / `get_relevant_memory`) não está sendo injetado no prompt do agente para essa pergunta, ou a query de busca não retorna os fatos (ex.: “Bruno” não no contexto da mensagem).
- **Recomendações:**
  - Garantir que, em toda mensagem do usuário, o Agent chame `get_relevant_memory(user_message)` e injete o resultado no system/user context enviado ao LLM.
  - Incluir no contexto do sistema algo como “Fatos sobre o usuário (se houver): …” quando houver resultado da memória.
  - Revisar se o path do `FactStore` no Docker é o mesmo que o usado em desenvolvimento (volume `dados/` e qualquer path de memória em `workspace`).

### 2.4 Listar diretório (4.1)

- **Observado:** Bot listou README, STYLE, IDENTITY, clawd, ReqMind, assistente, requirements.txt, setup.py e destacou README, STYLE, IDENTITY como documentação.
- **Problema:** No repositório atual, o “diretório atual do projeto” deveria ser algo como `assistente/` (onde estão `src/`, `docs/`, `teste-pratico.md`, `README.md`, etc.). Não existe `STYLE.md` ou `IDENTITY.md` na raiz do `assistente`; eles estão em `src/workspace/agent/`. Ou o bot listou outro diretório (ex.: home ou raiz do ReqMind), ou interpretou mal o resultado da tool.
- **Recomendações:**
  - Garantir que “diretório atual do projeto” seja definido de forma explícita (ex.: `MOLTBOT_DIR` ou `BASE_DIR`) e que a tool `list_directory` seja chamada com esse path quando o usuário disser “diretório atual do projeto”.
  - No `teste-pratico.md`, ser explícito: “Liste os arquivos do diretório **assistente** (raiz do bot)” ou “do diretório definido como oficial do projeto”.

### 2.5 Cobertura do teste-pratico.md

- **Coberto nesta sessão:** Seções 1 (parcial), 2, 3 e início da 4.
- **Não coberto por causa do limite:** Restante da 4 (ler arquivo, escrever), 5 (código/Git), 6 (mídia), 7 (transcrição), 8 (clima, notícias, lembretes), 9 (gráficos), 10 (gerar imagens), 11 (segurança/sanitização).
- **Recomendações:**
  - Incluir no próprio `teste-pratico.md` um aviso: “Muitos prompts em sequência podem atingir o limite da API Groq. Recomenda-se testar em blocos com pausa entre eles.”
  - Opcional: criar um “teste-pratico-minimo.md” com 5–7 prompts que validam o essencial (1 chat, 1 web, 1 memória, 1 arquivo, 1 comando) para uma rodada rápida sem estourar limite.

---

## 3. Resumo

| Aspecto | Situação | Ação sugerida |
|--------|----------|----------------|
| Limite Groq | Atingido na 11ª mensagem; teste interrompido | Blocos no doc + pausas; mensagem clara; fallback Kimi/RAG quando aplicável |
| TTS (áudio) | Falhou; duas mensagens (texto + erro) | Documentar dependência ElevenLabs; unificar mensagem de erro |
| Memória do usuário | “Não tenho informações” sobre você | Garantir injeção de `get_relevant_memory` no contexto do Agent |
| Listar diretório | Resposta com paths/nomes estranhos | Fixar “diretório do projeto” e usar na tool; clarificar no doc |
| Cobertura do doc | ~40% testado; 60% não executado | Aviso no doc; opcional “teste mínimo” |

O `result.json` confirma que o fluxo do bot e as respostas até o momento do rate limit estão coerentes com o desenho (incluindo mensagem de limite). A análise acima aponta ajustes no desenho do teste (doc + uso de memória + diretório) e na operação (limite e TTS) para alinhar melhor o teste prático à realidade do bot e ao limite da API.
