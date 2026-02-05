# Relatório de Auditoria Técnica - Assistente Digital

**Data:** 2026-02-05  
**Escopo:** Repositório completo (src/, docs/, tests/, config/)  
**Referências:** MEMORY.md, ARCHITECTURE.md, IDENTITY.md, POLICIES.md, docs/security/

---

## 1. Resumo executivo

O projeto é um bot Telegram com agente de IA (tool calling), segurança em camadas e documentação extensa. A auditoria identificou **conformidade parcial**: a arquitetura e a documentação estão alinhadas em grande parte, mas há **divergência entre a estrutura documentada (raiz do projeto) e a estrutura real (código em `src/`)**, além de **não conformidades críticas de segurança** que foram mitigadas em parte pelos módulos em `security/` mas **não aplicadas de forma consistente** em todos os pontos de uso (handlers de vídeo/áudio, filesystem, YouTube). Principais riscos: (1) **filesystem sem validação de path** (leitura/escrita arbitrária, incluindo `.env`); (2) **handlers de vídeo e áudio sem `@require_auth`** e uso de `subprocess.run` direto em vídeo (sem SafeSubprocessExecutor); (3) **rate limiting do agent não aplicado** no handler de mensagem (falta passar `user_id`); (4) **vazamento de detalhes de erro** para o usuário (`str(e)` em respostas). Recomenda-se priorizar: aplicar `@require_auth` e rate limit em todos os handlers sensíveis, restringir filesystem com `validate_path`, usar SafeSubprocessExecutor e SecureFileManager nos fluxos de mídia, e padronizar tratamento de erros sem expor stack ou mensagens técnicas.

---

## 2. Por dimensão

### 2.1 Arquitetura e estrutura

**O que foi verificado:** Consistência da estrutura com MEMORY.md e ARCHITECTURE.md; separação bot/agent/core/tools/security/config/utils; dependências entre módulos; código morto/duplicado; tamanho de arquivos.

**Conformidades:**
- Separação clara: `src/bot_simple.py` (entrada), `src/workspace/core/` (agent, tools), `src/workspace/tools/` (ferramentas), `src/security/`, `src/config/`, `src/utils/`.
- Registry de ferramentas em `workspace/core/tools.py`; agente em `workspace/core/agent.py`.
- Módulos de segurança (auth, rate_limiter, sanitizer, media_validator, file_manager, executor) presentes e exportados em `security/__init__.py`.
- MEMORY e ARCHITECTURE descrevem fluxo Telegram → Bot → Agent → LLM → Tools de forma coerente com o código.

**Não conformidades e riscos:**
- **Estrutura documentada vs real:** MEMORY.md e ARCHITECTURE.md descrevem árvore com `bot_simple.py`, `workspace/`, `security/`, `config/` na **raiz** do projeto. No repositório, o código está sob **`src/`** (ex.: `src/bot_simple.py`, `src/workspace/`, `src/security/`). Scripts e testes referem tanto a raiz quanto a `src/` e a caminhos absolutos como `/home/brunoadsba/clawd/moltbot-setup`, gerando confusão e risco de rodar código/ testes no diretório errado.
- **Código morto/legado:** `workspace/core/sandbox.py` é citado em MEMORY como "Não usado"; existe também referência a GLM em `agent.py` (`_call_glm_vision`) e uso de `GLM_API_KEY` no YouTube (IDENTITY/POLICIES indicam Groq como padrão). Duplicação conceitual entre `workspace/agent/` (IDENTITY, POLICIES, CONTEXT_PACK) e `workspace/core/agent.py` (implementação).
- **Tamanho de arquivos:** `src/bot_simple.py` tem **762 linhas** (meta documentada &lt; 200). `workspace/core/agent.py` tem **293 linhas**. MEMORY indica "bot_simple.py (640 linhas)" e "agent.py (180 linhas)" — números desatualizados e acima do alvo.
- **Duplicação:** Paths absolutos repetidos (ex.: `/tmp/moltbot_*`, `moltbot.db`) em vez de uso sistemático de `config.TEMP_DIR` / `config.DATABASE_PATH`.

