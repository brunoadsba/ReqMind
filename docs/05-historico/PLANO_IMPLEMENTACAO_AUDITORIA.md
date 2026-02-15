# Plano de Implementação – Itens da Auditoria

**Base:** [AUDITORIA_PROJETO.md](./AUDITORIA_PROJETO.md) (2026-02-05)  
**Objetivo:** Executar as recomendações da auditoria em fases priorizadas, com critérios de conclusão e dependências explícitas.

---

## Visão geral das fases

| Fase | Foco | Prioridade | Estimativa |
|------|------|------------|------------|
| 0 | Bloqueadores e dependências | Crítico | 0,5 dia |
| 1 | Segurança crítica (auth, rate limit, filesystem) | Crítico | 1 dia |
| 2 | Segurança mídia e erros (vídeo, YouTube, mensagens) | Alto | 1,5 dias |
| 3 | Qualidade e configuração (ToolRegistry, agent, config, paths) | Alto | 1 dia |
| 4 | Testes (security, paths, comando) | Alto | 1 dia |
| 5 | Operação (retry Groq, logging) | Alto/Médio | 0,5 dia |
| 6 | Documentação e refatoração | Médio/Baixo | 1–2 dias |

**Total estimado:** 6–7 dias de desenvolvimento focado.

---

## Fase 0 – Bloqueadores e dependências (Crítico)

Objetivo: ambiente e dependências corretas para config, validação de MIME e testes.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 0.1 | Adicionar `python-dotenv` e `python-magic` ao requirements.txt com versões fixas | `requirements.txt` | `pip install -r requirements.txt` em venv novo sem erro; `python -c "import dotenv; import magic"` OK | - |
| 0.2 | Criar `.env.example` na raiz com todas as variáveis de MEMORY (obrigatórias e opcionais), sem valores reais | `.env.example` | Arquivo existe; variáveis TELEGRAM_TOKEN, GROQ_API_KEY, MOLTBOT_DIR, MOLTBOT_TEMP, ALLOWED_USERS, etc. documentadas com comentário | - |

**Verificação Fase 0:** Novo clone + venv + `pip install -r requirements.txt` + `cp .env.example .env` permite rodar o bot após preencher .env.

---

## Fase 1 – Segurança crítica (Crítico)

Objetivo: auth em todos os handlers sensíveis, rate limit no texto, filesystem restrito.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 1.1 | Aplicar `@require_auth` em `handle_video`, `handle_voice`, `handle_audio` | `src/bot_simple.py` | Os três handlers decorados com `@require_auth`; usuário não autorizado recebe "Acesso negado" ao enviar mídia | - |
| 1.2 | Em `handle_message`, passar `user_id=update.effective_user.id` em `agent.run(...)` | `src/bot_simple.py` | Chamada `agent.run(user_message, history, user_id=update.effective_user.id)`; ao exceder 20 msg/min, usuário recebe mensagem de rate limit | - |
| 1.3 | Em `workspace/tools/filesystem.py`, validar path com `validate_path` contra bases permitidas (config.BASE_DIR, config.TEMP_DIR) antes de read/write/list; rejeitar com `{"success": False, "error": "..."}` se fora do permitido | `src/workspace/tools/filesystem.py`, `src/config/settings.py` | read_file/list_directory/write_file chamam validate_path; path como `../../etc/passwd` ou `.env` retorna success False; testes manuais ou unitários cobrindo path válido e inválido | 0.1 |
| 1.4 | Em `auth.py`, usar `config.ALLOWED_USERS` quando não vazio; fallback para lista fixa só se env não definido | `src/security/auth.py` | ALLOWED_USERS carregado de config; definir ALLOWED_USERS no .env altera whitelist efetiva | 0.1 |

**Verificação Fase 1:** (1) Usuário não autorizado não consegue enviar texto, foto, vídeo, voz, áudio, documento. (2) Após 20 mensagens em 1 min, próxima mensagem retorna aviso de rate limit. (3) Tool read_file com path fora do permitido retorna erro sem ler arquivo.

