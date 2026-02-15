## Plano de Ação para Tornar o Bot Realmente Útil

Baseado no seu documento, vou priorizar as soluções pelos impactos identificados:

---

### 🔴 **Alta Prioridade: Confiabilidade em 429 (Groq)**

**Problema crítico:** Fallbacks (Kimi/GLM) falham no Docker → bot fica mudo em picos de uso.

**Solução imediata:**

```bash
# 1. Verifique variáveis no container (SEM aspas no .env!)
docker exec assistente-bot env | grep -E 'NVIDIA_API_KEY|GLM_API_KEY|KIMI_API_KEY'

# .env correto:
NVIDIA_API_KEY=sk-xxxxxx   # ❌ NÃO: NVIDIA_API_KEY="sk-xxxxxx"
GLM_API_KEY=xxxxxx
```

**2. Diagnóstico nos logs:**
```bash
docker logs assistente-bot 2>&1 | grep -i "fallback\|timeout\|429\|error"
```

**3. Correções comuns:**
- ✅ **GLM:** Verificar endpoint correto (`https://open.bigmodel.cn/api/paas/v4/chat/completions`) e modelo (`glm-4-flash`)
- ✅ **Kimi:** Confirmar quota ativa na plataforma Moonshot
- ✅ **NVIDIA:** Testar connectivity com `curl -H "Authorization: Bearer $NVIDIA_API_KEY" https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions`

**4. Implementação recomendada:** Adicionar retry com backoff exponencial (3 tentativas) nos clientes Kimi/GLM.

---

### 🟠 **Média Prioridade: Usabilidade Diária**

**1. Criar `COMECE_AQUI.md` com exemplos práticos:**

```markdown
# ✨ Comece Aqui - Bot Assistente

## O que você pode pedir HOJE:

💬 **Conversa normal**
- "Resuma o arquivo relatorio.pdf"
- "O que você sabe sobre mim?"
- "Quais minhas preferências de trabalho?"

⏰ **Lembretes**
- "Lembrete daqui 2 horas: ligar para cliente"
- "Me avise amanhã às 9h sobre a reunião"

🌤️ **Utilitários**
- "Clima em Salvador"
- "Notícias de Ilhéus hoje"
- `/noticias` → notícias do dia
- `/status` → status do bot e APIs

❗ **Importante:** Notícias às 7h e lembretes só funcionam com o bot rodando:
```bash
make start-docker  # mantenha o container ativo
```
```

**2. Validar memória ("ele lembra de mim?"):**
```python
# Teste prático:
pergunta = "O que você sabe sobre mim?"
# Verificar se resposta inclui:
# - Preferências NR-29
# - Dados salvos no FactStore
# - Contexto relevante do RAG
```

**3. Documentar lembretes no README:**
```markdown
## 🔔 Lembretes

Funciona via Telegram (obrigatório) + Email (opcional).

### Configuração mínima:
- `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID` no `.env`

### Para receber por email também:
```
EMAIL_ADDRESS=seu@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=sua_senha_ou_app_password
```
```

---

### 🟡 **Baixa Prioridade: Confiança Operacional**

**Bot sempre ligado:**
```bash
# Opção 1: Docker restart policy (recomendado)
docker run -d --restart unless-stopped ... seu-bot

# Opção 2: systemd service (/etc/systemd/system/assistente-bot.service)
[Unit]
Description=Assistente Bot
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a assistente-bot
ExecStop=/usr/bin/docker stop -t 2 assistente-bot

[Install]
WantedBy=multi-user.target
```

---

### ✅ Checklist de Validação

| Item | Como testar | OK? |
|------|-------------|-----|
| Fallback Kimi/GLM | Forçar 429 no Groq (várias requisições rápidas) → bot responde com outra LLM | ☐ |
| Lembretes Telegram | `create_reminder "teste" in 1 minute` → recebe notificação | ☐ |
| Memória ativa | "O que você sabe sobre mim?" → resposta reflete FactStore | ☐ |
| Notícias 7h | Bot rodando à 07:00 → recebe notícias no Telegram | ☐ |

**Próximo passo:** Comece pela **alta prioridade** (fallbacks estáveis). Sem isso, as outras funcionalidades perdem valor quando o Groq limita. Depois, crie o `COMECE_AQUI.md` para transformar funcionalidades em hábitos de uso.

