# Propostas de Correção - Assistente Bot

Este documento detalha as alterações sugeridas para resolver os problemas de fallback e leitura de arquivos em caso de erro 429 (Rate Limit) na API Groq.

---

## 1. Melhoria nos Clientes de Fallback (`nvidia_kimi.py` e `glm_client.py`)

O objetivo é tornar as chamadas mais resilientes e fáceis de diagnosticar.

### `src/workspace/core/nvidia_kimi.py` (Sugestão)
```python
import requests
import logging

logger = logging.getLogger(__name__)

def chat_completion_sync(api_key, messages, model="nvidia/llama-3.1-70b-instruct", timeout=25):
    """
    Chamada para NVIDIA NIM (Kimi/Llama).
    """
    if not api_key:
        logger.warning("fallback_kimi_pulado: NVIDIA_API_KEY ausente")
        return None

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}", # Remove espaços/aspas acidentais
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        
        # Log para diagnóstico em caso de erro
        if response.status_code != 200:
            logger.error(f"Fallback Kimi falhou (Status {response.status_code}): {response.text}")
            return None
            
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        
        if not content:
            logger.error(f"Fallback Kimi retornou resposta vazia: {data}")
            return None
            
        return content

    except requests.exceptions.Timeout:
        logger.error("Fallback Kimi falhou: Timeout")
    except Exception as e:
        logger.error(f"Fallback Kimi falhou: {str(e)}")
    
    return None
```

---

## 2. Implementação de Leitura de Arquivo em 429 (`agent.py`)

Alteração no loop do agente para extrair o nome do arquivo e tentar lê-lo diretamente quando a LLM principal falha.

### `src/workspace/core/agent.py` (Sugestão de lógica)

```python
import re
from workspace.tools.filesystem import read_file

def _extract_filename(message):
    """
    Tenta extrair um nome de arquivo .md ou .txt da mensagem.
    """
    match = re.search(r'([\w\d\-_]+\.(?:md|txt))', message, re.IGNORECASE)
    return match.group(1) if match else None

# Dentro do bloco 'except Exception as e' onde trata _is_rate_limit_error:

if _is_rate_limit_error(error_msg):
    # ... (lógica de cooldown e fallbacks Kimi/GLM) ...
    
    # Se fallbacks falharam e é uma pergunta de arquivo
    if _user_asked_to_read_file(user_message):
        filename = _extract_filename(user_message)
        if filename:
            try:
                logger.info(f"Tentando leitura direta de arquivo em 429: {filename}")
                content = read_file(filename)
                if content:
                    # Retorna o conteúdo diretamente com um aviso
                    return (
                        "⚠️ **Limite de API atingido.** Não consegui resumir, "
                        f"mas aqui está o conteúdo de `{filename}`:\n\n"
                        f"{content[:2000]}..." # Truncar se for muito grande para o Telegram
                    )
            except Exception as read_err:
                logger.error(f"Falha na leitura direta em 429: {read_err}")

    # Se nada funcionou, retorna a rate_msg padrão
    return rate_msg
```

---

## 3. Verificação de Ambiente (Docker/`.env`)

Para garantir que as chaves cheguem corretamente ao processo:

1. **Remover aspas:** No arquivo `.env`, certifique-se de que as chaves não tenham aspas.
   - Errado: `NVIDIA_API_KEY="nvapi-..."`
   - Correto: `NVIDIA_API_KEY=nvapi-...`
2. **Logs de Inicialização:** Adicione um log no início do bot para validar a presença (não o valor) das chaves:
   ```python
   import os
   logger.info(f"Config: NVIDIA_KEY={'SET' if os.getenv('NVIDIA_API_KEY') else 'MISSING'}")
   logger.info(f"Config: GLM_KEY={'SET' if os.getenv('GLM_API_KEY') else 'MISSING'}")
   ```

---

## 4. Diagnóstico de GLM (`glm_client.py`)

Se o GLM estiver falhando, verifique se a URL base e o modelo estão corretos para o seu provedor (Zhipu ou outro). O modelo `glm-4.7-flash` pode exigir uma URL específica ou cabeçalhos diferentes dependendo da API.

```python
# Exemplo de ajuste de URL para Zhipu AI
url = os.getenv("GLM_API_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
```



--




## Solução Técnica para o Problema de Fallback + Leitura de Arquivos em 429

Baseado na análise do documento, o problema tem **duas causas interligadas** que precisam ser resolvidas:

---

### 🔧 Correção Imediata Recomendada (Prioridade Alta)

#### 1. Corrigir o fluxo de fallback para perguntas de arquivo em `agent.py`

