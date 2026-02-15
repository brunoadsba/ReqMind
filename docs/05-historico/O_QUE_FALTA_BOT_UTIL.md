# O que falta para o bot ser realmente útil

Visão objetiva: o que já entrega valor e o que falta para você usar o bot no dia a dia com confiança.

---

## O que já ajuda hoje

- Chat com IA (Groq), busca web, leitura/escrita de arquivos, clima, notícias.
- Notícias diárias às 7h (se o bot estiver rodando).
- Lembretes (create_reminder) com notificação por Telegram (e email se configurado).
- Análise de imagem, vídeo, áudio (transcrição).
- Memória (FactStore + RAG): preferências, NR-29, etc.
- Em 429: leitura direta de arquivo (implementado); fallbacks Kimi/GLM (podem não responder no Docker).

---

## O que falta (por impacto)

### 1. Confiabilidade quando o Groq está em 429 (alto impacto)

**Problema:** No Docker, Kimi e GLM muitas vezes não devolvem resposta (chaves não chegam, timeout ou erro de API). Em 429 você fica só com mensagem de limite ou com o conteúdo bruto do arquivo (se for pergunta de leitura).

**O que falta:** Garantir que os fallbacks funcionem no ambiente onde o bot roda:
- Confirmar que `NVIDIA_API_KEY` e `GLM_API_KEY` estão no container (`docker exec assistente-bot env | grep -E 'NVIDIA|GLM'`) e sem aspas no `.env`.
- Ver nos logs o motivo da falha (`Fallback Kimi falhou (Status ...)` ou `Timeout`); corrigir rede, cota ou URL/modelo do GLM.
- Opcional: retry com backoff nos clientes Kimi/GLM.

**Resultado:** Com fallbacks estáveis, o bot continua respondendo (com outra LLM) quando o Groq atinge o limite.

---

### 2. Uso recorrente claro (médio impacto)

**Problema:** O bot tem muitas ferramentas, mas não fica óbvio “o que pedir” no dia a dia.

**O que falta:** Um guia curto para o usuário final (você), por exemplo em `README` ou `COMECE_AQUI`:
- Exemplos: “Resuma o arquivo X”, “O que você sabe sobre mim?”, “Lembrete daqui 2 horas: ligar para Y”, “Notícias de Ilhéus”, “Clima em Salvador”.
- Comandos úteis: `/noticias`, `/status`, `/clear`.
- Uma linha: “Notícias às 7h e lembretes só funcionam com o bot rodando (ex.: `make start-docker`).”

**Resultado:** Você sabe quando e como usar o bot sem reler documentação técnica.

---

### 3. Lembretes que você confia (médio impacto)

**Problema:** Lembretes existem (create_reminder + ReminderNotifier), mas dependem de env (Telegram sempre; email se tiver SMTP_*). Não fica claro se estão sendo disparados.

**O que falta:**
- Documentar no README ou COMECE_AQUI: “Lembretes: o bot envia no Telegram; para email, configure EMAIL_ADDRESS, SMTP_SERVER, SMTP_PORT, SMTP_PASSWORD.”
- Opcional: comando `/lembretes` para listar os próximos lembretes (se a tool ou o storage expuser isso).

**Resultado:** Você usa lembretes sem dúvida se estão ativos e como configurá-los.

---

### 4. Memória presente nas respostas (médio impacto)

**Problema:** FactStore e memória RAG existem e são usados no sistema (ex.: contexto no prompt). Mas a sensação de “ele lembra de mim” depende de o modelo realmente usar esse contexto nas respostas.

**O que falta:**
- Validar na prática: perguntar “O que você sabe sobre mim?” e “Quais minhas preferências?” e ver se a resposta reflete o que está no FactStore.
- Se não refletir: revisar como o `memory_context` é montado e injetado no system prompt; eventualmente aumentar relevância (mais fatos ou melhor query).

**Resultado:** O bot demonstra de forma clara que usa o que “sabe” sobre você.

---

### 5. Bot sempre ligado (baixo impacto se você já usa Docker)

**Problema:** Notícias às 7h e lembretes só funcionam com o processo ativo. Se a máquina desliga ou o container cai, não há envio.

**O que falta:** Garantir que o bot sobe ao ligar o servidor (ex.: systemd ou cron com `make start-docker`) ou aceitar que roda só quando a máquina está ligada. Opcional: health check periódico ou restart automático (Docker restart policy, systemd, etc.).

**Resultado:** Notícias e lembretes passam a ser confiáveis no dia a dia.

---

### 6. Respostas mais rápidas (baixo impacto)

**Problema:** Chamadas ao Groq + tool calling podem levar vários segundos.

**O que falta:** Otimizações opcionais: cache para perguntas repetidas, respostas diretas para perguntas muito simples (já existe para data/hora), ou modelo mais leve para tarefas simples. Não é bloqueante para “ser útil”.

---

## Resumo prático

| Prioridade | O que fazer |
|------------|-------------|
| **Alta** | Fazer Kimi/GLM funcionarem no Docker (env + logs + ajustes de rede/modelo). |
| **Média** | Guia de uso para o usuário (exemplos do que pedir + comandos); documentar lembretes; validar “O que você sabe sobre mim?”. |
| **Baixa** | Bot sempre ligado (systemd/restart); opcionalmente velocidade (cache, etc.). |

Com fallbacks estáveis e um uso recorrente claro (guia + lembretes documentados), o bot passa a ser realmente útil no dia a dia.