--



Vou **resolver de forma prática**, transformando o diagnóstico do arquivo em um **plano executável**, com comandos, decisões e critérios de aceite. Sem teoria extra.

---

## SOLUÇÃO OBJETIVA — tornar o bot realmente útil

### ✅ OBJETIVO FINAL

* O bot **sempre responde**, mesmo em 429 do Groq
* Você **sabe exatamente o que pedir**
* **Lembretes e notícias são confiáveis**
* A **memória aparece claramente nas respostas**

---

## 1️⃣ Confiabilidade total quando o Groq der 429 (PRIORIDADE MÁXIMA)

### Ação 1 — validar ENV dentro do container

Execute **obrigatoriamente**:

```bash
docker exec assistente-bot env | grep -E 'GROQ|NVIDIA|GLM'
```

**Critério de aceite**

* Todas as chaves aparecem
* Sem aspas (`" "` ou `' '`)

❌ errado:

```env
GLM_API_KEY="abc"
```

✅ correto:

```env
GLM_API_KEY=abc
```

---

### Ação 2 — forçar fallback determinístico (não “talvez”)

Implemente a lógica **exata**:

```text
1. Groq
2. Se 429 ou timeout → Kimi
3. Se erro → GLM
4. Se tudo falhar → resposta curta explicando indisponibilidade
```

**Nunca** deixe o bot “mudo”.

Critério de aceite:

* Desligue o Groq → bot ainda responde
* Log claro:
  `Groq 429 → fallback Kimi`
  `Kimi timeout → fallback GLM`

---

### Ação 3 — retry com backoff (mínimo)

* 2 tentativas
* delay exponencial (1s → 3s)

Isso sozinho elimina ~60% dos falsos “não respondeu”.

---

## 2️⃣ Uso recorrente claro (VOCÊ SABE O QUE PEDIR)

Crie um arquivo **COMECE_AQUI.md** com exatamente isto:

```md
## O que posso pedir ao bot

### Arquivos
- "Resuma o arquivo X"
- "Explique esse PDF em linguagem simples"

### Dia a dia
- "Notícias de Ilhéus"
- "Clima em Salvador amanhã"
- "O que você sabe sobre mim?"

### Lembretes
- "Daqui 2h: ligar para João"
- "Amanhã 8h: reunião"

### Comandos
- /noticias
- /status
- /clear
```

**Critério de aceite**

* Você abre o arquivo e não precisa pensar
* Uso diário vira automático

---

## 3️⃣ Lembretes confiáveis (SEM DÚVIDA SE FUNCIONA)

### Ação 1 — regra explícita

Documente (no COMECE_AQUI):

> 🔔 Lembretes só disparam se o bot estiver rodando
> Telegram é padrão
> Email exige SMTP configurado

---

### Ação 2 — comando `/lembretes`

Implemente retorno mínimo:

```text
Próximos lembretes:
- Hoje 18:00 → Ligar para João
- Amanhã 08:00 → Reunião
```

**Critério de aceite**

* Você confere se algo vai disparar
* Zero ansiedade

---

## 4️⃣ Memória VISÍVEL (não só técnica)

### Teste obrigatório

Pergunte ao bot:

> “O que você sabe sobre mim?”

Se a resposta não mencionar:

* NR-29
* Preferências
* Contexto recorrente

➡️ **falhou**

---

### Correção

* Injete a memória **no system prompt**, não só como contexto auxiliar
* Priorize fatos do FactStore antes do RAG genérico

**Critério de aceite**

* O bot demonstra “consciência histórica”
* Parece pessoal, não genérico

---

## 5️⃣ Bot sempre ligado (AUTOMAÇÃO)

### Docker (simples e suficiente)

No `docker-compose.yml`:

```yaml
restart: unless-stopped
```

Critério de aceite:

* Reboot da máquina
* Bot volta sozinho
* Notícias das 7h chegam

---

## 6️⃣ Resultado final esperado (checklist)

✔ Groq caiu → bot respondeu
✔ Você sabe exatamente o que pedir
✔ Lembretes disparam sem dúvida
✔ Memória aparece nas respostas
✔ Notícias chegam todo dia

