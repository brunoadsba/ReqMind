"""Tool Registry - Sistema de registro e execução de ferramentas"""
from typing import Dict, Callable, Any
import json
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
    
    def register(self, name: str, function: Callable, schema: Dict):
        self.tools[name] = {"function": function, "schema": schema}
        logger.info("tool_registrada name=%s", name)
    
    def get_schemas(self) -> list:
        return [tool["schema"] for tool in self.tools.values()]
    
    async def execute(self, name: str, args: Dict) -> Any:
        if name not in self.tools:
            raise ValueError(f"Ferramenta '{name}' não encontrada")
        
        try:
            result = await self.tools[name]["function"](**args)
            logger.info("tool_executada name=%s", name)
            return result
        except Exception as e:
            logger.error("erro_ao_executar_tool name=%s error=%s", name, e)
            return {"success": False, "error": str(e)}
    
    def list_tools(self) -> list:
        return list(self.tools.keys())
