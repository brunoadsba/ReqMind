"""Executor de subprocessos assíncrono e seguro"""

import asyncio
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SafeSubprocessExecutor:
    """Executa comandos shell de forma assíncrona e segura"""

    ALLOWED_COMMANDS = {"ffmpeg", "ffprobe", "tesseract", "python", "python3", "yt-dlp"}
    TIMEOUT_SECONDS = 30

    @classmethod
    async def run(
        cls,
        cmd: List[str],
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
    ) -> Tuple[bool, str, str]:
        """
        Executa comando de forma segura

        Args:
            cmd: Lista de argumentos do comando
            timeout: Timeout em segundos (padrão: TIMEOUT_SECONDS)
            cwd: Diretório de trabalho
            env: Variáveis de ambiente adicionais

        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        if not cmd or not isinstance(cmd, list):
            return False, "", "Comando inválido: deve ser uma lista não vazia"

        command = cmd[0]
        if command not in cls.ALLOWED_COMMANDS:
            return False, "", f"Comando não permitido: {command}"

        # Valida argumentos para prevenir injection
        dangerous_patterns = [";", "&&", "||", "`", "$", "|", ">", "<", "&"]
        for i, arg in enumerate(cmd[1:], start=1):
            arg_str = str(arg)
            for pattern in dangerous_patterns:
                if pattern in arg_str:
                    logger.warning(
                        f"Padrão perigoso detectado no argumento {i}: {pattern}"
                    )
                    return (
                        False,
                        "",
                        f"Argumento suspeito detectado no argumento {i}: {arg_str[:50]}",
                    )

        # Prepara o timeout
        exec_timeout = timeout or cls.TIMEOUT_SECONDS

        try:
            logger.debug(f"Executando comando: {' '.join(cmd)}")

            # Cria subprocesso de forma assíncrona (sem shell)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            # Aguarda com timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=exec_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Timeout após {exec_timeout}s no comando: {command}")
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                return False, "", f"Timeout na execução ({exec_timeout}s)"

            # Decodifica saída
            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""

            # Verifica código de retorno
            # FFmpeg retorna 8 em --version (como documentado)
            if command == "ffmpeg":
                success = proc.returncode == 0 or proc.returncode == 8
            else:
                success = proc.returncode == 0

            if success:
                logger.debug(f"Comando executado com sucesso: {command}")
            else:
                logger.warning(
                    f"Comando falhou com código {proc.returncode}: {command}"
                )

            return success, stdout_str, stderr_str

        except asyncio.TimeoutError:
            return False, "", "Timeout na execução"
        except Exception as e:
            logger.error(f"Erro ao executar comando {command}: {e}")
            return False, "", str(e)

    @classmethod
    def validate_command(cls, cmd: List[str]) -> Tuple[bool, str]:
        """Valida se um comando pode ser executado (sem executar)"""
        if not cmd or not isinstance(cmd, list):
            return False, "Comando inválido"

        command = cmd[0]
        if command not in cls.ALLOWED_COMMANDS:
            return False, f"Comando não permitido: {command}"

        dangerous_patterns = [";", "&&", "||", "`", "$", "|", ">", "<", "&"]
        for arg in cmd[1:]:
            arg_str = str(arg)
            for pattern in dangerous_patterns:
                if pattern in arg_str:
                    return False, f"Argumento suspeito: {arg_str[:50]}"

        return True, "OK"


# Função de conveniência
async def safe_run(
    cmd: List[str], timeout: Optional[int] = None
) -> Tuple[bool, str, str]:
    """Executa comando de forma segura (função de conveniência)"""
    return await SafeSubprocessExecutor.run(cmd, timeout)
