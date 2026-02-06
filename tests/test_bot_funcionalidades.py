#!/usr/bin/env python3
"""
🧪 Teste Completo das Funcionalidades do Bot via Terminal
Testa todas as 10+ ferramentas disponíveis no Assistente Digital
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o caminho do projeto (raiz do repo ou src/)
_repo_root = Path(__file__).resolve().parent.parent
_src = _repo_root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
elif str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Importa as ferramentas
from workspace.tools.web_search import web_search
from workspace.tools.rag_tools import rag_search, save_memory
from workspace.tools.code_tools import search_code, git_status, git_diff
from workspace.tools.filesystem import read_file, write_file, list_directory
from workspace.tools.extra_tools import (
    get_weather,
    get_news,
    create_reminder,
    create_chart,
    generate_image,
)
from workspace.core.tools import ToolRegistry

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE} {text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")


async def test_web_search():
    """Testa busca na web usando DuckDuckGo"""
    print_header("1. WEB SEARCH - DuckDuckGo")
    print_info("Buscando: 'Python 3.12 novidades'...")

    result = await web_search("Python 3.12 novidades", max_results=3)

    if result.get("success"):
        print_success("Busca web funcionando!")
        results = result.get("results", [])
        print(f"   Resultados encontrados: {len(results)}")
        for i, item in enumerate(results[:2], 1):
            print(f"   {i}. {item.get('title', 'N/A')[:50]}...")
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_rag_search():
    """Testa busca na memória pessoal"""
    print_header("2. RAG SEARCH - Busca na Memória")
    print_info("Buscando na memória...")

    result = await rag_search("projeto")

    if result.get("success"):
        print_success("Busca na memória funcionando!")
        print(f"   Resultado: {str(result.get('results', 'N/A'))[:100]}...")
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_save_memory():
    """Testa salvar informação na memória"""
    print_header("3. SAVE MEMORY - Salvar na Memória")
    print_info("Salvando informação de teste...")

    test_content = f"Teste automatizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    result = await save_memory(test_content, category="test")

    if result.get("success"):
        print_success("Salvar na memória funcionando!")
        print(f"   Mensagem: {result.get('message', 'N/A')}")
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_search_code():
    """Testa busca em código"""
    print_header("4. SEARCH CODE - Busca em Código")
    print_info("Buscando 'async def' nos arquivos Python...")

    result = await search_code(
        "async def",
        path=str(_repo_root),
        extensions=[".py"],
    )

    if result.get("success"):
        print_success("Busca em código funcionando!")
        matches = result.get("matches", 0)
        print(f"   Matches encontrados: {matches}")
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_filesystem():
    """Testa operações de arquivo"""
    print_header("5. FILESYSTEM - Operações de Arquivo")

    test_file = "/tmp/test_bot_funcionalidades.txt"
    test_content = (
        f"Teste de funcionalidades do bot\nData: {datetime.now().isoformat()}"
    )

    # Testa write
    print_info("Testando escrita de arquivo...")
    write_result = await write_file(test_file, test_content)
    if not write_result.get("success"):
        print_error(f"Falha na escrita: {write_result.get('error')}")
        return False
    print_success("Escrita funcionando!")

    # Testa read
    print_info("Testando leitura de arquivo...")
    read_result = await read_file(test_file)
    if not read_result.get("success"):
        print_error(f"Falha na leitura: {read_result.get('error')}")
        return False
    print_success("Leitura funcionando!")
    print(f"   Conteúdo lido: {read_result.get('content', 'N/A')[:50]}...")

    # Testa list
    print_info("Testando listagem de diretório...")
    list_result = await list_directory("/tmp")
    if not list_result.get("success"):
        print_error(f"Falha na listagem: {list_result.get('error')}")
        return False
    print_success("Listagem funcionando!")
    print(f"   Arquivos em /tmp: {len(list_result.get('files', []))}")

    # Cleanup
    if os.path.exists(test_file):
        os.unlink(test_file)

    return True


async def test_git():
    """Testa comandos git"""
    print_header("6. GIT - Status e Diff")

    # Testa git status
    print_info("Testando git status...")
    status_result = await git_status(str(_repo_root))
    if status_result.get("success"):
        print_success("Git status funcionando!")
        status_text = status_result.get("status", "")[:100]
        print(f"   Status: {status_text}...")
    else:
        print_error(f"Git status falhou: {status_result.get('error')}")

    # Testa git diff
    print_info("Testando git diff...")
    diff_result = await git_diff(str(_repo_root))
    if diff_result.get("success"):
        print_success("Git diff funcionando!")
        diff_text = diff_result.get("diff", "")[:100]
        print(f"   Diff: {diff_text}...")
    else:
        print_error(f"Git diff falhou: {diff_result.get('error')}")

    return status_result.get("success") or diff_result.get("success")


async def test_weather():
    """Testa obtenção de clima"""
    print_header("7. WEATHER - Clima Atual")
    print_info("Obtendo clima de Ilhéus, BR...")

    result = await get_weather("Ilhéus,BR")

    if result.get("success"):
        print_success("Clima funcionando!")
        weather = result.get("weather", {})
        print(f"   Cidade: {weather.get('cidade', 'N/A')}")
        print(f"   Temperatura: {weather.get('temperatura', 'N/A')}")
        print(f"   Descrição: {weather.get('descricao', 'N/A')}")
        return True
    else:
        error = result.get("error", "Erro desconhecido")
        if "API key" in str(error):
            print_error(f"API key não configurada: {error}")
        else:
            print_error(f"Falha: {error}")
        return False


async def test_news():
    """Testa busca de notícias"""
    print_header("8. NEWS - Últimas Notícias")
    print_info("Buscando notícias sobre 'tecnologia'...")

    result = await get_news("tecnologia", limit=3)

    if result.get("success"):
        print_success("Notícias funcionando!")
        articles = result.get("articles", [])
        print(f"   Notícias encontradas: {len(articles)}")
        for i, article in enumerate(articles[:2], 1):
            print(f"   {i}. {article.get('titulo', 'N/A')[:50]}...")
        return True
    else:
        error = result.get("error", "Erro desconhecido")
        if "API key" in str(error):
            print_error(f"API key não configurada: {error}")
        else:
            print_error(f"Falha: {error}")
        return False


async def test_reminder():
    """Testa criação de lembretes"""
    print_header("9. REMINDER - Criar Lembrete")

    # Cria lembrete para amanhã
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y %H:%M")
    print_info(f"Criando lembrete para: {tomorrow}")

    result = await create_reminder("Teste de funcionalidade do bot", tomorrow)

    if result.get("success"):
        print_success("Lembretes funcionando!")
        print(f"   Mensagem: {result.get('message', 'N/A')}")
        reminder = result.get("reminder", {})
        print(f"   Data: {reminder.get('datetime', 'N/A')}")
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_chart():
    """Testa criação de gráficos"""
    print_header("10. CHART - Criar Gráficos")

    data = {
        "labels": ["Jan", "Fev", "Mar", "Abr", "Mai"],
        "values": [100, 150, 120, 180, 200],
        "title": "Teste de Funcionalidades - Vendas 2024",
    }

    print_info("Criando gráfico de barras...")
    result = await create_chart(data, chart_type="bar")

    if result.get("success"):
        print_success("Gráficos funcionando!")
        image_path = result.get("image_path", "N/A")
        print(f"   Imagem salva em: {image_path}")

        # Verifica se arquivo existe
        if os.path.exists(image_path):
            size = os.path.getsize(image_path)
            print(f"   Tamanho do arquivo: {size} bytes")
            # Cleanup
            os.unlink(image_path)
        return True
    else:
        print_error(f"Falha: {result.get('error', 'Erro desconhecido')}")
        return False


async def test_image_generation():
    """Testa geração de imagens com IA"""
    print_header("11. IMAGE GENERATION - Gerar Imagens com IA")
    print_info("Testando geração de imagem (pode requerer API key)...")

    result = await generate_image("um gato astronauta no espaço, arte digital colorida")

    if result.get("success"):
        print_success("Geração de imagens funcionando!")
        print(f"   URL: {result.get('image_url', 'N/A')[:60]}...")
        return True
    else:
        error = result.get("error", "Erro desconhecido")
        if "API key" in str(error):
            print_error(f"API key não configurada: {error}")
        else:
            print_error(f"Falha: {error}")
        return False


async def test_tool_registry():
    """Testa o registro de ferramentas"""
    print_header("12. TOOL REGISTRY - Sistema de Ferramentas")
    print_info("Testando registro de ferramentas...")

    registry = ToolRegistry()

    # Registra algumas ferramentas
    from workspace.tools.web_search import WEB_SEARCH_SCHEMA
    from workspace.tools.filesystem import READ_FILE_SCHEMA, WRITE_FILE_SCHEMA

    registry.register("web_search", web_search, WEB_SEARCH_SCHEMA)
    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("write_file", write_file, WRITE_FILE_SCHEMA)

    tools = registry.list_tools()
    print_success(f"Tool Registry funcionando!")
    print(f"   Ferramentas registradas: {len(tools)}")
    print(f"   Lista: {', '.join(tools)}")

    return len(tools) == 3


async def run_all_tests():
    """Executa todos os testes"""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  🧪 TESTE DE FUNCIONALIDADES DO ASSISTENTE DIGITAL{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(
        f"{YELLOW}Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{RESET}\n"
    )

    tests = [
        ("Web Search (DuckDuckGo)", test_web_search),
        ("RAG Search (Memória)", test_rag_search),
        ("Save Memory", test_save_memory),
        ("Search Code", test_search_code),
        ("Filesystem (R/W/List)", test_filesystem),
        ("Git (Status/Diff)", test_git),
        ("Weather (Clima)", test_weather),
        ("News (Notícias)", test_news),
        ("Reminder (Lembretes)", test_reminder),
        ("Chart (Gráficos)", test_chart),
        ("Image Generation", test_image_generation),
        ("Tool Registry", test_tool_registry),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Erro inesperado em {name}: {e}")
            results.append((name, False))
        print()  # Linha em branco entre testes

    # Resumo
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  📊 RESUMO DOS TESTES{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = f"{GREEN}✅ PASSOU{RESET}" if success else f"{RED}❌ FALHOU{RESET}"
        print(f"{status} - {name}")

    print(f"\n{BOLD}Total: {passed}/{total} testes passaram{RESET}")
    percentage = (passed / total) * 100 if total > 0 else 0
    print(f"{BOLD}Taxa de sucesso: {percentage:.1f}%{RESET}")

    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 TODOS OS TESTES PASSARAM!{RESET}")
    elif passed >= total * 0.7:
        print(f"\n{YELLOW}{BOLD}⚠️  MAIORIA DOS TESTES PASSOU (>= 70%){RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ VÁRIOS TESTES FALHARAM (< 70%){RESET}")

    print(
        f"\n{YELLOW}Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{RESET}\n"
    )

    return passed, total


if __name__ == "__main__":
    try:
        passed, total = asyncio.run(run_all_tests())
        sys.exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Teste interrompido pelo usuário{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Erro fatal: {e}{RESET}")
        sys.exit(1)