**Recomendações:**
- **Crítico:** Atualizar MEMORY.md e ARCHITECTURE.md para refletir a estrutura real com `src/` e, se possível, consolidar um único diretório de trabalho (evitar referências a `clawd/moltbot-setup` na doc como se fosse a única raiz).
- **Alto:** Quebrar `bot_simple.py` em módulos (handlers por tipo de mídia, comandos, setup do app) para ficar abaixo de ~200 linhas por arquivo.
- **Médio:** Remover ou marcar claramente como legado `sandbox.py` e código GLM não usado; unificar documentação do agente (IDENTITY/POLICIES vs implementação em core/agent.py).
- **Baixo:** Reduzir complexidade de `agent.py` extraindo chamadas Groq/GLM e finalização de run para funções auxiliares.

---

### 2.2 Segurança

**O que foi verificado:** Autenticação e autorização; rate limiting; validação de entrada (filenames, path traversal, SafeSubprocessExecutor, whitelist de comandos); arquivos temporários (SecureFileManager, cleanup); validação de mídia (MIME, tamanho, extensões); gestão de segredos; tratamento de erros (não vazamento); conformidade com checklist em MEMORY e docs/security/.

**Conformidades:**
- **Autenticação:** `security/auth.py` com whitelist e decorator `@require_auth`; usado em `handle_message`, `handle_photo`, `handle_document` (bot_simple.py linhas 164, 244, 482).
- **Rate limiting:** `security/rate_limiter.py` com limites 20 msg/min, 5 mídia/min, 3 YouTube/5min; `agent.run()` verifica `message_limiter.is_allowed(user_id)` quando `user_id` é passado (agent.py 104–107).
- **SecureFileManager:** Implementado em `security/file_manager.py` (temp_file, temp_directory, sanitize_filename, validate_mime_type, validate_file_size, cleanup_old_files).
- **SafeSubprocessExecutor:** Implementado em `security/executor.py` (whitelist ffmpeg, ffprobe, tesseract, python; bloqueio de caracteres perigosos; timeout; tratamento de exit code 8 do ffmpeg).
- **Sanitizer:** `sanitize_youtube_url`, `sanitize_filename`, `validate_path` e `safe_subprocess` em `security/sanitizer.py`.
- **Config centralizada:** `config/settings.py` com paths e limites via env (MOLTBOT_DIR, MOLTBOT_TEMP, ALLOWED_USERS, etc.).
- **.env:** MEMORY e docs orientam chmod 600; não foi verificado no sistema de arquivos (N/A no repositório).

**Não conformidades e riscos:**
- **Handlers sem @require_auth:** `handle_video`, `handle_voice`, `handle_audio` **não** usam `@require_auth` (bot_simple.py 299, 400, 440). Qualquer usuário que consiga enviar mídia ao bot pode acionar esses fluxos, contrário a POLICIES.md ("SEMPRE usar @require_auth em handlers sensíveis").
- **Rate limiting não aplicado no texto:** Em `handle_message`, `agent.run()` é chamado como `agent.run(user_message, history)` **sem `user_id`** (linha 208). O rate limit dentro do agent nunca é acionado para mensagens de texto.
- **Filesystem sem validação de path:** `workspace/tools/filesystem.py` usa `os.path.expanduser(path)` diretamente em `read_file`, `write_file`, `list_directory`, **sem** chamar `validate_path` nem restringir a diretórios permitidos. Permite ler/escrever qualquer path (ex.: `.env`, `/etc/passwd`), conforme já apontado em SECURITY_AUDIT_REPORT.md.
- **Vídeo: subprocess e arquivos temporários:** Em `handle_video` (313–324) usa-se `subprocess.run` direto para ffmpeg e paths em `/tmp/` fixos, **sem** SafeSubprocessExecutor e **sem** SecureFileManager. Risco de command injection via file_id ou paths e ausência de cleanup garantido em falha.
- **YouTube:** `workspace/tools/youtube_analyzer.py` chama `subprocess.run` com `youtube_url` sem sanitização (linhas 18–25). `sanitize_youtube_url` existe em security mas **não é usado** no analyzer. Client-ID Imgur hardcoded (linha 60), citado no SECURITY_AUDIT_REPORT.
- **ALLOWED_USERS:** Em `auth.py` a lista é fixa `[6974901522]`; em `config/settings.py` há `ALLOWED_USERS` lido de env. O módulo auth **não** usa `config.ALLOWED_USERS`, então variável de ambiente não altera a whitelist.
- **Vazamento de erros:** Vários handlers fazem `await update.message.reply_text(f"❌ Erro: {str(e)}")` (ex.: bot_simple.py 200, 241, 296, 397, 438, 479, 696). POLICIES: "SEMPRE retornar erro amigável ao usuário, nunca stack trace"; `str(e)` pode expor caminhos ou detalhes internos.
- **Paths hardcoded:** `bot_simple.py` linha 148: `db_file = "/home/brunoadsba/clawd/moltbot-setup/moltbot.db"` no clear(); linha 217: `glob.glob("/tmp/tmp*.png")`. Deveriam usar `config.DATABASE_PATH` e `config.TEMP_DIR`.

