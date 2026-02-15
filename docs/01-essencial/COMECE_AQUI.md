# Comece aqui – Assistente Digital

Guia único para não se perder no projeto.

---

## 1. O que é este projeto

Bot do Telegram que usa IA (Groq), com memória persistente, análise de mídia, arquivos, busca na web, etc. O código do bot está em `src/` (entrada: `src/bot_simple.py`).

---

## 2. Comandos do dia a dia (na raiz do projeto)

O bot deve ser rodado **apenas com Docker**.

| O que fazer | Comando |
|-------------|---------|
| Ver todos os comandos | `make help` |
| Iniciar o bot | `make start-docker` |
| Parar o bot | `make stop-docker` |
| Bot está rodando? | `make status-docker` |
| Ver logs do bot | `docker logs -f assistente-bot` |
| Rodar testes | `make test` |

**Importante:** Só pode haver **uma** instância do bot por token. Se o bot responde no Telegram mas `make status-docker` não mostra container, a instância ativa está em outro lugar (outro PC, outra máquina).

---

## 2.1. Bot não responde ou dá erro 409?

Pode ser outra instância usando o mesmo token. Confira:

1. **Container Docker no seu PC:** `docker ps` — se existir outro container com o mesmo token (ex.: `assistente-bot` ou nome antigo), pare: `make stop-docker` ou `docker stop <nome>`.
2. **Outro processo no mesmo PC (sem Docker):** `make instancias` (lista processos com "bot_simple"); pare com `make stop` se tiver usado `make start` antes.
3. **Bot na nuvem ou em outro PC:** pare essa instância se quiser usar só o local, ou use só a remota e faça `make stop-docker` no seu PC.

Só uma conexão (polling) por token é permitida pelo Telegram.

---

## 3. Pré-requisitos

- **Docker** instalado ([Get Docker](https://docs.docker.com/get-docker/))
- Arquivo `.env` na raiz do projeto (copie de `.env.example`) com pelo menos:
  - `TELEGRAM_TOKEN`
  - `GROQ_API_KEY`
- Opcional: `NVIDIA_API_KEY` — quando o Groq atinge o limite (429), o bot tenta Kimi K2.5 (NVIDIA); se não houver chave ou falhar, responde a partir da memória RAG (ex.: NR-29)

---

## 4. Onde está cada coisa

| Você quer | Onde olhar |
|-----------|------------|
| Início rápido (bot, make, .env) | `README.md` (seção "Guia rápido") |
| Lista completa de comandos make | `make help` |
| Estrutura do código | `README.md` (seção "Estrutura do Projeto") |
| Documentação técnica (arquitetura, testes, segurança) | `docs/DOCS_INDEX.md` |
| O que está pronto / pendente | `docs/STATUS_PENDENTE.md` |
| Modelo de 3 camadas e diagnóstico (se falhou, qual camada?) | `docs/COMPARATIVO_OPENCLAW_REQMIND.md` (seção "Como funciona na realidade") |
| Verificar processo, env e carregamento do agente | `make health` |

---

## 5. Normas Regulamentadoras (NRs)

O assistente possui um **sistema híbrido** para consultar NRs de SST:

### NRs em memória (instantâneo)
| NR | Tema |
|----|------|
| NR-1 | Disposições Gerais e Gerenciamento de Riscos |
| NR-5 | CIPA |
| NR-6 | EPI |
| NR-10 | Eletricidade |
| NR-29 | Trabalho Portuário |
| NR-35 | Trabalho em Altura |

### Como usar

```
Usuário: "me explica a NR-35 trabalho em altura"
→ Bot responde instantaneamente (NR-35 está na memória)

Usuário: "o que diz a NR-18 construção civil"
→ Bot faz web search e retorna resultado atualizado
```

### Exemplos práticos
- "quais são os EPIs obrigatórios segundo NR-6"
- "resumo da NR-10 instalações elétricas"
- "o que a NR-1 diz sobre gerenciamento de riscos"

### Para desenvolvedores
Ver `PLANO_NRS_HIBRIDO.md` para detalhes da implementação.

---

## 6. Se ainda estiver perdido

1. Abra o **README.md** e use só a seção **"Guia rápido – Bot"**.
2. No terminal, na pasta do projeto: `make help`.
3. Para desenvolvimento e detalhes: `docs/DOCS_INDEX.md`.

O restante da documentação em `docs/` é referência; você não precisa ler tudo para rodar o bot.