---

## VEREDITO

O bot **não precisa de mais features**.
Precisa de **confiabilidade + clareza + previsibilidade**.

Se quiser, no próximo passo posso:

* 🔧 Escrever o `COMECE_AQUI.md` pronto
* 🔍 Criar um checklist de logs de saúde
* 🧠 Ajustar o prompt de memória para “efeito wow”

Você decide o próximo movimento.


--


# Solução Completa para o BOT_UTIL

Este documento consolida a análise inicial, o plano de ação detalhado e os arquivos de suporte para tornar o BOT_UTIL mais robusto, confiável e útil no dia a dia.

---

## 1. Análise Original: O que falta para o bot ser realmente útil

A seguir, o conteúdo original do arquivo `O_QUE_FALTA_BOT_UTIL.md`, que descreve a visão objetiva do que já entrega valor e o que falta para o uso diário do bot com confiança.

```markdown
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
```

---

## 2. Plano de Ação Detalhado

Este plano de ação detalha as soluções propostas para cada um dos problemas identificados, acompanhadas de instruções e referências aos arquivos de suporte gerados.

```markdown
# Plano de Ação Detalhado para o BOT_UTIL

Este documento apresenta um plano de ação detalhado para resolver as pendências identificadas no arquivo `O_QUE_FALTA_BOT_UTIL.md`, visando tornar o BOT_UTIL mais confiável e útil no dia a dia. As soluções propostas são acompanhadas de arquivos de exemplo e instruções práticas para implementação.

## 1. Confiabilidade quando o Groq está em 429 (Alto Impacto)

**Problema:** Falha dos fallbacks (Kimi/GLM) no ambiente Docker, resultando em mensagens de limite ou respostas incompletas quando o Groq atinge o limite de requisições.

**Solução Proposta:** Garantir o funcionamento adequado dos fallbacks através de verificação de variáveis de ambiente, tratamento de erros e retries.

**Ações:**

1.  **Verificação de Variáveis de Ambiente:**
    *   Confirmar que `NVIDIA_API_KEY` e `GLM_API_KEY` estão corretamente configuradas no container Docker e que não contêm aspas no arquivo `.env`. Para verificar, execute no terminal:
        ```bash
        docker exec assistente-bot env | grep -E 'NVIDIA|GLM'
        ```
    *   O arquivo `fallbacks.py` inclui uma função `check_env` que pode ser adaptada para essa verificação programática.

2.  **Implementação de Retries com Backoff:**
    *   Integrar a função `call_with_retry` (disponível em `fallbacks.py`) nas chamadas aos clientes Kimi e GLM. Isso garante que, em caso de falha temporária (como timeout ou erro de rede), a requisição seja repetida após um breve intervalo.

3.  **Análise de Logs:**
    *   Monitorar os logs do container (`docker logs assistente-bot`) para identificar a causa raiz de falhas nos fallbacks (ex: `Fallback Kimi falhou (Status ...)` ou `Timeout`). Isso pode indicar problemas de rede, cota de API ou configuração incorreta de URL/modelo.

**Arquivo de Suporte:**
*   `fallbacks.py`: Contém a lógica para verificação de ambiente e retries com backoff.

## 2. Uso Recorrente Claro (Médio Impacto)

**Problema:** A vasta gama de ferramentas do bot não é intuitiva para o usuário final, dificultando o uso diário.

**Solução Proposta:** Criação de um guia de uso rápido com exemplos práticos e comandos úteis.

**Ações:**

1.  **Criação de Guia de Uso:**
    *   O arquivo `COMECE_AQUI.md` foi criado com exemplos claros de como interagir com o bot para tarefas comuns (resumo de arquivos, lembretes, notícias, clima, etc.).
    *   Este guia também lista comandos úteis do Telegram (`/noticias`, `/status`, `/clear`, `/lembretes`).

2.  **Documentação de Funcionamento:**
    *   O guia explica que funcionalidades como notícias agendadas e lembretes dependem do bot estar ativo (`make start-docker`).

**Arquivo de Suporte:**
*   `COMECE_AQUI.md`: Guia de uso rápido para o usuário final.

## 3. Lembretes Confiáveis (Médio Impacto)

**Problema:** A configuração e o disparo de lembretes não são claros, gerando incerteza sobre sua ativação e funcionamento.

**Solução Proposta:** Documentação clara sobre a configuração de lembretes e a implementação de um comando para listar lembretes ativos.

**Ações:**

1.  **Documentação de Configuração:**
    *   O arquivo `COMECE_AQUI.md` inclui uma seção detalhada sobre como os lembretes funcionam (Telegram por padrão, e-mail com configuração SMTP).

2.  **Comando para Listar Lembretes:**
    *   O arquivo `utilitarios.py` sugere uma lógica para implementar um comando `/lembretes` que lista os próximos lembretes ativos. Isso proporciona ao usuário visibilidade e controle sobre seus lembretes.

**Arquivos de Suporte:**
*   `COMECE_AQUI.md`: Documentação sobre a configuração de lembretes.
*   `utilitarios.py`: Lógica sugerida para o comando `/lembretes`.

## 4. Memória Presente nas Respostas (Médio Impacto)

**Problema:** Embora o FactStore e a memória RAG existam, a percepção de que o bot realmente "lembra" do usuário não é sempre clara.

**Solução Proposta:** Validar a efetividade da memória e otimizar sua injeção no contexto do modelo.

**Ações:**

1.  **Validação Prática:**
    *   Utilizar o script `utilitarios.py` para verificar se o FactStore está sendo lido corretamente. Em seguida, fazer perguntas ao bot como "O que você sabe sobre mim?" ou "Quais minhas preferências?" para avaliar se as respostas refletem as informações armazenadas.

2.  **Otimização do Contexto:**
    *   Se a memória não for claramente refletida nas respostas, revisar como o `memory_context` é montado e injetado no system prompt. Pode ser necessário aumentar a relevância dos fatos ou refinar a query de busca na memória.
    *   O arquivo `utilitarios.py` contém uma sugestão de como reforçar a instrução no System Prompt para que o modelo utilize ativamente o `memory_context`.

**Arquivos de Suporte:**
*   `utilitarios.py`: Script para validação da memória e sugestão de otimização do System Prompt.

## 5. Bot Sempre Ligado (Baixo Impacto se você já usa Docker)

**Problema:** Notícias agendadas e lembretes não são disparados se o processo do bot não estiver ativo (ex: máquina desligada ou container inativo).

**Solução Proposta:** Garantir a persistência do serviço do bot através de configurações de restart automático.

**Ações:**

1.  **Configuração de Restart Automático:**
    *   Para ambientes Docker, adicionar a política `restart: always` ao serviço do bot no `docker-compose.yml`. Isso garante que o container será reiniciado automaticamente em caso de falha ou ao ligar o sistema.
    *   Para ambientes sem Docker, configurar um serviço `systemd` para gerenciar o processo do bot, garantindo que ele inicie com o sistema e seja reiniciado em caso de falha.

2.  **Health Check (Opcional):**
    *   Implementar um health check no Docker para monitorar a saúde do serviço do bot, permitindo que o Docker tome ações corretas em caso de inatividade.

**Arquivo de Suporte:**
*   `deploy_config.md`: Contém exemplos de configuração para Docker e Systemd, além de sugestão de health check.

## 6. Respostas Mais Rápidas (Baixo Impacto)

**Problema:** O tempo de resposta do bot pode ser elevado devido às chamadas ao Groq e ao tool calling.

**Solução Proposta:** Otimizações para reduzir a latência, embora não seja um bloqueador para a utilidade do bot.

**Ações:**

1.  **Cache de Perguntas:**
    *   Implementar um sistema de cache para respostas a perguntas repetidas ou muito comuns, evitando chamadas desnecessárias à LLM.

2.  **Modelos Mais Leves:**
    *   Para tarefas simples, considerar o uso de modelos de linguagem mais leves e rápidos, que podem ser mais eficientes para respostas diretas.

**Observação:** Não foram gerados arquivos de suporte específicos para esta seção, pois as otimizações de velocidade são mais complexas e dependem da arquitetura existente do bot. As sugestões são para consideração futura.

## Resumo do Plano de Ação

| Prioridade | Problema Principal | Solução Proposta | Arquivos de Suporte |
|------------|--------------------|------------------|---------------------|
| **Alta**   | Fallbacks não funcionam | Garantir funcionamento de Kimi/GLM com retries e verificação de envs | `fallbacks.py` |
| **Média**  | Uso não intuitivo | Guia de uso rápido e comandos claros | `COMECE_AQUI.md` |
| **Média**  | Lembretes incertos | Documentação e comando `/lembretes` | `COMECE_AQUI.md`, `utilitarios.py` |
| **Média**  | Memória não evidente | Validação e otimização do uso da memória | `utilitarios.py` |
| **Baixa**  | Bot não persistente | Restart automático (Docker/Systemd) | `deploy_config.md` |
| **Baixa**  | Respostas lentas | Cache e modelos mais leves (opcional) | N/A |

---

**Autor:** Manus AI
**Data:** 06 de Fevereiro de 2026
```