No método `run()` de `src/workspace/core/agent.py`, substitua o bloco que trata 429 + `_user_asked_to_read_file`:

```python
# ANTES (comportamento atual - problema):
if _user_asked_to_read_file(user_message):
    return rate_msg + " Quando retomar, tente: «O que você sabe sobre mim?» ou «Quais minhas preferências?». Perguntas que exigem leitura de arquivos não podem ser atendidas enquanto a API estiver indisponível."

# DEPOIS (solução proposta):
if _user_asked_to_read_file(user_message):
    # Extrair caminho do arquivo da mensagem (ex: MEMORY.md, notes.txt)
    file_path = _extract_file_path(user_message)  # Nova função helper
    
    if file_path:
        try:
            # Ler arquivo DIRETAMENTE mesmo em 429
            from workspace.tools.filesystem import read_file
            content = read_file(file_path)
            
            # Retornar conteúdo truncado (máx. 2000 chars) + aviso
            truncated = content[:2000] + "..." if len(content) > 2000 else content
            return (
                "⚠️ API principal temporariamente indisponível (limite atingido).\n\n"
                f"Conteúdo do arquivo `{file_path}` (sem processamento):\n\n"
                f"```\n{truncated}\n```\n\n"
                "Para um resumo completo, tente novamente em 1 minuto."
            )
        except Exception as e:
            logger.warning(f"read_file fallback 429 falhou para {file_path}: {e}")
    
    # Fallback mínimo se não conseguir ler arquivo
    return (
        "⚠️ API temporariamente indisponível (limite atingido).\n\n"
        "⚠️ Não foi possível acessar o arquivo solicitado no momento.\n\n"
        "💡 Tente novamente em 1 minuto ou pergunte sobre suas preferências salvas."
    )
```

#### 2. Implementar helper `_extract_file_path()` em `agent.py`

