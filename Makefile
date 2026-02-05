# Makefile - alvos padrão para desenvolvimento
# Uso: make install, make test, make lint

.PHONY: install test lint test-sync clean help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install   - Instala dependências (pip -r requirements.txt)"
	@echo "  make test     - Roda todos os testes (pytest)"
	@echo "  make test-sync - Roda apenas testes síncronos (evita segfault em alguns ambientes)"
	@echo "  make lint     - Verifica código com Ruff"
	@echo "  make clean    - Remove cache e artefatos"

install:
	pip install -r requirements.txt

test:
	PYTHONPATH=src python -m pytest tests/ -v --tb=short

test-sync:
	PYTHONPATH=src python -m pytest \
		tests/test_e2e_simple.py::test_sqlite_store \
		tests/test_security.py::test_sanitize_youtube_url_valid \
		tests/test_security.py::test_sanitize_youtube_url_invalid \
		tests/test_security.py::test_validate_path_allowed \
		tests/test_security.py::test_validate_path_traversal_rejected \
		-v --tb=short

lint:
	ruff check src/ tests/ || true

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ src/**/__pycache__ tests/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
