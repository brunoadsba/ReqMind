"""Runs Module - Camada 1: Execucoes Imutaveis

Cada run é um diretório em runs/YYYY-MM-DDTHHMMSSZ_run_XXX/
com estrutura de arquivos auditável.
"""

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class RunMetrics:
    """Métricas de uma execução"""
    timestamp: str
    duration_ms: float
    tokens_input: int = 0
    tokens_output: int = 0
    iterations: int = 0
    tools_used: int = 0
    status: str = "unknown"  # success, error, partial
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunMetrics":
        return cls(**data)


@dataclass
class RunData:
    """Dados completos de uma execução"""
    run_id: str
    input_data: Dict[str, Any]
    actions: list
    output_text: str
    metrics: RunMetrics


class RunManager:
    """Gerenciador de execuções em runs/"""

    def __init__(self, runs_dir: Path = None):
        if runs_dir is None:
            from config import config
            runs_dir = config.WORKSPACE_DIR / "runs"
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self._run_counter = 0

    def create_run(self, user_message: str, user_id: Optional[int] = None,
                   image_url: Optional[str] = None) -> Path:
        """Cria um novo diretório de run"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
        self._run_counter += 1
        run_id = f"{timestamp}_run_{self._run_counter:03d}"

        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Salva input.json
        input_data = {
            "timestamp": timestamp,
            "user_id": user_id,
            "message": user_message,
            "image_url": image_url,
            "run_id": run_id
        }
        (run_dir / "input.json").write_text(
            json.dumps(input_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # Cria actions.log vazio
        (run_dir / "actions.log").write_text(
            f"# Actions Log - {run_id}\n# Timestamp: {timestamp}\n\n",
            encoding='utf-8'
        )

        return run_dir

    def log_action(self, run_dir: Path, tool_name: str, tool_args: Dict,
                   result: Dict, iteration: int):
        """Loga uma ação no actions.log"""
        actions_path = run_dir / "actions.log"

        log_entry = f"""\n## Iteration {iteration}
### Tool: {tool_name}
**Args:**```json
{json.dumps(tool_args, indent=2, ensure_ascii=False)}
```
**Result:**```json
{json.dumps(result, indent=2, ensure_ascii=False)}
```
---
"""
        with open(actions_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def save_output(self, run_dir: Path, output_text: str):
        """Salva o output final"""
        output_path = run_dir / "output.md"
        output_path.write_text(
            f"# Output\n\n{output_text}\n",
            encoding='utf-8'
        )

    def save_metrics(self, run_dir: Path, metrics: RunMetrics):
        """Salva métricas em metrics.json"""
        metrics_path = run_dir / "metrics.json"
        metrics_path.write_text(
            json.dumps(metrics.to_dict(), indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def get_latest_runs(self, limit: int = 10) -> list:
        """Retorna os runs mais recentes"""
        if not self.runs_dir.exists():
            return []

        run_dirs = sorted(
            [d for d in self.runs_dir.iterdir() if d.is_dir()],
            reverse=True
        )
        return run_dirs[:limit]


__all__ = [
    "RunMetrics",
    "RunData",
    "RunManager",
]