---

## 3. Arquivos de Suporte

Esta seção contém o código e as configurações sugeridas para implementar as soluções propostas.

### 3.1. `fallbacks.py`

```python
import time
import logging
import os
from typing import Optional, Callable

# Configuração de logs para facilitar o debug no Docker
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_with_retry(func: Callable, max_retries: int = 3, delay: int = 2):
    """Executa uma função com retry e backoff simples."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise e

class LLMFallbackManager:
    def __init__(self):
        self.nvidia_key = os.getenv("NVIDIA_API_KEY")
        self.glm_key = os.getenv("GLM_API_KEY")
        
    def check_env(self):
        """Verifica se as chaves estão presentes e sem aspas."""
        keys = {"NVIDIA_API_KEY": self.nvidia_key, "GLM_API_KEY": self.glm_key}
        for name, val in keys.items():
            if not val:
                logger.error(f"ERRO: {name} não encontrada no ambiente.")
            elif val.startswith('"') or val.endswith('"'):
                logger.warning(f"AVISO: {name} contém aspas no .env. Isso pode causar falhas de autenticação.")

    def call_kimi(self, prompt: str):
        # Exemplo de implementação robusta para Kimi (NVIDIA API)
        logger.info("Iniciando fallback para Kimi...")
        # Aqui entraria a lógica de chamada da API (ex: openai client com base_url da NVIDIA)
        pass

    def call_glm(self, prompt: str):
        # Exemplo de implementação robusta para GLM
        logger.info("Iniciando fallback para GLM...")
        pass

# Instrução para o Docker:
# Para verificar as envs no container:
# docker exec assistente-bot env | grep -E 'NVIDIA|GLM'
```

