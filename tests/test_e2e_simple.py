"""Testes E2E do Moltbot (sem Docker)"""
import pytest
import os
import sys
from pathlib import Path

# Path do projeto: raiz do repo (parent de tests/)
_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
if _src.exists():
    sys.path.insert(0, str(_src))
else:
    sys.path.insert(0, str(_repo_root))

from workspace.core.tools import ToolRegistry
from workspace.storage.sqlite_store import SQLiteStore

@pytest.mark.asyncio
async def test_tool_registry():
    """Testa registro e execução de ferramentas"""
    registry = ToolRegistry()
    
    async def dummy_tool(arg1: str):
        return {"result": arg1.upper()}
    
    schema = {
        "type": "function",
        "function": {
            "name": "dummy_tool",
            "description": "Ferramenta de teste",
            "parameters": {
                "type": "object",
                "properties": {"arg1": {"type": "string"}},
                "required": ["arg1"]
            }
        }
    }
    
    registry.register("dummy_tool", dummy_tool, schema)
    result = await registry.execute("dummy_tool", {"arg1": "hello"})
    
    assert result["result"] == "HELLO"
    assert "dummy_tool" in registry.list_tools()
    print("✅ Tool registry OK")

def test_sqlite_store():
    """Testa persistência SQLite"""
    store = SQLiteStore(db_path="/tmp/test_moltbot.db")
    
    # Adiciona mensagens
    store.add_message("user", "Olá")
    store.add_message("assistant", "Oi!")
    
    # Recupera histórico
    history = store.get_history(limit=10)
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Olá"
    
    # Limpa
    store.clear_history()
    history = store.get_history()
    assert len(history) == 0
    
    # Loga métrica
    store.log_metric("test_event", {"data": "test"})
    
    print("✅ SQLite store OK")
    
    # Cleanup
    if os.path.exists("/tmp/test_moltbot.db"):
        os.unlink("/tmp/test_moltbot.db")

@pytest.mark.asyncio
async def test_filesystem_tools():
    """Testa ferramentas de filesystem (paths dentro de TEMP_DIR permitido)"""
    from workspace.tools.filesystem import read_file, write_file, list_directory
    from config.settings import config

    test_dir = Path(config.TEMP_DIR)
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = str(test_dir / "test_moltbot.txt")
    result = await write_file(test_file, "Teste de conteúdo")
    assert result["success"] is True

    result = await read_file(test_file)
    assert result["success"] is True
    assert result["content"] == "Teste de conteúdo"

    result = await list_directory(str(test_dir))
    assert result["success"] is True
    assert "test_moltbot.txt" in result["files"]

    print("✅ Filesystem tools OK")

    if os.path.exists(test_file):
        os.unlink(test_file)


@pytest.mark.asyncio
async def test_filesystem_path_rejected():
    """Path fora dos diretórios permitidos deve retornar success False"""
    from workspace.tools.filesystem import read_file

    result = await read_file("../../etc/passwd")
    assert result["success"] is False
    assert "error" in result
    print("✅ Filesystem path rejeitado OK")

@pytest.mark.asyncio
async def test_agent_creation():
    """Testa criação do agente com ferramentas registradas"""
    from workspace.core.tools import ToolRegistry
    from workspace.core.agent import Agent

    registry = ToolRegistry()
    # Registra pelo menos uma ferramenta para ter agent válido
    async def dummy_tool():
        return {"success": True}
    schema = {"type": "function", "function": {"name": "dummy_tool", "description": "Test", "parameters": {"type": "object", "properties": {}}}}
    registry.register("dummy_tool", dummy_tool, schema)
    agent = Agent(registry)

    tools = agent.tools.list_tools()
    assert "dummy_tool" in tools
    assert len(tools) >= 1
    print(f"✅ Agente criado com {len(tools)} ferramentas")

@pytest.mark.asyncio
async def test_code_tools():
    """Testa ferramentas de código"""
    from workspace.tools.code_tools import git_status
    
    # Testa git status
    result = await git_status("~/clawd")
    
    # Pode falhar se não for um repo git, mas deve retornar estrutura correta
    assert "success" in result
    
    print("✅ Code tools OK")

if __name__ == "__main__":
    import asyncio
    
    print("\n🧪 Iniciando testes E2E do Moltbot (sem Docker)\n")
    
    # Roda testes
    asyncio.run(test_tool_registry())
    test_sqlite_store()
    asyncio.run(test_filesystem_tools())
    asyncio.run(test_agent_creation())
    asyncio.run(test_code_tools())
    
    print("\n✅ Todos os testes passaram!\n")
    print("⚠️  Nota: Testes de sandbox (Docker) foram pulados devido a problemas de compatibilidade")
    print("   O sandbox funcionará quando o bot estiver rodando em container Docker\n")
