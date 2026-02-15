# Makefile - alvos padrão para desenvolvimento
# Uso: make install, make test, make lint

.PHONY: install test test-all test-sync lint clean help start stop status instancias start-docker stop-docker status-docker health

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala dependências (pip -r requirements.txt)"
	@echo "  make start     - Inicia o bot Telegram (scripts/start.sh)"
	@echo "  make stop      - Encerra o bot Telegram (scripts/stop.sh)"
	@echo "  make status    - Verifica se o bot está rodando"
	@echo "  make instancias - Lista todas as instâncias do bot (pgrep -af bot_simple)"
	@echo "  make health    - Health check (container, .env, agente/tools)"
	@echo "  make test     - Suíte estável (SQLite + segurança; recomendado)"
	@echo "  make test-all - Todos os testes (pode segfault/erro ctypes no Python do sistema; use venv)"
	@echo "  make test-sync - Alias para make test"
	@echo "  make lint     - Verifica código com Ruff"
	@echo "  make clean    - Remove cache e artefatos"
	@echo "  make start-docker - Builda imagem Docker e inicia o bot em container"
	@echo "  make stop-docker  - Para o container do bot"
	@echo "  make status-docker - Mostra status do container do bot"

start:
	@bash scripts/start.sh

stop:
	@bash scripts/stop.sh

status:
	@bash scripts/status.sh

instancias:
	@pgrep -af "bot_simple" 2>/dev/null | grep -v "pgrep\|grep\|make" || echo "Nenhum processo com 'bot_simple'."

install:
	python3 -m venv venv || true
	./venv/bin/pip install -r requirements.txt

# Suíte estável: evita segfault (logging/asyncio) e ctypes (pandas) em alguns ambientes
test test-sync:
	PYTHONPATH=src python -m pytest \
		tests/test_fixes_bot.py \
		tests/test_e2e_simple.py::test_sqlite_store \
		tests/test_security.py::test_sanitize_youtube_url_valid \
		tests/test_security.py::test_sanitize_youtube_url_invalid \
		tests/test_security.py::test_validate_path_allowed \
		tests/test_security.py::test_validate_path_traversal_rejected \
		-v --tb=short

# Todos os testes (ignora test_bot_funcionalidades por ctypes; testes async podem dar segfault)
test-all:
	PYTHONPATH=src python -m pytest tests/ --ignore=tests/test_bot_funcionalidades.py -v --tb=short

lint:
	ruff check src/ tests/ || true

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ src/**/__pycache__ tests/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

backup:
	@echo "Backup simples de dados:"
	@echo "  - O diretório de dados atual é definido por config.DATA_DIR (ver src/config/settings.py)."
	@echo "  - Para backup local, copie esse diretório manualmente para um local seguro (ex.: cp -r dados backups/)."

start-docker:
	docker build -t assistente-bot .
	docker run --rm -d \
		--name assistente-bot \
		--env-file .env \
		-v $$(pwd)/dados:/app/dados \
		assistente-bot

stop-docker:
	-docker stop assistente-bot

status-docker:
	@docker ps --filter "name=assistente-bot" --format "table {{.Names}}\t{{.Status}}" || true

health:
	PYTHONPATH=src python scripts/health_check.py