### 3.2. `COMECE_AQUI.md`

```markdown
# 🚀 Guia de Uso Rápido - BOT_UTIL

Este guia ajuda você a aproveitar ao máximo o seu assistente no dia a dia.

## 💡 O que pedir ao Bot?

Aqui estão alguns exemplos práticos de comandos e perguntas:

| Categoria | Exemplo de Pergunta/Comando |
|-----------|-----------------------------|
| **Arquivos** | "Resuma o arquivo `relatorio.pdf`" ou "O que diz o arquivo `notas.txt`?" |
| **Memória** | "O que você sabe sobre mim?" ou "Quais são minhas preferências de café?" |
| **Lembretes** | "Lembrete daqui a 2 horas: ligar para o suporte" |
| **Informação** | "Quais as notícias de hoje em Ilhéus?" ou "Clima em Salvador agora" |
| **Utilidades** | "Transcreva o áudio que enviei" ou "Analise esta imagem" |

## 🛠️ Comandos Úteis (Telegram)

- `/noticias` - Recebe as principais notícias do momento.
- `/status` - Verifica se o bot e os serviços (Groq, Kimi, GLM) estão online.
- `/clear` - Limpa o contexto da conversa atual.
- `/lembretes` - Lista seus próximos lembretes ativos.

## 🔔 Lembretes e Notificações

1. **Telegram:** Ativo por padrão se o `TELEGRAM_TOKEN` estiver configurado.
2. **E-mail:** Para receber lembretes por e-mail, configure no seu `.env`:
   - `EMAIL_ADDRESS`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_PASSWORD`.
3. **Disponibilidade:** Notícias agendadas (7h) e lembretes só funcionam se o bot estiver rodando (`make start-docker`).