**Recomendações:**
- **Crítico:** Em `workspace/tools/filesystem.py`, validar path com `validate_path` contra lista de bases permitidas (ex.: config.BASE_DIR, config.TEMP_DIR) antes de qualquer read/write/list; rejeitar com `{"success": False, "error": "..."}` se fora do permitido.
- **Crítico:** Aplicar `@require_auth` em `handle_video`, `handle_voice` e `handle_audio`.
- **Crítico:** Em `handle_message`, passar `user_id=update.effective_user.id` em `agent.run(user_message, history, user_id=update.effective_user.id)` para ativar rate limiting.
- **Alto:** Refatorar `handle_video` para usar SecureFileManager (temp_file) para vídeo/frame/áudio e SafeSubprocessExecutor para ffmpeg; garantir cleanup em bloco finally/context manager.
- **Alto:** No YouTube analyzer, validar URL com `sanitize_youtube_url` antes de passar para yt-dlp; usar SafeSubprocessExecutor (e incluir yt-dlp na whitelist) ou no mínimo `safe_subprocess` com lista de argumentos.
- **Alto:** Fazer `auth.py` usar `config.ALLOWED_USERS` quando não vazio, mantendo fallback para lista fixa apenas se env não definido.
- **Médio:** Substituir `reply_text(f"❌ Erro: {str(e)}")` por mensagem genérica ("Ocorreu um erro. Tente novamente.") e manter `str(e)` apenas em logs.
- **Médio:** Remover path hardcoded do clear() e do glob de gráficos; usar config.DATABASE_PATH e config.TEMP_DIR.
- **Baixo:** Mover Client-ID Imgur para variável de ambiente e documentar em .env.example.

---

### 2.3 Qualidade de código

**O que foi verificado:** Type hints; docstrings; padrão de retorno das tools; tratamento de exceções; uso de async/await; duplicação (DRY).

**Conformidades:**
- Ferramentas em `workspace/tools/` retornam em geral `{"success": True, "data": ...}` ou `{"success": False, "error": str}` (ex.: filesystem, rag_tools, code_tools, extra_tools, web_search).
- Type hints presentes em funções principais (ex.: auth.py, rate_limiter.py, file_manager.py, executor.py, retry.py, config/settings.py).
- Docstrings em estilo descritivo em security, utils e config.
- Código assíncrono consistente nos handlers e no agent; SafeSubprocessExecutor e retry com async.

**Não conformidades e riscos:**
- **ToolRegistry.execute:** Em `workspace/core/tools.py` (linhas 28–29), em caso de exceção retorna `{"error": str(e)}` em vez de `{"success": False, "error": str(e)}`, inconsistente com o padrão documentado e com as próprias tools.
- **agent.py:** O método `_finalize_run` é chamado com assinaturas diferentes: linha 184 `(run_dir, output_text, start_time, tools_used, status, messages)` e linha 255 `(run_dir, output_text, user_message, start_time, tools_used, status, messages)` — provável bug (parâmetro extra `user_message` e ordem distinta).
- **Bare except:** Em agent.py linha 173, `except:` sem tipo; em youtube_analyzer e em outros pontos há `except Exception` com `pass` ou mensagem genérica, podendo engolir erros.
- **Duplicação:** Lógica de download de mídia + path em `/tmp/` repetida em handle_voice, handle_audio, handle_document (paths e cleanup manual); poderia ser centralizada com SecureFileManager e um helper.

