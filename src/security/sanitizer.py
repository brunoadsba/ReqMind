"""Sanitização de comandos e inputs"""
import re
import subprocess
from pathlib import Path
from typing import Tuple

def sanitize_youtube_url(url: str) -> Tuple[bool, str]:
    """Valida e sanitiza URL do YouTube"""
    # Padrão estrito para URLs do YouTube
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})(\&.*)?$'
    match = re.match(pattern, url)
    
    if not match:
        return False, "URL do YouTube inválida"
    
    video_id = match.group(3)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    return True, clean_url

def sanitize_filename(filename: str) -> str:
    """Remove caracteres perigosos de nomes de arquivo"""
    # Remove tudo exceto alfanuméricos, underscore, hífen e ponto
    safe = re.sub(r'[^\w\-.]', '_', filename)
    # Remove múltiplos pontos (path traversal)
    safe = re.sub(r'\.{2,}', '.', safe)
    # Limita tamanho
    return safe[:200]

def validate_path(path: str, allowed_bases: list) -> Tuple[bool, str]:
    """Valida se path está dentro de diretórios permitidos"""
    try:
        # Resolve path absoluto
        real_path = Path(path).expanduser().resolve()
        
        # Verifica se está dentro de algum diretório permitido
        for base in allowed_bases:
            base_path = Path(base).resolve()
            try:
                real_path.relative_to(base_path)
                return True, str(real_path)
            except ValueError:
                continue
        
        return False, "Path fora de diretórios permitidos"
    
    except Exception as e:
        return False, f"Path inválido: {e}"

def safe_subprocess(cmd: list, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
    """Executa subprocess com proteções"""
    # Valida que não há shell injection
    dangerous_chars = [';', '|', '&', '$', '`', '\n', '>', '<']
    
    for arg in cmd:
        arg_str = str(arg)
        for char in dangerous_chars:
            if char in arg_str:
                raise ValueError(f"Caractere perigoso detectado em: {arg_str}")
    
    # Força shell=False e adiciona timeout
    kwargs['shell'] = False
    kwargs['timeout'] = timeout
    kwargs.setdefault('capture_output', True)
    
    return subprocess.run(cmd, **kwargs)
