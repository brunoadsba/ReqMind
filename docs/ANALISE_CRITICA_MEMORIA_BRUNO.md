# Análise Crítica: Sistema de Memória e Informações sobre Bruno

**Data:** 2026-02-06  
**Autor:** Análise Automatizada  
**Escopo:** Sistema de memória do bot e armazenamento de informações sobre o usuário

---

## 1. Resumo Executivo

O sistema de memória do bot apresenta **arquitetura fragmentada** com dois sistemas paralelos que não se comunicam adequadamente. As informações sobre Bruno estão **dispersas** entre código-fonte, configuração e documentação, mas **não estão estruturadas na memória persistente** do agente.

**Estado atual:**
- ✅ Sistema de memória implementado tecnicamente
- ❌ Poucos fatos armazenados (apenas 3 no `facts.jsonl`)
- ❌ Arquivos markdown de memória completamente vazios
- ❌ Informações sobre Bruno não estão na memória estruturada
- ⚠️ Dois sistemas de memória diferentes sem integração

---

## 2. Arquitetura de Memória: Problemas Identificados

### 2.1. Duplicação de Sistemas

**Sistema 1: FactStore (`workspace/memory/fact_store.py`)**
- Armazena em: `workspace/memory/facts.jsonl`
- Formato: JSONL (uma linha por fato)
- Busca: TF-IDF + similaridade de cosseno
- Status: ✅ Funcional, mas subutilizado

**Sistema 2: RAG Memory (`workspace/tools/impl/rag_memory.py`)**
- Armazena em: `dados/memory.json` (não existe ainda)
- Formato: JSON estruturado (`knowledge`, `conversations`, `documents`)
- Busca: Busca textual simples (substring)
- Status: ⚠️ Implementado mas nunca usado

**Problema:** Dois sistemas paralelos sem coordenação. O Agent usa apenas o FactStore via `MemoryManager`, mas há ferramentas RAG que tentam usar o sistema alternativo.

### 2.2. Arquivos de Memória Vazios

**Arquivos Markdown (Camada 2) - TODOS VAZIOS:**
- `workspace/memory/facts.md` - Vazio
- `workspace/memory/decisions.md` - Vazio  
- `workspace/memory/patterns.md` - Vazio
- `workspace/memory/feedback.md` - Vazio

**Implicação:** A arquitetura de 3 camadas foi implementada, mas a Camada 2 (memória estruturada) não está sendo populada.

### 2.3. Extração Automática Limitada

O `MemoryManager.remember_interaction()` só extrai fatos quando detecta padrões específicos:

```python
fact_patterns = [
    r"(?:projeto|diretório|caminho) [ée]stá? em ([/\w~.-]+)",  # path
    r"(?:versão|versao) [ée] ([\d.]+)",                        # version
    r"(?:usuário|login) [ée] (\w+)",                           # user
    r"(?:token|senha|chave) [ée] (\S+)",                       # secret
    r"(?:porta|port) [ée] (\d+)",                              # port
    r"ip [ée] (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",          # ip
]
```

**Problema:** Informações pessoais sobre Bruno (preferências, contexto, histórico) não são capturadas automaticamente porque não seguem esses padrões técnicos.

---

## 3. Informações sobre Bruno: Onde Estão?

### 3.1. Informações Encontradas (Espalhadas)

| Localização | Tipo | Informação |
|------------|------|------------|
| `MEMORY.md` | Documentação | Nome: Bruno, User ID: 6974901522, Bot: @br_bruno_bot |
| `.env` | Configuração | Email: brunotstba@gmail.com |
| `workspace/agent/IDENTITY.md` | Contexto do agente | "Assistente Pessoal de Bruno", User ID: 6974901522 |
| `fact_store.py` (vocabulário) | Código hardcoded | Palavra "bruno" no vocabulário inicial |
| `workspace/memory/facts.jsonl` | Memória persistente | ❌ Nenhuma informação sobre Bruno |

### 3.2. Informações NÃO Encontradas na Memória

**Informações que DEVERIAM estar na memória estruturada:**
- ❌ Nome completo do usuário
- ❌ Preferências de comunicação (tom, verbosidade)
- ❌ Contexto de trabalho/projetos atuais
- ❌ Histórico de interações relevantes
- ❌ Padrões de uso identificados
- ❌ Feedback sobre respostas do bot

**Consequência:** O bot não "lembra" quem é Bruno além do que está hardcoded no código.

---

## 4. Análise do `facts.jsonl` Atual

**Conteúdo atual (apenas 3 fatos):**

```json
1. {"content": "O projeto principal esta em /home/brunoadsba/clawd", "tags": ["path", "projeto"]}
2. {"content": "O projeto principal está em /home/brunoadsba/clawd", "tags": ["projeto"]}
3. {"content": "Senha do banco: s3cr3t123", "tags": ["seguranca"]}
```

**Problemas identificados:**
1. **Duplicação:** Fatos 1 e 2 são idênticos (apenas diferença de acentuação)
2. **Informação sensível:** Fato 3 contém senha em texto plano (risco de segurança)
3. **Baixa qualidade:** Apenas 3 fatos em todo o histórico
4. **Sem contexto pessoal:** Nenhum fato sobre Bruno como pessoa

---

