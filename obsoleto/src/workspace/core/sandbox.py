"""
LEGADO: Sandbox - Execução segura de código

⚠️ ATENÇÃO: Este módulo não é mais usado no bot.
O código foi movido para o diretório obsoleto apenas para referência histórica.

Para executar código Python de forma segura, considere usar:
- SafeSubprocessExecutor (src/security/executor.py)
- Ou implementar sandbox com Docker se necessário no futuro
"""
import docker
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


class CodeSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image = "python:3.11-slim"
        self.timeout = 30
        self.memory_limit = "128m"

    def _is_dangerous(self, code: str) -> bool:
        dangerous = [
            "import os",
            "import subprocess",
            "import sys",
            "__import__",
            "eval(",
            "exec(",
            "compile(",
            "open(",
            "file(",
        ]
        return any(d in code.lower() for d in dangerous)

    async def execute_python(self, code: str) -> dict:
        if self._is_dangerous(code):
            return {"success": False, "error": "Código contém operações proibidas"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            output = self.client.containers.run(
                self.image,
                f"python /code/{os.path.basename(temp_file)}",
                volumes={os.path.dirname(temp_file): {"bind": "/code", "mode": "ro"}},
                working_dir="/code",
                mem_limit=self.memory_limit,
                network_disabled=True,
                remove=True,
                timeout=self.timeout,
            )

            logger.info("Código executado com sucesso")
            return {"success": True, "output": output.decode("utf-8")}

        except docker.errors.ContainerError as e:
            logger.error(f"Erro no container: {e}")
            return {"success": False, "error": e.stderr.decode("utf-8")}

        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return {"success": False, "error": str(e)}

        finally:
            os.unlink(temp_file)


async def execute_code(code: str, language: str = "python") -> dict:
    if language != "python":
        return {"success": False, "error": f"Linguagem '{language}' não suportada"}

    sandbox = CodeSandbox()
    return await sandbox.execute_python(code)


EXECUTE_CODE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "execute_code",
        "description": "Executa código Python em ambiente seguro",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Código Python a executar",
                },
                "language": {
                    "type": "string",
                    "description": "Linguagem (padrão: python)",
                    "default": "python",
                },
            },
            "required": ["code"],
        },
    },
}

