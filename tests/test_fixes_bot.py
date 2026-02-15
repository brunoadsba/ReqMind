"""Testes unitários das correções: memória 'sobre mim', list_directory diretório projeto (sync apenas)."""
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
sys.path.insert(0, str(_src))


def test_normalize_project_path_empty_or_dot():
    """_normalize_project_path retorna BASE_DIR para '.' e vazio."""
    from workspace.tools.filesystem import _normalize_project_path
    from config.settings import config

    base = str(config.BASE_DIR)
    assert _normalize_project_path("") == base
    assert _normalize_project_path(".") == base
    assert _normalize_project_path("  .  ") == base


def test_normalize_project_path_keywords():
    """_normalize_project_path retorna BASE_DIR para 'diretório atual do projeto' etc."""
    from workspace.tools.filesystem import _normalize_project_path
    from config.settings import config

    base = str(config.BASE_DIR)
    assert _normalize_project_path("diretório atual do projeto") == base
    assert _normalize_project_path("Diretório Atual do Projeto") == base
    assert _normalize_project_path("diretorio atual") == base
    assert _normalize_project_path("atual") == base


def test_normalize_project_path_passthrough():
    """_normalize_project_path não altera path absoluto válido."""
    from workspace.tools.filesystem import _normalize_project_path

    path = "/tmp/outro"
    assert _normalize_project_path(path) == path


def test_memory_is_about_me_query():
    """MemoryManager._is_about_me_query identifica perguntas sobre o usuário."""
    from workspace.memory.memory_manager import MemoryManager

    assert MemoryManager._is_about_me_query("O que você sabe sobre mim como usuário?") is True
    assert MemoryManager._is_about_me_query("o que tem salvo na memória sobre minhas preferências?") is True
    assert MemoryManager._is_about_me_query("minhas preferências") is True
    assert MemoryManager._is_about_me_query("Liste os arquivos do diretório") is False
    assert MemoryManager._is_about_me_query("") is False


def test_user_asked_to_read_file():
    """Agent._user_asked_to_read_file identifica pedidos de leitura de arquivo."""
    from workspace.core.agent import Agent

    assert Agent._user_asked_to_read_file("Leia o conteúdo do arquivo MEMORY.md e resuma.") is True
    assert Agent._user_asked_to_read_file("conteúdo do arquivo README") is True
    assert Agent._user_asked_to_read_file("resuma o arquivo X") is True
    assert Agent._user_asked_to_read_file("O que você sabe sobre mim?") is False
    assert Agent._user_asked_to_read_file("") is False


def test_extract_file_path():
    """Agent._extract_file_path extrai path de arquivo da mensagem de forma segura."""
    from workspace.core.agent import Agent

    assert Agent._extract_file_path("Leia o conteúdo do arquivo MEMORY.md e resuma.") == "MEMORY.md"
    assert Agent._extract_file_path("arquivo docs/notes.md") == "docs/notes.md"
    assert Agent._extract_file_path("leia README.txt por favor") == "README.txt"
    assert Agent._extract_file_path("nada aqui") is None
    assert Agent._extract_file_path("path com ../etc/passwd") is None
    assert Agent._extract_file_path("/absolute/path.md") is None


def test_extract_markdown_headings():
    """Agent._extract_markdown_headings extrai ## e ### do markdown."""
    from workspace.core.agent import Agent

    text = """# Titulo H1 (ignorado)
## Informações Essenciais
### Identidade do Projeto
## Arquitetura do Sistema
### Componentes
foo bar
## Decisões
"""
    out = Agent._extract_markdown_headings(text)
    assert "## Informações Essenciais" in out
    assert "### Identidade do Projeto" in out
    assert "## Arquitetura do Sistema" in out
    assert "## Decisões" in out
    assert "foo bar" not in out
    assert "# Titulo H1" not in out
