"""Memory Module - Camada 2: Memória Estruturada

Armazenamento estruturado de fatos, decisões e resumos.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json


class MemoryManager:
    """Gerenciador de memória estruturada (Camada 2)"""

    def __init__(self, memory_dir: Path = None):
        if memory_dir is None:
            from config import config
            memory_dir = config.WORKSPACE_DIR / "memory"
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Arquivos
        self.facts_file = self.memory_dir / "facts.md"
        self.decisions_file = self.memory_dir / "decisions.md"
        self.patterns_file = self.memory_dir / "patterns.md"
        self.feedback_file = self.memory_dir / "feedback.md"

        # Garantir arquivos existam
        self._init_files()

    def _init_files(self):
        """Inicializa arquivos se não existirem"""
        for file_path in [self.facts_file, self.decisions_file,
                         self.patterns_file, self.facts_file]:
            if not file_path.exists():
                file_path.write_text(f"# {file_path.name}\n\n", encoding='utf-8')

    def add_fact(self, content: str, source: str = None, tags: List[str] = None):
        """Adiciona um fato à memória"""
        timestamp = datetime.utcnow().isoformat()
        tags_str = f" [{', '.join(tags)}]" if tags else ""

        entry = f"\n## {timestamp}{tags_str}\n{content}\n"
        if source:
            entry += f"_Fonte: {source}_\n"

        with open(self.facts_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def add_decision(self, decision: str, context: str, reasoning: str):
        """Registra uma decisão importante"""
        timestamp = datetime.utcnow().isoformat()

        entry = f"""\n## {timestamp}

**Decisão:** {decision}

**Contexto:** {context}

**Raciocínio:** {reasoning}

---
"""
        with open(self.decisions_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def get_recent_facts(self, limit: int = 10) -> List[str]:
        """Retorna fatos recentes"""
        if not self.facts_file.exists():
            return []

        content = self.facts_file.read_text(encoding='utf-8')
        facts = content.split('\n## ')[1:]  # Skip header
        return facts[:limit]


__all__ = ["MemoryManager"]