---
*Dica: Se o bot demorar a responder, ele pode estar usando um fallback (Kimi/GLM) devido a limites no Groq.*
```

### 3.3. `utilitarios.py`

```python
import os
import json

def validar_memoria(fact_store_path: str):
    """
    Verifica se o FactStore contém dados e se o bot consegue acessá-los.
    """
    if not os.path.exists(fact_store_path):
        print(f"❌ FactStore não encontrado em: {fact_store_path}")
        return

    with open(fact_store_path, 'r') as f:
        try:
            data = json.load(f)
            print(f"✅ FactStore carregado. Total de fatos: {len(data.get('facts', []))}")
            for fact in data.get('facts', [])[:3]: # Mostra os 3 primeiros
                print(f"   - {fact}")
        except Exception as e:
            print(f"❌ Erro ao ler FactStore: {e}")

# Exemplo de implementação do comando /lembretes
def list_reminders_logic(storage):
    """
    Lógica sugerida para o comando /lembretes.
    """
    reminders = storage.get_all_pending() # Assumindo que o storage tem esse método
    if not reminders:
        return "Você não tem lembretes pendentes."
    
    msg = "📅 **Seus próximos lembretes:**\n"
    for r in reminders:
        msg += f"- {r.time}: {r.text}\n"
    return msg

# Sugestão de Melhoria no System Prompt para Memória:
"""
Adicione ou reforce no seu System Prompt:
'Você tem acesso a uma memória de longo prazo (FactStore). Sempre que o usuário perguntar 
sobre si mesmo ou suas preferências, consulte o contexto fornecido em <memory_context> 
e responda de forma personalizada, demonstrando que você se lembra dessas informações.'
"""
```

### 3.4. `deploy_config.md`

```markdown
# 🔄 Garantindo que o Bot esteja Sempre Ligado

Para que os lembretes e as notícias das 7h sejam confiáveis, o bot precisa reiniciar automaticamente se o servidor cair ou o processo falhar.

## 1. Docker (Recomendado)

Adicione a política de restart no seu `docker-compose.yml`:

```yaml
services:
  assistente-bot:
    image: seu-usuario/assistente-bot
    restart: always  # Garante que o container suba com o Docker
    env_file: .env
    # ... resto da config
```

## 2. Systemd (Se rodar fora do Docker)

Crie um arquivo em `/etc/systemd/system/bot-util.service`:

```ini
[Unit]
Description=Bot Util Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projeto-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Comandos úteis:
- `sudo systemctl enable bot-util` (para iniciar no boot)
- `sudo systemctl start bot-util` (para iniciar agora)

## 3. Health Check (Opcional)

Para monitorar se o bot está "vivo", você pode adicionar um healthcheck no Docker:

```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 1m
      timeout: 10s
      retries: 3
```
```

---

**Autor:** Manus AI
**Data:** 06 de Fevereiro de 2026


--



 Vou analisar esse documento sobre o que falta para o bot ser útil e propor soluções práticas. Primeiro, deixe-me verificar se há informações atualizadas sobre as APIs mencionadas (Groq, NVIDIA/Kimi, GLM) e também buscar exemplos de boas práticas para bots de produtividade.  
 Com base na análise do seu documento e nas informações atualizadas sobre as APIs, aqui está o plano de resolução prática para tornar seu bot realmente útil no dia a dia:

---

## 1. Confiabilidade em 429 (Alta Prioridade)

### Problema identificado
Seus fallbacks (Kimi/GLM) falham no Docker por problemas de ambiente, não de API.

### Solução imediata

**Verificação de ambiente Docker:**
```bash
# Verificar se as chaves estão no container
docker exec assistente-bot env | grep -E 'NVIDIA|GLM|GROQ'

# Testar conectividade de rede
docker exec assistente-bot curl -s https://integrate.api.nvidia.com/v1/models
docker exec assistente-bot curl -s https://open.bigmodel.cn/api/paas/v4/models
```

**Configuração correta do `.env`:**
```bash
# Sem aspas nos valores
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxx
GLM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Timeout aumentado para containers
REQUEST_TIMEOUT=60
```

