#!/usr/bin/env python3
"""
Teste Simplificado das Funcionalidades do Bot
Testa ferramentas sem dependências problemáticas de pandas/ctypes
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, "/home/brunoadsba/Assistente-Digital/assistente")

from workspace.tools.filesystem import read_file, write_file, list_directory
from workspace.tools.code_tools import search_code, git_status, git_diff
from workspace.core.tools import ToolRegistry

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


async def test_filesystem():
    print(f"\n{BOLD}5. FILESYSTEM - Operações de Arquivo{RESET}")

    test_file = "/tmp/test_bot_terminal.txt"
    test_content = (
        f"Teste de funcionalidades do bot\nData: {datetime.now().isoformat()}"
    )

    write_result = await write_file(test_file, test_content)
    if not write_result.get("success"):
        print(f"{RED}❌ Falha na escrita: {write_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Escrita funcionando!{RESET}")

    read_result = await read_file(test_file)
    if not read_result.get("success"):
        print(f"{RED}❌ Falha na leitura: {read_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Leitura funcionando!{RESET}")
    print(f"   Conteúdo: {read_result.get('content', 'N/A')[:50]}...")

    list_result = await list_directory("/tmp")
    if not list_result.get("success"):
        print(f"{RED}❌ Falha na listagem: {list_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Listagem funcionando!{RESET}")
    print(f"   Arquivos em /tmp: {len(list_result.get('files', []))}")

    if os.path.exists(test_file):
        os.unlink(test_file)

    return True


async def test_git():
    print(f"\n{BOLD}6. GIT - Status e Diff{RESET}")

    status_result = await git_status("/home/brunoadsba/Assistente-Digital/assistente")
    if status_result.get("success"):
        print(f"{GREEN}✅ Git status funcionando!{RESET}")
        print(f"   Status: {status_result.get('status', 'N/A')[:80]}...")
    else:
        print(f"{RED}❌ Git status falhou: {status_result.get('error')}{RESET}")

    diff_result = await git_diff("/home/brunoadsba/Assistente-Digital/assistente")
    if diff_result.get("success"):
        print(f"{GREEN}✅ Git diff funcionando!{RESET}")
    else:
        print(f"{RED}❌ Git diff falhou: {diff_result.get('error')}{RESET}")

    return status_result.get("success") or diff_result.get("success")


async def test_search_code():
    print(f"\n{BOLD}4. SEARCH CODE - Busca em Código{RESET}")

    result = await search_code(
        "async def",
        path="/home/brunoadsba/Assistente-Digital/assistente",
        extensions=[".py"],
    )

    if result.get("success"):
        print(f"{GREEN}✅ Busca em código funcionando!{RESET}")
        matches = result.get("matches", 0)
        print(f"   Matches encontrados: {matches}")
        return True
    else:
        print(f"{RED}❌ Falha: {result.get('error', 'Erro desconhecido')}{RESET}")
        return False


async def test_tool_registry():
    print(f"\n{BOLD}12. TOOL REGISTRY - Sistema de Ferramentas{RESET}")

    registry = ToolRegistry()

    from workspace.tools.filesystem import READ_FILE_SCHEMA, WRITE_FILE_SCHEMA

    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("write_file", write_file, WRITE_FILE_SCHEMA)

    tools = registry.list_tools()
    print(f"{GREEN}✅ Tool Registry funcionando!{RESET}")
    print(f"   Ferramentas registradas: {len(tools)}")
    print(f"   Lista: {', '.join(tools)}")

    return len(tools) == 2


async def run_tests():
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  🧪 TESTE SIMPLIFICADO DO BOT{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")
    print(f"{YELLOW}Nota: Testes de Web Search, RAG, Weather, News, Charts e{RESET}")
    print(f"{YELLOW}Image Generation requerem dependências adicionais.{RESET}\n")

    tests = [
        ("Search Code", test_search_code),
        ("Filesystem", test_filesystem),
        ("Git", test_git),
        ("Tool Registry", test_tool_registry),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"{RED}Erro inesperado em {name}: {e}{RESET}")
            results.append((name, False))

    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  📊 RESUMO{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = f"{GREEN}✅ PASSOU{RESET}" if success else f"{RED}❌ FALHOU{RESET}"
        print(f"{status} - {name}")

    print(
        f"\n{BOLD}Total: {passed}/{total} testes passaram ({(passed / total) * 100:.0f}%){RESET}\n"
    )

    return passed, total


if __name__ == "__main__":
    try:
        passed, total = asyncio.run(run_tests())
        sys.exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Teste interrompido{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Erro fatal: {e}{RESET}")
        sys.exit(1)