---

## Fase 2 – Segurança mídia e erros (Alto)

Objetivo: handle_video seguro (SecureFileManager + SafeSubprocessExecutor), YouTube sanitizado, erros genéricos ao usuário.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 2.1 | Refatorar `handle_video`: usar `secure_files.temp_file()` para vídeo, frame e áudio; usar `SafeSubprocessExecutor.run()` para ffmpeg; cleanup em context manager ou finally | `src/bot_simple.py` | Nenhum `subprocess.run` direto em handle_video; paths vêm de temp_file; ffmpeg via SafeSubprocessExecutor; arquivos removidos mesmo em falha | 1.1 |
| 2.2 | Incluir `yt-dlp` na whitelist de SafeSubprocessExecutor; em youtube_analyzer chamar `sanitize_youtube_url(youtube_url)` antes de passar URL ao yt-dlp; usar SafeSubprocessExecutor (ou safe_subprocess) para o comando yt-dlp | `src/security/executor.py`, `src/workspace/tools/youtube_analyzer.py` | URL inválida rejeitada antes de subprocess; comando yt-dlp executado via executor seguro com timeout; argumentos validados | 1.3 |
| 2.3 | Substituir todas as respostas `reply_text(f"❌ Erro: {str(e)}")` por mensagem genérica (ex.: "Ocorreu um erro. Tente novamente."); manter `str(e)` apenas em logger | `src/bot_simple.py` (e outros handlers se houver) | Busca por "str(e)" em reply_text não retorna resultados; logs continuam com detalhe do erro | - |
| 2.4 | Em bot_simple: clear() usar `config.DATABASE_PATH`; glob de gráficos usar `config.TEMP_DIR`; remover path absoluto de moltbot.db | `src/bot_simple.py` | Nenhum path absoluto "/home/brunoadsba/..." ou "/tmp/..." fixo para db ou temp de gráficos | 0.1 |

**Verificação Fase 2:** (1) Envio de vídeo não deixa arquivos em /tmp ao falhar. (2) URL do YouTube malformada não chega ao subprocess. (3) Usuário nunca vê stack trace nem caminho de arquivo em mensagem de erro.

---

## Fase 3 – Qualidade e configuração (Alto)

Objetivo: retorno padronizado do ToolRegistry, _finalize_run consistente, configuração centralizada usada.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 3.1 | Em `workspace/core/tools.py`, em exceção em execute retornar `{"success": False, "error": str(e)}`; ajustar consumidores que esperem só `error` | `src/workspace/core/tools.py`, `src/workspace/core/agent.py` (se necessário) | execute em falha retorna dict com success False e error; agent ou outros que leem resultado tratam esse formato | - |
| 3.2 | Unificar assinatura e chamadas de `_finalize_run` em agent.py (uma única assinatura coerente com todos os usos) | `src/workspace/core/agent.py` | Duas chamadas a _finalize_run usam a mesma assinatura; nenhum parâmetro trocado de ordem ou omitido | - |
| 3.3 | Substituir `except:` por `except Exception:` em agent.py (e outros pontos) e logar; evitar `pass` sem log | `src/workspace/core/agent.py`, `src/workspace/tools/youtube_analyzer.py` | Grep por "except:" sem tipo não encontra; onde havia pass, há pelo menos logger.debug ou logger.warning | - |

**Verificação Fase 3:** (1) Resposta de tool com falha tem success False. (2) Runs são finalizados com métricas corretas. (3) Exceções não são engolidas silenciosamente.

---

## Fase 4 – Testes (Alto)