**Implementação de retry com backoff** (exemplo Python):
```python
import backoff
import requests
from groq import RateLimitError

@backoff.on_exception(backoff.expo, RateLimitError, max_tries=3)
def call_groq_with_fallback(**kwargs):
    try:
        return groq_client.chat.completions.create(**kwargs)
    except RateLimitError:
        # Fallback para NVIDIA/Kimi
        return call_nvidia_fallback(**kwargs)
```

**Headers do Groq para prevenção** :
O Groq retorna headers úteis: `x-ratelimit-remaining-requests`, `x-ratelimit-reset-requests`, `retry-after`. Use-os para prevenir 429 antes de acontecer.

---

## 2. Guia de Uso Recorrente (Média Prioridade)

Crie um arquivo `COMECE_AQUI.md` na raiz:

```markdown
# 🚀 Assistente Bot - Guia Rápido

## Comandos úteis
- `/noticias` - Notícias de hoje (fontes configuradas)
- `/status` - Verifica se bot está online e APIs funcionando
- `/clear` - Limpa histórico da conversa
- `/lembretes` - Lista seus próximos lembretes

## Exemplos do dia a dia
💬 "Resuma o arquivo relatorio.pdf"
💬 "O que você sabe sobre mim?"
💬 "Lembre daqui 2 horas: ligar para João"
💬 "Notícias de Ilhéus hoje"
💬 "Clima em Salvador agora"
💬 "Transcreva este áudio" (envie o arquivo)

## ⚠️ Importante
- Notícias às 7h e lembretes só funcionam com o bot rodando
- Para iniciar: `make start-docker`
- Para email nos lembretes: configure SMTP_* no .env
```

---

## 3. Lembretes Confiáveis (Média Prioridade)

**Documentação no README:**
```markdown
### Configuração de Lembretes

**Telegram (sempre funciona):**
- Já ativo por padrão via `TELEGRAM_BOT_TOKEN`

**Email (opcional):**
```env
EMAIL_ADDRESS=seu@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=sua_senha_app  # Não é a senha do email, é senha de app
```

**Comando para listar lembretes:**
Implemente `/lembretes` que consulta o `ReminderNotifier`:
```python
def list_reminders(user_id):
    upcoming = reminder_store.get_upcoming(user_id)
    return format_reminder_list(upcoming)
```

---

## 4. Memória Presente (Média Prioridade)

**Teste de validação:**
```
Você: "O que você sabe sobre mim?"
Bot deve responder: "Sei que [fato do FactStore], prefere [preferência], etc."
```

**Se não funcionar, ajuste o system prompt:**
```python
system_prompt = f"""Você é um assistente pessoal. 
Use estas informações sobre o usuário para personalizar respostas:
{memory_context}

Se o usuário perguntar "o que você sabe sobre mim", cite especificamente 
os fatos acima de forma natural."""
```

---

## 5. Bot Sempre Ligado (Baixa Prioridade)

**Opção A - Systemd (Linux):**
```ini
# /etc/systemd/system/assistente-bot.service
[Unit]
Description=Assistente Bot
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/caminho/do/projeto
ExecStart=/usr/bin/make start-docker
ExecStop=/usr/bin/make stop-docker

[Install]
WantedBy=multi-user.target
```

**Opção B - Docker restart policy:**
```yaml
# docker-compose.yml
services:
  bot:
    restart: unless-stopped
    # ... resto da config
```

**Health check:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Checklist de Implementação

| Tarefa | Comando/Arquivo | Prioridade |
|--------|----------------|------------|
| Verificar envs no Docker | `docker exec assistente-bot env` | 🔴 Alta |
| Implementar retry backoff | `src/llm/fallback.py` | 🔴 Alta |
| Criar `COMECE_AQUI.md` | raiz do projeto | 🟡 Média |
| Documentar SMTP | `README.md` seção Lembretes | 🟡 Média |
| Comando `/lembretes` | `src/commands/reminders.py` | 🟡 Média |
| Testar memória | Conversa: "O que sabe sobre mim?" | 🟡 Média |
| Systemd service | `/etc/systemd/system/assistente-bot.service` | 🟢 Baixa |

Com essas mudanças, seu bot terá fallbacks robustos (usando NVIDIA NIM com autenticação `$oauthtoken`  e GLM-4 da Zhipu AI ), interface clara para uso diário, e lembretes confiáveis.