## 5. Fluxo de Memória: Como Funciona (e Não Funciona)

### 5.1. Fluxo Atual

```
User Message → Agent.run() → LLM Response → _finalize_run() 
    → memory_manager.remember_interaction()
        → extract_facts_from_message() [só padrões técnicos]
            → FactStore.add_fact() → facts.jsonl
```

**Limitação:** Só captura informações técnicas (paths, versões, senhas), não informações pessoais ou contexto.

### 5.2. O Que Deveria Acontecer

```
User Message → Agent.run() → LLM Response → _finalize_run()
    → memory_manager.remember_interaction()
        → extract_facts_from_message() [padrões técnicos + LLM extraction]
        → extract_personal_context() [novo: informações sobre Bruno]
        → FactStore.add_fact() → facts.jsonl
        → MemoryManager.add_decision() → decisions.md [novo]
        → MemoryManager.add_pattern() → patterns.md [novo: se padrão detectado]
```

---

## 6. Problemas Críticos

### 6.1. Segurança: Senha em Texto Plano

**Localização:** `facts.jsonl`, linha 3  
**Conteúdo:** `"Senha do banco: s3cr3t123"`

**Risco:** 
- Arquivo `facts.jsonl` não está em `.gitignore` (verificar)
- Senha armazenada sem criptografia
- Acessível a qualquer processo que leia o arquivo

**Ação necessária:** 
1. Remover senha do arquivo
2. Implementar sanitização de dados sensíveis antes de salvar
3. Adicionar `facts.jsonl` ao `.gitignore` se não estiver

### 6.2. Memória Não Persiste Contexto Pessoal

O bot não "aprende" sobre Bruno porque:
- Extração automática só captura padrões técnicos
- Não há mecanismo para o LLM sugerir fatos pessoais
- Arquivos markdown de memória nunca são populados

**Exemplo do que falta:**
- "Bruno prefere respostas diretas"
- "Bruno trabalha principalmente com Python e Next.js"
- "Bruno usa o bot principalmente para análise de código"

### 6.3. Duplicação de Fatos

O `FactStore` verifica duplicação por conteúdo exato:
```python
if fact.content == content:
    return fact.id  # Ja existe
```

**Problema:** Fatos 1 e 2 são considerados diferentes porque têm acentuação diferente ("esta" vs "está"), mas são semanticamente idênticos.

**Solução:** Normalizar texto antes de verificar duplicação (remover acentos, lowercase).

---

## 7. Recomendações Prioritárias

### Prioridade ALTA (Segurança e Funcionalidade)

1. **Remover senha do `facts.jsonl`**
   - Localizar e remover linha com senha
   - Implementar sanitização de dados sensíveis

2. **Implementar extração de contexto pessoal**
   - Adicionar padrões para informações sobre Bruno
   - Usar LLM para sugerir fatos relevantes das conversas
   - Popular arquivos markdown de memória

3. **Consolidar sistemas de memória**
   - Decidir: FactStore OU RAG Memory (não ambos)
   - Migrar funcionalidades necessárias para sistema escolhido
   - Remover código não utilizado

### Prioridade MÉDIA (Qualidade)

4. **Melhorar detecção de duplicação**
   - Normalizar texto (lowercase, remover acentos)
   - Usar similaridade semântica além de igualdade exata

5. **Popular memória inicial sobre Bruno**
   - Criar script para adicionar fatos básicos:
     - Nome: Bruno
     - User ID: 6974901522
     - Email: brunotstba@gmail.com
     - Bot: @br_bruno_bot
     - Preferências de comunicação (do IDENTITY.md)

6. **Implementar população automática de markdown**
   - `decisions.md`: Decisões importantes do Agent
   - `patterns.md`: Padrões de uso detectados
   - `feedback.md`: Feedback implícito (quando usuário reformula pergunta)

### Prioridade BAIXA (Otimização)

7. **Adicionar métricas de memória**
   - Dashboard de fatos armazenados
   - Taxa de uso da memória nas respostas
   - Qualidade dos fatos (score de relevância)

8. **Implementar limpeza automática**
   - Remover fatos obsoletos (ex.: paths antigos)
   - Consolidar fatos similares

---

## 8. Conclusão

O sistema de memória está **tecnicamente implementado**, mas **subutilizado e fragmentado**. As informações sobre Bruno estão **dispersas** e não estruturadas na memória persistente do agente.

**Principais gaps:**
1. ❌ Memória não captura contexto pessoal
2. ❌ Dois sistemas paralelos sem coordenação
3. ❌ Arquivos markdown nunca populados
4. ⚠️ Risco de segurança (senha em texto plano)
5. ⚠️ Baixa qualidade dos fatos armazenados

**Próximos passos recomendados:**
1. Corrigir problema de segurança imediatamente
2. Implementar extração de contexto pessoal
3. Popular memória inicial sobre Bruno
4. Consolidar sistemas de memória

---

**Arquivos analisados:**
- `src/workspace/memory/fact_store.py`
- `src/workspace/memory/memory_manager.py`
- `src/workspace/memory/facts.jsonl`
- `src/workspace/tools/impl/rag_memory.py`
- `src/workspace/core/agent.py`
- `src/config/settings.py`
- `MEMORY.md`
- `src/workspace/agent/IDENTITY.md`