Objetivo: testes de segurança, paths de projeto portáteis, comando de testes documentado.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 4.1 | Nos testes, substituir `sys.path.insert(0, '...')` por path derivado do projeto (ex.: `Path(__file__).resolve().parent.parent / "src"`) | `tests/test_e2e_simple.py`, outros em `tests/` que usem path absoluto | Nenhum path absoluto tipo `/home/.../clawd/moltbot-setup` em testes; testes rodam a partir da raiz do repo em máquina diferente | - |
| 4.2 | Adicionar testes unitários: require_auth (mock update com user permitido/não permitido); rate_limiter.is_allowed; SafeSubprocessExecutor (comando permitido vs rejeitado, args perigosos); sanitize_youtube_url (URL válida/inválida); validate_path (path válido/inválido) | `tests/test_security.py` (ou módulos em tests/) | pytest executa novos testes; todos passam; cobertura para auth, rate_limiter, executor, sanitizer, validate_path | 1.3, 2.2 |
| 4.3 | Adicionar teste de filesystem com path fora do permitido (esperar success False) | `tests/test_e2e_simple.py` ou `tests/test_filesystem.py` | Teste chama read_file com path que deve ser rejeitado; assert result["success"] is False | 1.3 |
| 4.4 | Documentar em README e MEMORY comando reproduzível para rodar testes (ex.: `PYTHONPATH=src python -m pytest tests/` ou `python -m pytest tests/` com instrução de ativar venv e PYTHONPATH) | `README.md`, `MEMORY.md` | Seção "Testes" ou "Como rodar testes" com um comando copiável; MEMORY atualizado com mesmo comando | - |

**Verificação Fase 4:** `PYTHONPATH=src python -m pytest tests/` (ou o comando documentado) executa todos os testes a partir da raiz, incluindo os novos de segurança.

---

## Fase 5 – Operação (Alto/Médio)

Objetivo: retry em chamadas Groq, logging sem conteúdo sensível de mensagem.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 5.1 | Aplicar `@retry_with_backoff` nas chamadas Groq (chat.completions, vision, audio) em agent e bot_simple, com exceções (ConnectionError, TimeoutError, 5xx se aplicável) | `src/workspace/core/agent.py`, `src/bot_simple.py` | Funções que chamam groq.chat.completions.create ou groq.audio.* decoradas com retry; em falha transitória há retentativa antes de falhar | 0.1 |
| 5.2 | Reduzir log de conteúdo completo de mensagens: logar apenas user_id e tamanho (ou hash) quando necessário para debug; evitar logar `user_message` inteiro em produção | `src/bot_simple.py`, `src/workspace/core/agent.py` | Log de "Mensagem recebida" não inclui texto completo da mensagem; inclui user_id e talvez len(message) ou hash | - |

**Verificação Fase 5:** (1) Simular falha temporária de rede na chamada Groq e observar retentativa no log. (2) Logs não contêm corpo da mensagem do usuário.

---

## Fase 6 – Documentação e refatoração (Médio/Baixo)

Objetivo: doc alinhada ao código, bot_simple modularizado, referência à auditoria.

| ID | Ação | Arquivos | Critério de conclusão | Depends |
|----|------|----------|------------------------|--------|
| 6.1 | Atualizar MEMORY.md e ARCHITECTURE.md com estrutura real (src/), contagem de linhas atual, localização dos scripts (scripts/ na raiz) | `MEMORY.md`, `docs/ARCHITECTURE.md` | Árvore de diretórios mostra src/; números de linhas de bot_simple e agent atualizados; scripts referenciam scripts/ na raiz do repo | - |
| 6.2 | Incluir referência a docs/AUDITORIA_PROJETO.md e a este plano (docs/PLANO_IMPLEMENTACAO_AUDITORIA.md) no DOCS_INDEX | `docs/DOCS_INDEX.md` | DOCS_INDEX contém links para Auditoria e Plano de Implementação | - |
| 6.3 | Quebrar bot_simple.py em módulos (handlers por tipo de mídia, comandos, setup do app) para ficar abaixo de ~200 linhas por arquivo | `src/bot_simple.py`, novos em `src/` (ex.: `src/handlers/`, `src/commands.py`) | Nenhum arquivo Python do bot com mais de 200 linhas; bot_simple.py importa e registra handlers | 2.1, 2.3 |
| 6.4 | (Opcional) Marcar ou remover sandbox.py e código GLM não usado; mover Client-ID Imgur para variável de ambiente e documentar em .env.example | `src/workspace/core/sandbox.py`, `src/workspace/tools/youtube_analyzer.py`, `.env.example` | sandbox claramente marcado como legado ou removido; IMGUR_CLIENT_ID em .env.example | 0.2 |

