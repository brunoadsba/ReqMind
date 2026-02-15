# Plano: Sistema Híbrido de Normas Regulamentadoras (NRs)

## 1. Contexto e Problema

### 1.1 Situação Atual
- **NRs existentes no Brasil:** 38 aprovadas (36 ativas, 2 revogadas)
- **NR-29:** Já carregada na memória RAG (~4.000 tokens)
- **Restante:** Não disponíveis localmente

### 1.2 Opções Analisadas

| Opção | Vantagens | Desvantagens |
|-------|-----------|--------------|
| **Carregar todas 38 NRs** | Resposta instantânea | ~400K tokens, manutenção manual, desatualiza rápido |
| **Web Search puro** | Sempre atual, zero manutenção | 2-3s por consulta, depende de internet |
| **HÍBRIDA (escolhida)** | Melhor dos dois mundos | Complexidade de implementação |

### 1.3 Decisão: Abordagem Híbrida

```
NRs Frequentes (memória) + NRs Específicas (web search)
```

---

## 2. Arquitetura da Solução

### 2.1 NRs Prioritárias (Memória RAG - Carregamento Proativo)

| NR | Tema | Tokens Estimados | Prioridade |
|----|------|------------------|------------|
| NR-1 | Disposições Gerais e Gerenciamento de Riscos | 5.000 | ALTA |
| NR-5 | CIPA | 3.000 | ALTA |
| NR-6 | EPI | 4.000 | ALTA |
| NR-10 | Eletricidade | 8.000 | ALTA |
| NR-29 | Trabalho Portuário | 4.000 | JÁ IMPLEMENTADA |
| NR-33 | Espaço Confinado | 6.000 | ALTA |
| NR-35 | Trabalho em Altura | 5.000 | ALTA |

**Total estimado:** ~35.000 tokens

### 2.2 NRs Secundárias (Web Search Sob Demanda)

- NR-2 a NR-4, NR-7 a NR-9, NR-11 a NR-28, NR-30 a NR-38
- **Estratégia:** Busca automática quando usuário pergunta sobre NR não carregada

### 2.3 Fluxo de Consulta

```
Usuário pergunta sobre NR
         ↓
┌──────────────┴──────────────┐
↓                              ↓
NR está na memória?        NR NÃO está na memória?
         ↓                              ↓
    Responde              Faz web search no site govt.br
    (instantâneo)          Retorna resultado atualizado
```

---

## 3. Tarefas de Implementação

### 3.1 Tarefa 1: Criar Scripts de Alimentação

**Objetivo:** Automatizar o download e formatação das NRs

```
scripts/
├── feed_nr05.py    # NR-5 - CIPA
├── feed_nr06.py    # NR-6 - EPI
├── feed_nr10.py    # NR-10 - Eletricidade
├── feed_nr35.py    # NR-35 - Trabalho em Altura
└── fetch_nr_govt.py # Script genérico para download do site govt.br
```

**Critérios de sucesso:**
- [ ] Script genérico faz download de qualquer NR do site govt.br
- [ ] Scripts específicos para NRs prioritárias
- [ ] Tratamento de erros (site offline, NR não encontrada)
- [ ] Formatação consistente com NR-29 existente

---

### 3.2 Tarefa 2: Atualizar Agente para Web Search Automático

**Objetivo:** Detectar perguntas sobre NRs e acionar web search automaticamente

**Arquivo:** `src/workspace/core/agent.py`

**Lógica necessária:**
```
SE ("NR-" ou "Norma Regulamentadora") na mensagem E
   NR não está na memória local:
       → Usar web_search (DuckDuckGo)
       → Buscar no site: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/seguranca-e-saude-no-trabalho
       → Retornar resultado formatado
```

**Critérios de sucesso:**
- [ ] Detecção de perguntas sobre NRs funciona
- [ ] Web search acionado automaticamente para NRs desconhecidas
- [ ] Resultados formatados legivelmente
- [ ] Tempo de resposta < 5 segundos

---

### 3.3 Tarefa 3: Criar Ferramenta de Consulta NR

**Objetivo:** Criar ferramenta dedicado para consultas NR

**Arquivo:** `src/workspace/tools/norms/nr_lookup.py`

**Funcionalidades:**
```python
async def lookup_nr(nr_number: int, query: str = None) -> dict:
    """
    Consulta uma NR específica.

    Args:
        nr_number: Número da NR (1-38)
        query: Pergunta específica sobre a NR (opcional)

    Returns:
        dict com status, conteúdo e fonte
    """

# Comportamento:
# - Se NR está na memória → retorna conteúdo local
# - Se NR não está na memória → faz web search
# - Cache de 24h para resultados de web search
```