**Recomendações:**
- **Alto:** Padronizar retorno de erro do ToolRegistry: `return {"success": False, "error": str(e)}` e ajustar qualquer consumidor que espere só `error`.
- **Alto:** Corrigir assinatura e chamadas de `_finalize_run` em agent.py para uma única assinatura coerente com os usos.
- **Médio:** Substituir `except:` por `except Exception:` e logar; evitar `pass` sem log.
- **Médio:** Extrair helper para download de mídia com temp_file (SecureFileManager) e uso único em voice/audio/document.
- **Baixo:** Revisar type hints em bot_simple.py (handlers e callbacks) e em workspace/tools onde faltem.

---

### 2.4 Configuração e ambiente

**O que foi verificado:** Centralização em config/; ausência de paths/valores sensíveis hardcoded; uso de variáveis de ambiente; documentação de obrigatórias vs opcionais.

**Conformidades:**
- `config/settings.py` centraliza BASE_DIR, TEMP_DIR, modelos, limites, rate limits, ALLOWED_USERS (via property), DATABASE_PATH, REMINDERS_FILE.
- MEMORY.md descreve variáveis obrigatórias (TELEGRAM_TOKEN, GROQ_API_KEY) e opcionais (ELEVENLABS, EMAIL, SMTP, OPENWEATHER, NEWS_API_KEY, MOLTBOT_DIR, MOLTBOT_TEMP, ALLOWED_USERS).

**Não conformidades e riscos:**
- Path hardcoded em `bot_simple.py`: `db_file = "/home/brunoadsba/clawd/moltbot-setup/moltbot.db"` e `glob.glob("/tmp/tmp*.png")`.
- `auth.py` não usa config: ALLOWED_USERS e ADMIN_ID são listas/valores fixos; config.ALLOWED_USERS não é lido.
- **.env.example:** Não encontrado na raiz do repositório (MEMORY cita ".env.example"). Dificulta onboarding e documentação de variáveis.

**Recomendações:**
- **Alto:** Criar `.env.example` na raiz com todas as variáveis documentadas em MEMORY (obrigatórias e opcionais), sem valores reais.
- **Alto:** Eliminar paths hardcoded em bot_simple.py usando config.DATABASE_PATH e config.TEMP_DIR.
- **Médio:** Fazer auth.py usar config.ALLOWED_USERS (e opcionalmente um ADMIN_ID vindo de env) quando definidos.

---

### 2.5 Testes

**O que foi verificado:** Cobertura por tipo (E2E, integração, unitário); qualidade das assertivas; comando para rodar testes; lacunas em módulos críticos.

**Conformidades:**
- Existem testes em `tests/`: test_e2e_simple.py, test_e2e.py, test_bot_completo.py, test_bot_simples.py, test_bot_funcionalidades.py.
- test_e2e_simple.py cobre ToolRegistry, SQLiteStore, filesystem (read/write/list), e inclui pytest-asyncio.
- Padrão de assertivas claro (success, content, etc.) em vários testes.

**Não conformidades e riscos:**
- **Path e ambiente:** test_e2e_simple.py usa `sys.path.insert(0, '/home/brunoadsba/clawd/moltbot-setup')` — hardcoded; SQLiteStore("/tmp/test_moltbot.db") e write_file/read_file em "/tmp/test_moltbot.txt" — dependem de /tmp e do path do sistema.
- **Cobertura de segurança:** Não há testes para auth (require_auth), rate_limiter, SafeSubprocessExecutor, validate_path/sanitize_youtube_url, nem para filesystem com path inválido (path traversal).
- **Comando de testes:** MEMORY indica rodar de `clawd/moltbot-setup` com venv311; README não repete de forma explícita um único comando reproduzível a partir da raiz do repo (ex.: `cd src && python -m pytest ../tests/` ou similar). Dependência de ambiente externo ao repo.
- **Módulos sem testes:** security (auth, executor, file_manager, sanitizer, media_validator), config/settings, agent (run com e sem tool_calls, rate limit).

