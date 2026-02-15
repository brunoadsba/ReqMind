# O que foi implementado e o que está pendente

**Última atualização:** 2026-02-06

---

## Implementado (desta rodada de trabalho)

### 1. Fallback e leitura de arquivo em 429 (solucoes-erros.md)

| Item | Onde |
|------|------|
| Leitura direta de arquivo em 429 | `agent.py`: quando há 429 e a mensagem pede leitura de arquivo, extrai path, chama `read_file`, devolve conteúdo truncado (4000 chars) + aviso. Dois fluxos: 429 principal e 429 após tool error. |
| Helpers `_extract_file_path` e `_truncate` | `agent.py` |
| Logs de diagnóstico em Kimi/GLM | `nvidia_kimi.py`, `glm_client.py`: status ≠ 200 com trecho do body; resposta vazia/sem choices logada; timeout em nível error. |
| Log de presença de chaves na inicialização | `bot_simple.py`: `Config: NVIDIA_KEY=SET|MISSING GLM_KEY=SET|MISSING` |

**Pendente (opcional):** retry com Session em Kimi/GLM; validação de `.env` sem aspas é manual (documentado).

---

### 2. Resumo de arquivo correto (MEMORY.md / blocos inventados)

| Item | Onde |
|------|------|
| Regra “usar só conteúdo de read_file; citar títulos reais; não inventar seções” | `POLICIES.md` (regra 57), `STYLE.md` (seção “Resumo de arquivos”), `CONTEXT_PACK.md` regenerado. |
| Enriquecimento do resultado de read_file para arquivos longos | `agent.py`: para conteúdo > 10k caracteres, envia campo `structure` (títulos ##/###) e conteúdo truncado em 14k, para o modelo ancorar no documento real. |
| Helper `_extract_markdown_headings` | `agent.py` |
| Testes | `test_extract_file_path`, `test_extract_markdown_headings` em `tests/test_fixes_bot.py` |

Doc: `docs/INVESTIGACAO_RESUMO_ARQUIVO.md`.

---

### 3. Modelo 3 camadas e health check (COMPARATIVO_OPENCLAW_REQMIND)

| Item | Onde |
|------|------|
| Seção “Como funciona na realidade” | `docs/COMPARATIVO_OPENCLAW_REQMIND.md`: 3 camadas (Motor, Gateway, Habilidades), fluxo, tabela “Se falhou, qual camada?”. |
| Health check unificado | `scripts/health_check.py`: verifica container, .env (TELEGRAM, GROQ, opcionais NVIDIA/GLM), carregamento do agente/tools. |
| Comando `make health` | `Makefile`; `make help` atualizado. |
| Referência no COMECE_AQUI | `docs/COMECE_AQUI.md`: link para o comparativo e para `make health`. |

---

### 4. Outros

| Item | Onde |
|------|------|
| Dependências de teste | `requirements.txt`: `pluggy`, `iniconfig` para pytest. |
| Comparativo OpenClaw vs ReqMind | `docs/COMPARATIVO_OPENCLAW_REQMIND.md` (criado/atualizado). |

---

## Pendente (desta rodada)

| Item | Observação |
|------|------------|
| Gateway explícito / múltiplas UIs | API HTTP ou WebSocket para outros clientes além do Telegram. Opcional; exige novo serviço e autenticação. |
| Retry com Session em Kimi/GLM | Robustez extra nas chamadas de fallback; não essencial. |
| Validação automática de .env no Docker | Confirmar chaves dentro do container (ex.: `docker exec ... env \| grep`); hoje é manual. |

---

## Pendente (geral – STATUS_PENDENTE.md)

Resumo do que já constava como pendente no projeto:

- **Melhorias futuras:** consolidar diretórios, PostgreSQL, cache Redis, logging JSON, mais testes (cobertura > 70%), CI/CD, Docker Compose, monitoramento (Sentry/Prometheus), MemoryManager/embeddings, dashboard de métricas.
- **Roadmap longo prazo:** Kubernetes, múltiplas instâncias, message queue, API REST, múltiplos usuários.
- **Documentação:** revisar MEMORY.md com estrutura modularizada, documentar handlers em ARCHITECTURE.md.

Detalhes: `docs/STATUS_PENDENTE.md`.