**Verificação Fase 6:** Novo desenvolvedor lê MEMORY/ARCHITECTURE e encontra estrutura e números corretos; DOCS_INDEX aponta para auditoria e plano; bot_simple e módulos com tamanho controlado.

---

## Ordem sugerida de execução (fluxo linear)

1. **Fase 0** (0.1, 0.2)  
2. **Fase 1** (1.1, 1.2, 1.3, 1.4)  
3. **Fase 2** (2.3, 2.4, 2.1, 2.2) — 2.3 e 2.4 podem vir antes de 2.1/2.2  
4. **Fase 3** (3.1, 3.2, 3.3)  
5. **Fase 4** (4.1, 4.2, 4.3, 4.4)  
6. **Fase 5** (5.1, 5.2)  
7. **Fase 6** (6.1, 6.2, 6.3, 6.4 opcional)

---

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Validação de path quebra fluxos legítimos (ex.: read_file em projeto) | Definir allowed_bases incluindo BASE_DIR e TEMP_DIR; testar com paths reais usados pelas tools. |
| SafeSubprocessExecutor sem yt-dlp causa falha no YouTube | Incluir yt-dlp na whitelist na mesma alteração que o uso no analyzer. |
| Retry em Groq mascarar erros permanentes (ex.: quota) | Limitar max_retries (ex.: 3) e usar exceções específicas (ConnectionError, TimeoutError); logar após último retry. |
| Quebrar bot_simple introduz regressões | Fazer 6.3 após Fase 4 (testes estáveis); rodar suite E2E após refatoração. |

---

## Checklist de conclusão do plano

- [ ] Fase 0: requirements e .env.example
- [ ] Fase 1: @require_auth em todos os handlers sensíveis; user_id em agent.run; filesystem com validate_path; auth com config.ALLOWED_USERS
- [ ] Fase 2: handle_video com SecureFileManager + SafeSubprocessExecutor; YouTube com sanitize e executor; erros genéricos; paths em config
- [ ] Fase 3: ToolRegistry retorno padronizado; _finalize_run unificado; except explícito e log
- [ ] Fase 4: Testes com path portável; testes de security; teste filesystem path inválido; comando de testes documentado
- [ ] Fase 5: Retry Groq; log sem conteúdo completo de mensagem
- [ ] Fase 6: MEMORY/ARCHITECTURE atualizados; DOCS_INDEX com auditoria e plano; bot_simple modularizado (e opcionalmente sandbox/Imgur)

---

**Documento criado a partir de:** [AUDITORIA_PROJETO.md](./AUDITORIA_PROJETO.md).  
**Última atualização:** 2026-02-05.

---

## Status da execução (2026-02-05 - ATUALIZADO)

- **Fases 0 a 6** implementadas completamente, incluindo:
  - ✅ **6.3** - `bot_simple.py` modularizado (160 linhas, abaixo da meta de 200)
  - ✅ **6.4** - Código legado limpo (sandbox marcado, GLM removido, Imgur em .env)
- **Testes:** Em ambientes onde `python-magic` causa segfault ao importar, rode apenas testes que não carreguem o pacote `security` completo, ou use um venv com `python-magic` instalado corretamente (dependência de sistema `libmagic`).
- **Status geral:** ✅ **TODAS AS FASES DO PLANO CONCLUÍDAS**