**Recomendações:**
- **Alto:** Incluir testes unitários para `validate_path` e `sanitize_youtube_url` (casos válidos e inválidos); para SafeSubprocessExecutor (comando permitido vs rejeitado, argumentos com caracteres perigosos); para require_auth (mock de update com user_id permitido e não permitido).
- **Alto:** Remover path absoluto de `sys.path` nos testes; usar `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))` ou variável de ambiente para raiz do projeto.
- **Médio:** Documentar no README e em MEMORY um comando único para rodar testes a partir da raiz (ex.: `python -m pytest tests/` com PYTHONPATH=src ou script de teste).
- **Médio:** Adicionar teste de filesystem que tente path fora do permitido e espere `success: False` (após implementar validação de path).
- **Baixo:** Testes de integração para agent.run (mock Groq) com e sem user_id (rate limit).

---

### 2.6 Documentação

**O que foi verificado:** Completude de README, MEMORY e docs/; atualização das decisões e fluxos; índice/navegação; runbooks e políticas vs comportamento.

**Conformidades:**
- README, MEMORY.md e docs/ (ARCHITECTURE, FEATURES, API_REFERENCE, TOOLS_REFERENCE, DEVELOPMENT, DOCS_INDEX, security/) cobrem arquitetura, funcionalidades, APIs, ferramentas e segurança.
- DOCS_INDEX.md oferece índice e mapa de navegação por persona.
- IDENTITY.md e POLICIES.md descrevem modelo, limites, regras de segurança e operação; em grande parte alinhados ao que está implementado (exceto onde a implementação não aplica as políticas em todos os pontos).

**Não conformidades e riscos:**
- MEMORY e ARCHITECTURE descrevem estrutura sem `src/` e mencionam "bot_simple.py (640 linhas)" e "agent.py (180 linhas)" — valores e árvore desatualizados.
- DOCS_INDEX referencia INSTANCE_MANAGEMENT.md e scripts em `clawd/moltbot-setup`; no repo atual os scripts estão em `scripts/` (start.sh, stop.sh) — pode não haver INSTANCE_MANAGEMENT.md nem scripts idênticos na raiz do assistente.
- README foca em "notícias diárias" e agendamento (07h, /noticias); em bot_simple.py não foi verificada implementação desse fluxo — possível doc de outro modo de execução ou feature não presente neste código.
- SECURITY_INDEX e SECURITY_AUDIT_REPORT referem "quick_security_fix.sh", "reset_and_start.sh" — não encontrados na raiz do repositório listada.

**Recomendações:**
- **Alto:** Atualizar MEMORY e ARCHITECTURE com estrutura real (src/), contagem de linhas atual e localização dos scripts (scripts/ na raiz do repo).
- **Médio:** Alinhar README ao que está em bot_simple.py (comandos e features realmente disponíveis) ou marcar seção "notícias" como outro produto/entrada.
- **Médio:** Garantir que DOCS_INDEX e security docs referenciem apenas arquivos/scripts existentes no repo ou indicar "opcional/externo" onde for o caso.
- **Baixo:** Adicionar ao DOCS_INDEX referência a este relatório de auditoria (docs/AUDITORIA_PROJETO.md).

---

### 2.7 Operação e resiliência

**O que foi verificado:** Logging (níveis, ausência de dados sensíveis); retry/backoff em APIs externas; timeouts em I/O e subprocessos; scripts de instância; fallbacks (modelo, vision, tools).

**Conformidades:**
- Logging com nível INFO em operações normais e ERROR em falhas; uso de logger em vez de print.
- SafeSubprocessExecutor aplica timeout (30s) e trata TimeoutError; agent usa max_iterations e fallback sem tools em falha de tool calling (agent.py 158–176).
- utils/retry.py implementa retry com backoff e jitter para funções async/sync.