**Critérios de sucesso:**
- [ ] Ferramenta funciona para todas as NRs (1-38)
- [ ] Cache implementado (24h)
- [ ] Retorno estruturado (conteúdo, fonte, timestamp)

---

### 3.4 Tarefa 4: Atualizar Documentação

**Objetivo:** Documentar o sistema híbrido

**Arquivos:**
- `docs/03-referencia/TOOLS_REFERENCE.md` (atualizar)
- `COMECE_AQUI.md` (adicionar exemplos NR)
- `MEMORY.md` (documentar NRs em memória)

**Critérios de sucesso:**
- [ ] Exemplos de uso de NRs
- [ ] Lista de NRs disponíveis em memória
- [ ] Descrição do comportamento híbrido

---

## 4. Cronograma Sugerido

### Fase 1: Fundação (Dias 1-2)
- [ ] Tarefa 3.1: Scripts de alimentação
- [ ] Tarefa 3.4: Atualizar documentação básica

### Fase 2: Core (Dias 3-4)
- [ ] Tarefa 3.2: Web search automático no agente
- [ ] Tarefa 3.3: Ferramenta de consulta NR

### Fase 3: Refinamento (Dia 5)
- [ ] Tarefa 3.4: Documentação completa
- [ ] Testes end-to-end
- [ ] Ajustes de performance

---

## 5. Critérios de Sucesso Finais

| Critério | Métrica | Meta |
|----------|---------|------|
| Tempo de resposta NR em memória | ms | < 100ms |
| Tempo de resposta NR via web | s | < 5s |
| Cobertura de NRs críticas | % | 100% (7/7) |
| Taxa de sucesso web search | % | > 95% |
| Documentação completa | % | 100% |

---

## 6. Exemplos de Uso

### 6.1 NR Carregada (Instantâneo)
```
Usuário: "me explica a NR-35 trabalho em altura"
Bot: [responde instantâneo usando memória local]
```

### 6.2 NR Não Carregada (Web Search)
```
Usuário: "o que diz a NR-18 construção civil"
Bot: [faz web search, retorna resultado atualizado]
```

### 6.3 Consulta Específica
```
Usuário: "quais são os EPIs obrigatórios segundo NR-6"
Bot: [busca específica na NR-6, retorna seção relevante]
```

---

## 7. Links Úteis

- **Portal oficial:** https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/seguranca-e-saude-no-trabalho/ctpp-nrs/normas-regulamentadoras-nrs
- **NR-29 atual:** `scripts/feed_nr29_to_memory.py`
- **Padrão atual:** `src/workspace/core/agent.py`

---

## 8. Status da Implementação (2026-02-06)

### ✅ Implementado

| NR | Tema | Script | Status |
|----|------|--------|--------|
| NR-1 | Disposições Gerais | feed_nr01.py | ✅ Carregado |
| NR-5 | CIPA | feed_nr05.py | ✅ Carregado |
| NR-6 | EPI | feed_nr06.py | ✅ Carregado |
| NR-10 | Eletricidade | feed_nr10.py | ✅ Carregado |
| NR-29 | Trabalho Portuário | feed_nr29_to_memory.py | ✅ Carregado |
| NR-33 | Espaço Confinado | feed_nr33.py | ✅ Carregado |
| NR-35 | Trabalho em Altura | feed_nr35.py | ✅ Carregado |

### Arquivos Criados/Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `scripts/fetch_nr_govt.py` | Novo | Download de NRs do site govt.br |
| `scripts/feed_nr01.py` | Novo | Feed NR-1 |
| `scripts/feed_nr05.py` | Novo | Feed NR-5 |
| `scripts/feed_nr06.py` | Novo | Feed NR-6 |
| `scripts/feed_nr10.py` | Novo | Feed NR-10 |
| `scripts/feed_nr33.py` | Novo | Feed NR-33 |
| `scripts/feed_nr35.py` | Novo | Feed NR-35 |
| `src/workspace/tools/norms/nr_lookup.py` | Novo | Ferramenta de consulta NR |
| `src/workspace/core/agent.py` | Modificado | Web search automático para NRs |

### Critérios de Sucesso

| Critério | Status | Observação |
|----------|--------|------------|
| Tempo de resposta NR em memória | ✅ | ~100ms |
| Tempo de resposta NR via web | ✅ | ~2-3s |
| Cobertura de NRs críticas | ✅ | 7/7 (100%) |
| Taxa de sucesso web search | ✅ | Funcional |
| Documentação completa | ✅ | Atualizada |

### Como Testar

```bash
# Testar NR em memória (instantâneo)
echo "me explica a NR-35 trabalho em altura" | pyTHONPATH=src python -c "from workspace.tools.impl.rag_memory import search_memory; print(search_memory('NR-35'))"

# Testar NR via web (busca automática)
# Envie mensagem no Telegram: "o que diz a NR-18 construção civil"
```