```python
def _extract_file_path(message: str) -> Optional[str]:
    """Extrai caminho de arquivo de mensagens como 'leia MEMORY.md'."""
    import re
    # Padrões comuns: MEMORY.md, arquivo.txt, docs/notes.md
    patterns = [
        r'[\s"\'`]([a-zA-Z0-9_\-/]+\.md)[\s"\'`]',
        r'[\s"\'`]([a-zA-Z0-9_\-/]+\.txt)[\s"\'`]',
        r'arquivo\s+([a-zA-Z0-9_\-/.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            path = match.group(1).strip()
            # Validar contra allowlist/base_dir (evitar path traversal)
            if ".." not in path and not path.startswith("/"):
                return path
    return None
```

---

### 🔧 Correção Secundária (Garantir Fallbacks Funcionais)

#### 3. Validar configuração do `.env`

```ini
# .env - EXEMPLO CORRETO (sem aspas/whitespace)
GROQ_API_KEY=...
NVIDIA_API_KEY=...          # Obrigatório para Kimi fallback
GLM_API_KEY=...             # Opcional mas recomendado como 2º fallback
GLM_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4  # Default Zhipu
GLM_MODEL=glm-4-flash       # Mais rápido/mais barato que glm-4.7-flash
```

> ⚠️ **Checklist Docker**:  
> - Executar `docker exec assistente-bot env | grep -E "(NVIDIA|GLM)_API_KEY"` para confirmar que as chaves estão no container  
> - Remover aspas no `.env`: `NVIDIA_API_KEY="abc"` → `NVIDIA_API_KEY=abc`

#### 4. Melhorar robustez dos clientes de fallback

Em `nvidia_kimi.py` e `glm_client.py`, adicionar:

```python
# Timeout mais generoso + retry simples
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _get_session():
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

# Usar session com timeout 30s
response = session.post(url, json=payload, headers=headers, timeout=30)
```

---

### ✅ Plano de Validação

1. **Teste de leitura direta em 429**:
   ```bash
   # Forçar 429 (simular)
   curl -X POST http://localhost:8000/debug/force-429

   # Telegram: "Leia o conteúdo do arquivo MEMORY.md"
   # ✅ Esperado: Conteúdo do arquivo retornado mesmo com 429
   ```

2. **Teste de fallback funcional**:
   ```bash
   # Remover GROQ_API_KEY temporariamente no container
   docker exec assistente-bot sh -c "unset GROQ_API_KEY && python -c 'from workspace.core.agent import Agent; print(Agent().run(\"oi\"))'"

   # ✅ Esperado: Resposta vinda de Kimi/GLM com log "llm_resposta_fallback provider=nvidia"
   ```

3. **Logs esperados após correção**:
   ```
   llm_rate_limit provider=groq
   fallback_429_arquivo path=MEMORY.md
   read_file_fallback_429 success bytes=1240
   ```

---

### 📌 Resumo da Solução

| Problema | Solução |
|----------|---------|
| Fallbacks não funcionam | Validar `.env` + adicionar retry/timeouts nos clientes |
| Leitura de arquivo bloqueada em 429 | Chamar `read_file()` diretamente mesmo em 429 (sem depender de LLM) |
| UX ruim com 429 | Retornar conteúdo bruto do arquivo + aviso claro (não apenas "tente depois") |

Esta abordagem resolve **80% do problema imediatamente** (leitura direta de arquivo em 429) e **20% restante** com ajustes de configuração para fallbacks funcionais. Implementação estimada: **1-2 horas** por um desenvolvedor familiarizado com o código base.





--




Segue **solução objetiva e implementável**, atacando o problema **sem depender de Groq** quando há **429** e a pergunta exige **leitura de arquivo**.

---

## SOLUÇÃO RECOMENDADA (definitiva)

### 🎯 Objetivo

Garantir que **perguntas de leitura/resumo de arquivo funcionem mesmo em 429**, **independentemente** de Kimi/GLM.

---

## A. Corrigir o gargalo estrutural (prioridade máxima)

Hoje, em 429 + `_user_asked_to_read_file == True`, o agente **não chama nenhuma tool** e **retorna erro por design**.

👉 **Isso é o bug.**

### ✅ Correção: permitir `read_file` em 429 quando a pergunta for de arquivo

---

## B. Implementação direta (patch cirúrgico)

### 1️⃣ No `agent.run()` – bloco de rate limit (429)

**ANTES (resumo do comportamento atual):**

```python
if _is_rate_limit_error(error_msg):
    if _user_asked_to_read_file(user_message):
        return rate_msg
```

---

### ✅ DEPOIS (com fallback real para leitura de arquivo)

```python
if _is_rate_limit_error(error_msg):
    logger.warning("429 detectado (Groq). Avaliando fallback...")

    if _user_asked_to_read_file(user_message):
        try:
            from src.workspace.tools.filesystem import read_file
            path = _extract_file_path(user_message)  # ex: MEMORY.md

            content = read_file(path)

            return (
                "⚠️ API principal indisponível no momento.\n\n"
                "📄 **Conteúdo do arquivo solicitado:**\n\n"
                f"{_truncate(content, max_chars=6000)}"
            )
        except Exception as fe:
            logger.error(f"Falha ao ler arquivo em 429: {fe}")
            return rate_msg
```

---

### 2️⃣ Função utilitária para extrair path (simples e segura)

```python
import re

def _extract_file_path(msg: str) -> str:
    match = re.search(r"([\w\-\/]+\.(md|txt|json))", msg.lower())
    if not match:
        raise ValueError("Arquivo não identificado na mensagem.")
    return match.group(1)
```

---

### 3️⃣ Truncamento defensivo (evita estouro no Telegram)

```python
def _truncate(text: str, max_chars=6000):
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n[...]"
```

---

## C. Resultado prático

| Cenário                           | Resultado                      |
| --------------------------------- | ------------------------------ |
| Groq OK                           | LLM responde normalmente       |
| Groq 429 + pergunta normal        | Kimi → GLM → RAG → FactStore   |
| **Groq 429 + leitura de arquivo** | ✅ **Arquivo lido via tool**    |
| Kimi/GLM fora                     | **Sistema continua funcional** |

👉 **O bot nunca mais “morre” por causa de 429**.

---

## D. (Opcional, mas recomendado) – Melhorar Kimi/GLM

Se quiser robustez extra:

### ✔️ Logs explícitos

```python
logger.info("tentando_fallback_kimi")
logger.info("tentando_fallback_glm")
```

### ✔️ Timeout + retry

* 2 tentativas
* backoff exponencial (1s → 3s)

Mas **isso é complementar**, não essencial.

---

## E. Validação final (checklist)

* [ ] Forçar 429 no Groq
* [ ] Enviar: `Leia o conteúdo do arquivo MEMORY.md e resuma...`
* [ ] ✅ Bot responde com conteúdo do arquivo
* [ ] Logs mostram: `read_file em modo 429`

---

## Conclusão técnica

> **Erro não é de API externa.
> É de fluxo de controle.**

A leitura de arquivos **não depende de LLM** e **não deve ser bloqueada por 429**.

Essa correção elimina o problema **pela raiz**, com baixo risco e alta previsibilidade.

Se quiser, posso:

* adaptar o patch exatamente ao seu `agent.py`
* ou gerar um **diff pronto para commit**.
