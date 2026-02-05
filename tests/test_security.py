"""Testes unitários dos módulos de segurança"""
import pytest
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
if _src.exists():
    sys.path.insert(0, str(_src))
else:
    sys.path.insert(0, str(_repo_root))


def test_sanitize_youtube_url_valid():
    """URL do YouTube válida é aceita e normalizada"""
    from security.sanitizer import sanitize_youtube_url

    ok, url = sanitize_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert ok is True
    assert "youtube.com" in url
    assert "dQw4w9WgXcQ" in url


def test_sanitize_youtube_url_invalid():
    """URL inválida ou com injeção é rejeitada"""
    from security.sanitizer import sanitize_youtube_url

    ok, _ = sanitize_youtube_url("https://evil.com; rm -rf /")
    assert ok is False

    ok, _ = sanitize_youtube_url("not-a-url")
    assert ok is False


def test_validate_path_allowed():
    """Path dentro de base permitido é aceito"""
    from security.sanitizer import validate_path
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        ok, resolved = validate_path(d, [d])
        assert ok is True
        assert resolved


def test_validate_path_traversal_rejected():
    """Path traversal fora da base é rejeitado"""
    from security.sanitizer import validate_path
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        ok, msg = validate_path("../../etc/passwd", [d])
        assert ok is False
        assert "fora" in msg or "inválido" in msg.lower()


def test_rate_limiter_allows_under_limit():
    """Rate limiter permite requisições abaixo do limite"""
    from security.rate_limiter import RateLimiter

    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed(99991) is True
    assert limiter.is_allowed(99991) is True
    assert limiter.is_allowed(99991) is False


@pytest.mark.asyncio
async def test_safe_subprocess_executor_allowed_command():
    """Comando permitido é executado"""
    from security.executor import SafeSubprocessExecutor

    success, stdout, stderr = await SafeSubprocessExecutor.run(
        ["python3", "-c", "print('ok')"],
        timeout=5,
    )
    assert success is True
    assert "ok" in stdout


@pytest.mark.asyncio
async def test_safe_subprocess_executor_rejects_forbidden_command():
    """Comando fora da whitelist é rejeitado"""
    from security.executor import SafeSubprocessExecutor

    success, _, err = await SafeSubprocessExecutor.run(["curl", "https://example.com"], timeout=5)
    assert success is False
    assert "não permitido" in err or "permitido" in err


@pytest.mark.asyncio
async def test_safe_subprocess_executor_rejects_dangerous_args():
    """Argumentos com caracteres perigosos são rejeitados"""
    from security.executor import SafeSubprocessExecutor

    success, _, err = await SafeSubprocessExecutor.run(
        ["ffmpeg", "-i", "file; rm -rf /"],
        timeout=5,
    )
    assert success is False
