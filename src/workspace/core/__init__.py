"""Core - Inicialização do agente com todas as ferramentas"""
from .tools import ToolRegistry
from .agent import Agent
from workspace.tools.web_search import web_search, WEB_SEARCH_SCHEMA
from workspace.tools.rag_tools import rag_search, save_memory, RAG_SEARCH_SCHEMA, SAVE_MEMORY_SCHEMA
# Sandbox causa segfault com docker, comentado temporariamente
# from workspace.core.sandbox import execute_code, EXECUTE_CODE_SCHEMA
from workspace.tools.filesystem import read_file, write_file, list_directory, READ_FILE_SCHEMA, WRITE_FILE_SCHEMA, LIST_DIRECTORY_SCHEMA
from workspace.tools.code_tools import search_code, git_status, git_diff, SEARCH_CODE_SCHEMA, GIT_STATUS_SCHEMA, GIT_DIFF_SCHEMA

def create_agent() -> Agent:
    registry = ToolRegistry()
    
    # Web e memória
    registry.register("web_search", web_search, WEB_SEARCH_SCHEMA)
    registry.register("rag_search", rag_search, RAG_SEARCH_SCHEMA)
    registry.register("save_memory", save_memory, SAVE_MEMORY_SCHEMA)
    
    # Código
    # registry.register("execute_code", execute_code, EXECUTE_CODE_SCHEMA)  # Comentado temporariamente
    registry.register("search_code", search_code, SEARCH_CODE_SCHEMA)
    
    # Filesystem
    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("write_file", write_file, WRITE_FILE_SCHEMA)
    registry.register("list_directory", list_directory, LIST_DIRECTORY_SCHEMA)
    
    # Git
    registry.register("git_status", git_status, GIT_STATUS_SCHEMA)
    registry.register("git_diff", git_diff, GIT_DIFF_SCHEMA)
    
    return Agent(registry)
