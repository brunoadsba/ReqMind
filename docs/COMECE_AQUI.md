# Comece aqui – Assistente Digital

Guia único para não se perder no projeto.

---

## 1. O que é este projeto

Bot do Telegram que usa IA (Groq), com memória persistente, análise de mídia, arquivos, busca na web, etc. O código do bot está em `src/` (entrada: `src/bot_simple.py`).

---

## 2. Comandos do dia a dia (na raiz do projeto)

| O que fazer | Comando |
|-------------|---------|
| Ver todos os comandos | `make help` |
| Iniciar o bot (local) | `make start` |
| Parar o bot (local) | `make stop` |
| Bot está rodando? | `make status` |
| Ver todas as instâncias do bot | `make instancias` |
| Rodar testes | `make test` |

**Importante:** Só pode haver **uma** instância do bot por token (local **ou** nuvem). Se o bot responde no Telegram mas `make status` diz que não está rodando, a instância ativa está em outro lugar (nuvem, outro PC).

---

## 2.1. Bot não responde ou dá erro 409?

Pode ser outra instância usando o mesmo token. Confira:

1. **Outro processo no mesmo PC:** `make instancias` (lista processos com "bot_simple").
2. **Container Docker:** `docker ps` — se existir algo como `assistente-telegram` ou outro bot com o mesmo token, pare/remova: `docker stop <nome>` ou `docker rm -f <nome>`.
3. **Bot na nuvem ou em outro PC:** pare essa instância se quiser usar só o local, ou use só a remota e faça `make stop` no seu PC.

Só uma conexão (polling) por token é permitida pelo Telegram.

---

## 3. Pré-requisitos

- Python 3.11+ com `venv` na pasta do projeto
- Arquivo `.env` na raiz (copie de `.env.example`) com pelo menos:
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

---

## 5. Se ainda estiver perdido

1. Abra o **README.md** e use só a seção **"Guia rápido – Bot"**.
2. No terminal, na pasta do projeto: `make help`.
3. Para desenvolvimento e detalhes: `docs/DOCS_INDEX.md`.

O restante da documentação em `docs/` é referência; você não precisa ler tudo para rodar o bot.
