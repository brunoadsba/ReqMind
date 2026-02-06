#!/usr/bin/env python3
"""
Teste Abrangente das Funcionalidades do Bot via Terminal.
Requer PYTHONPATH=src (ou path do projeto no path). Ex.: PYTHONPATH=src pytest tests/test_bot_completo.py
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Usa src do projeto onde este teste está (evita path fixo de outro diretório)
_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
elif str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from workspace.tools.web_search import web_search
from workspace.tools.rag_tools import rag_search, save_memory
from workspace.tools.code_tools import search_code, git_status, git_diff
from workspace.tools.filesystem import read_file, write_file, list_directory
from workspace.core.tools import ToolRegistry

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN} {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")


async def test_web_search():
    print_header("1. WEB SEARCH - Busca na Web (DuckDuckGo)")
    print(f"{YELLOW}Buscando 'Python 3.12 features'...{RESET}")

    result = await web_search("Python 3.12 features", max_results=3)

    if result.get("success"):
        results = result.get("results", [])
        print(f"{GREEN}✅ Web Search funcionando!{RESET}")
        print(f"   Resultados: {len(results)}")
        for i, item in enumerate(results[:2], 1):
            print(f"   {i}. {item.get('title', 'N/A')[:60]}...")
        return True
    else:
        error = result.get("error", "")
        if "No module" in str(error) or "not found" in str(error).lower():
            print(f"{YELLOW}⚠️  Web Search requer script externo em ~/.clawdbot/{RESET}")
        else:
            print(f"{RED}❌ Falha: {error}{RESET}")
        return False


async def test_rag_search():
    print_header("2. RAG SEARCH - Busca na Memória Pessoal")
    print(f"{YELLOW}Buscando 'projeto' na memória...{RESET}")

    result = await rag_search("projeto")

    if result.get("success"):
        print(f"{GREEN}✅ RAG Search funcionando!{RESET}")
        print(f"   Resultado: {str(result.get('results', 'N/A'))[:100]}...")
        return True
    else:
        error = result.get("error", "")
        if "No module" in str(error) or "not found" in str(error).lower():
            print(f"{YELLOW}⚠️  RAG Search requer script externo em ~/.clawdbot/{RESET}")
        else:
            print(f"{RED}❌ Falha: {error}{RESET}")
        return False


async def test_save_memory():
    print_header("3. SAVE MEMORY - Salvar na Memória")
    print(f"{YELLOW}Salvando informação de teste...{RESET}")

    test_content = f"Teste automatizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    result = await save_memory(test_content, category="test")

    if result.get("success"):
        print(f"{GREEN}✅ Save Memory funcionando!{RESET}")
        print(f"   Mensagem: {result.get('message', 'N/A')}")
        return True
    else:
        error = result.get("error", "")
        if "No module" in str(error) or "not found" in str(error).lower():
            print(
                f"{YELLOW}⚠️  Save Memory requer script externo em ~/.clawdbot/{RESET}"
            )
        else:
            print(f"{RED}❌ Falha: {error}{RESET}")
        return False


async def test_search_code():
    print_header("4. SEARCH CODE - Busca em Arquivos de Código")
    print(f"{YELLOW}Buscando 'async def' em arquivos Python...{RESET}")

    result = await search_code(
        "async def",
        path=str(_repo_root),
        extensions=[".py"],
    )

    if result.get("success"):
        print(f"{GREEN}✅ Search Code funcionando!{RESET}")
        print(f"   Matches encontrados: {result.get('matches', 0)}")
        return True
    else:
        print(f"{RED}❌ Falha: {result.get('error', 'Erro desconhecido')}{RESET}")
        return False


async def test_filesystem():
    print_header("5. FILESYSTEM - Ler, Escrever e Listar")

    test_file = "/tmp/test_bot_completo.txt"
    test_content = f"Teste de funcionalidades do bot\nData: {datetime.now().isoformat()}\nConteúdo de teste para verificar operações de arquivo."

    print(f"{YELLOW}Testando escrita...{RESET}")
    write_result = await write_file(test_file, test_content)
    if not write_result.get("success"):
        print(f"{RED}❌ Escrita falhou: {write_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Escrita funcionando!{RESET}")

    print(f"{YELLOW}Testando leitura...{RESET}")
    read_result = await read_file(test_file)
    if not read_result.get("success"):
        print(f"{RED}❌ Leitura falhou: {read_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Leitura funcionando!{RESET}")
    content = read_result.get("content", "")
    print(f"   Conteúdo ({len(content)} chars): {content[:60]}...")

    print(f"{YELLOW}Testando listagem...{RESET}")
    list_result = await list_directory("/tmp")
    if not list_result.get("success"):
        print(f"{RED}❌ Listagem falhou: {list_result.get('error')}{RESET}")
        return False
    print(f"{GREEN}✅ Listagem funcionando!{RESET}")
    files = list_result.get("files", [])
    dirs = list_result.get("directories", [])
    print(f"   Encontrado: {len(files)} arquivos, {len(dirs)} diretórios")

    if os.path.exists(test_file):
        os.unlink(test_file)

    return True


async def test_git():
    print_header("6. GIT - Status e Diff do Repositório")

    print(f"{YELLOW}Testando git status...{RESET}")
    status_result = await git_status(str(_repo_root))
    if status_result.get("success"):
        print(f"{GREEN}✅ Git Status funcionando!{RESET}")
        status = status_result.get("status", "")
        lines = status.split("\n")[:3]
        for line in lines:
            if line.strip():
                print(f"   {line}")
    else:
        print(f"{RED}❌ Git Status falhou: {status_result.get('error')}{RESET}")

    print(f"{YELLOW}Testando git diff...{RESET}")
    diff_result = await git_diff(str(_repo_root))
    if diff_result.get("success"):
        print(f"{GREEN}✅ Git Diff funcionando!{RESET}")
        diff = diff_result.get("diff", "")
        if diff:
            print(f"   Há alterações não commitadas ({len(diff)} chars)")
        else:
            print(f"   Nenhuma alteração não commitada")
    else:
        print(f"{RED}❌ Git Diff falhou: {diff_result.get('error')}{RESET}")

    return status_result.get("success") or diff_result.get("success")


async def test_tool_registry():
    print_header("7. TOOL REGISTRY - Sistema de Ferramentas")
    print(f"{YELLOW}Registrando ferramentas...{RESET}")

    registry = ToolRegistry()

    from workspace.tools.filesystem import (
        READ_FILE_SCHEMA,
        WRITE_FILE_SCHEMA,
        LIST_DIRECTORY_SCHEMA,
    )
    from workspace.tools.code_tools import SEARCH_CODE_SCHEMA, GIT_STATUS_SCHEMA
    from workspace.tools.web_search import WEB_SEARCH_SCHEMA
    from workspace.tools.rag_tools import RAG_SEARCH_SCHEMA, SAVE_MEMORY_SCHEMA

    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("write_file", write_file, WRITE_FILE_SCHEMA)
    registry.register("list_directory", list_directory, LIST_DIRECTORY_SCHEMA)
    registry.register("search_code", search_code, SEARCH_CODE_SCHEMA)
    registry.register("git_status", git_status, GIT_STATUS_SCHEMA)
    registry.register("web_search", web_search, WEB_SEARCH_SCHEMA)
    registry.register("rag_search", rag_search, RAG_SEARCH_SCHEMA)
    registry.register("save_memory", save_memory, SAVE_MEMORY_SCHEMA)

    tools = registry.list_tools()
    print(f"{GREEN}✅ Tool Registry funcionando!{RESET}")
    print(f"   Total de ferramentas registradas: {len(tools)}")
    print(f"   Ferramentas: {', '.join(sorted(tools))}")

    print(f"{YELLOW}Testando execução via registry...{RESET}")
    test_file = "/tmp/test_registry.txt"
    exec_result = await registry.execute(
        "write_file", {"path": test_file, "content": "Teste via registry"}
    )
    if exec_result.get("success"):
        print(f"{GREEN}✅ Execução via registry funcionando!{RESET}")
        if os.path.exists(test_file):
            os.unlink(test_file)
    else:
        print(f"{RED}❌ Execução via registry falhou{RESET}")

    schemas = registry.get_schemas()
    print(f"   Schemas disponíveis: {len(schemas)}")

    return len(tools) >= 8


async def run_all_tests():
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(
        f"{BOLD}{BLUE}  🤖 TESTE COMPLETO DAS FUNCIONALIDADES DO ASSISTENTE DIGITAL{RESET}"
    )
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"\n{CYAN}Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{RESET}")
    print(f"{CYAN}Diretório: {_repo_root}{RESET}\n")

    tests = [
        ("1. Web Search (DuckDuckGo)", test_web_search),
        ("2. RAG Search (Memória)", test_rag_search),
        ("3. Save Memory", test_save_memory),
        ("4. Search Code", test_search_code),
        ("5. Filesystem (R/W/List)", test_filesystem),
        ("6. Git (Status/Diff)", test_git),
        ("7. Tool Registry", test_tool_registry),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n{RED}❌ Erro inesperado em {name}: {e}{RESET}")
            results.append((name, False))

    # Resumo final
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}  📊 RESUMO FINAL DOS TESTES{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = f"{GREEN}✅ PASSOU{RESET}" if success else f"{RED}❌ FALHOU{RESET}"
        print(f"{status} - {name}")

    print(f"\n{BOLD}{'─' * 70}{RESET}")
    percentage = (passed / total) * 100
    print(f"{BOLD}Total: {passed}/{total} testes passaram ({percentage:.0f}%){RESET}")

    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 TODOS OS TESTES PASSARAM!{RESET}")
    elif passed >= total * 0.7:
        print(f"\n{YELLOW}{BOLD}⚠️  MAIORIA DOS TESTES PASSOU (>= 70%){RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ VÁRIOS TESTES FALHARAM (< 70%){RESET}")

    print(
        f"\n{CYAN}Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{RESET}\n"
    )

    return passed, total


if __name__ == "__main__":
    try:
        passed, total = asyncio.run(run_all_tests())
        sys.exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Teste interrompido pelo usuário{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Erro fatal: {e}{RESET}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