**Não conformidades e riscos:**
- **Retry em chamadas Groq:** Nenhuma chamada a Groq em bot_simple ou agent usa `@retry_with_backoff`; falhas transitórias não são reattemptadas conforme documentado em MEMORY ("Retry com backoff em chamadas a APIs externas (ex.: Groq)").
- **Logs e sensibilidade:** Alguns logs incluem conteúdo de mensagem (`logger.info(f"Mensagem recebida de user_id=...: {user_message}")`); POLICIES proíbem logar conteúdo sensível — mensagens podem conter PII.
- **handle_video:** subprocess.run sem timeout explícito (apenas capture_output=True, check=True); em vídeos grandes pode travar.
- **Scripts de instância:** MEMORY descreve start_bot_safe.sh, stop_bot.sh, healthcheck.sh em `clawd/moltbot-setup`; no repo listado há scripts/start.sh e scripts/stop.sh — não foi verificado conteúdo nem se há healthcheck. Single-instance depende de uso correto desses scripts.

**Recomendações:**
- **Alto:** Aplicar `@retry_with_backoff` nas chamadas Groq (chat.completions, vision, audio) em agent e bot_simple, com exceções (ConnectionError, TimeoutError, 5xx).
- **Médio:** Reduzir log de conteúdo completo de mensagens; logar apenas user_id e tamanho ou hash quando necessário para debug.
- **Médio:** Em handle_video, usar SafeSubprocessExecutor (ou no mínimo subprocess com timeout) para ffmpeg.
- **Médio:** Incluir no repo (ou documentar) scripts start/stop/healthcheck equivalentes aos descritos em MEMORY, para garantir single-instance reproduzível.

---

### 2.8 Dependências e manutenção

**O que foi verificado:** requirements.txt (versões); dependências obsoletas ou não utilizadas; venv e setup.

**Conformidades:**
- requirements.txt existe na raiz com versões fixas (python-telegram-bot==20.7, groq==0.4.1, etc.).
- MEMORY descreve uso de venv e passos de setup (clone, venv, pip install, .env).

**Não conformidades e riscos:**
- **python-magic:** SecureFileManager usa `magic.from_file` (file_manager.py); `python-magic` **não** está em requirements.txt — validação de MIME pode estar desabilitada (fallback quando MAGIC_AVAILABLE = False).
- **Outras dependências:** chromadb, docker, ollama, rank-bm25, tiktoken estão listadas; não foi verificado uso direto em bot_simple/agent/tools — possível dependência de outros scripts ou uso indireto.
- **dotenv:** Uso de `load_dotenv()` em bot_simple; `python-dotenv` não está listado em requirements.txt — pode falhar em ambiente limpo.

**Recomendações:**
- **Crítico:** Adicionar `python-dotenv` e `python-magic` a requirements.txt (com versões fixas) para garantir que config e validação de MIME funcionem em novo ambiente.
- **Médio:** Revisar dependências (chromadb, docker, ollama, etc.); remover ou marcar como opcionais as não usadas pelo fluxo principal do bot.
- **Baixo:** Documentar em README/MEMORY dependências de sistema (ffmpeg, tesseract, yt-dlp) já referidas na doc.

---

## 3. Matriz de prioridades

| Prioridade | Dimensão        | Recomendação |
|-----------|------------------|--------------|
| Crítico   | Segurança       | Validar path em filesystem (validate_path) antes de read/write/list |
| Crítico   | Segurança       | Aplicar @require_auth em handle_video, handle_voice, handle_audio |
| Crítico   | Segurança       | Passar user_id em agent.run() em handle_message para rate limiting |
| Crítico   | Dependências    | Adicionar python-dotenv e python-magic ao requirements.txt |
| Alto      | Segurança       | Refatorar handle_video com SecureFileManager e SafeSubprocessExecutor |
| Alto      | Segurança       | Sanitizar URL no YouTube analyzer (sanitize_youtube_url) e usar executor ou safe_subprocess |
| Alto      | Segurança       | auth.py usar config.ALLOWED_USERS quando definido |
| Alto      | Segurança       | Mensagens de erro genéricas ao usuário (sem str(e)) |
| Alto      | Qualidade       | Padronizar retorno de erro do ToolRegistry (success: False, error) |
| Alto      | Qualidade       | Corrigir assinatura e chamadas de _finalize_run em agent.py |
| Alto      | Configuração    | Criar .env.example e eliminar paths hardcoded em bot_simple |
| Alto      | Testes          | Testes unitários para security (auth, executor, sanitizer, path) |
| Alto      | Testes          | Remover path absoluto de sys.path nos testes |
| Alto      | Operação        | Aplicar retry_with_backoff nas chamadas Groq |
| Médio     | Arquitetura     | Atualizar MEMORY/ARCHITECTURE com src/ e quebrar bot_simple em módulos |
| Médio     | Segurança       | Remover paths hardcoded (clear, glob) usando config |
| Médio     | Qualidade       | Evitar bare except; extrair helper de download de mídia |
| Médio     | Testes          | Comando único de testes documentado; teste filesystem path inválido |
| Médio     | Documentação    | Alinhar README e DOCS_INDEX aos scripts/arquivos existentes |
| Médio     | Operação        | Reduzir log de conteúdo de mensagens; timeout em handle_video |
| Baixo     | Arquitetura     | Marcar/remover sandbox e código GLM legado |
| Baixo     | Configuração    | Admin/ALLOWED_USERS via env em auth |
| Baixo     | Documentação    | Referência a AUDITORIA_PROJETO.md no DOCS_INDEX |

---

## 4. Checklist de ação

1. Adicionar `python-dotenv` e `python-magic` a `requirements.txt`.
2. Em `workspace/tools/filesystem.py`, importar `validate_path` (e config); antes de expanduser, validar path contra bases permitidas; retornar `{"success": False, "error": "..."}` se inválido.
3. Em `bot_simple.py`, aplicar `@require_auth` a `handle_video`, `handle_voice` e `handle_audio`.
4. Em `handle_message`, alterar chamada para `agent.run(user_message, history, user_id=update.effective_user.id)`.
5. Refatorar `handle_video`: usar `secure_files.temp_file()` para vídeo, frame e áudio; usar `SafeSubprocessExecutor.run()` para chamadas ffmpeg; garantir cleanup em finally ou context manager.
6. Em `youtube_analyzer.py`, chamar `sanitize_youtube_url(youtube_url)` antes de passar URL ao yt-dlp; usar SafeSubprocessExecutor (adicionar yt-dlp à whitelist) ou `safe_subprocess` com lista de argumentos.
7. Em `auth.py`, ler ALLOWED_USERS de `config.ALLOWED_USERS` quando não vazio; manter fallback para lista fixa apenas se env não definido.
8. Substituir todas as respostas `reply_text(f"❌ Erro: {str(e)}")` por mensagem genérica e manter detalhe apenas em logger.
9. Em `bot_simple.py`, usar `config.DATABASE_PATH` no clear() e `config.TEMP_DIR` no glob de gráficos; remover path absoluto de moltbot.db.
10. Em `workspace/core/tools.py`, em caso de exceção em execute, retornar `{"success": False, "error": str(e)}`.
11. Em `workspace/core/agent.py`, unificar assinatura e chamadas de `_finalize_run`.
12. Criar `.env.example` na raiz com variáveis documentadas em MEMORY (sem valores reais).
13. Adicionar testes unitários para require_auth, rate_limiter.is_allowed, SafeSubprocessExecutor (comando/args), sanitize_youtube_url, validate_path (path válido/inválido).
14. Nos testes, substituir `sys.path.insert(0, '...')` por path derivado do projeto (ex.: `Path(__file__).resolve().parent.parent / "src"`).
15. Documentar em README/MEMORY comando reproduzível para rodar testes (ex.: `PYTHONPATH=src python -m pytest tests/`).
16. Aplicar `@retry_with_backoff` nas chamadas Groq em agent e bot_simple (chat, vision, audio).
17. Atualizar MEMORY.md e ARCHITECTURE.md com estrutura real (src/), contagem de linhas atual e localização dos scripts.
18. Quebrar `bot_simple.py` em módulos (handlers, comandos, setup) para reduzir linhas por arquivo.
19. Reduzir logging de conteúdo completo de mensagens (apenas user_id e metadados quando necessário).
20. Incluir referência a `docs/AUDITORIA_PROJETO.md` no DOCS_INDEX e, se aplicável, no README.

---

**Fim do relatório.**
