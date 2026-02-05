#!/usr/bin/env python3
"""heartbeat.py - Atualiza CURRENT_STATE.md periodicamente Autor: Gemini CLI-Cursor Mode Data: 2026-02-04 Versao: 1.0.0 """

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys


class StateHeartbeat:
    """Atualiza CURRENT_STATE.md com metricas de execucao"""

    def __init__(self, agent_dir: Path = None):
        if agent_dir is None:
            agent_dir = Path(__file__).parent.parent
        self.agent_dir = Path(agent_dir).resolve()
        self.workspace_dir = self.agent_dir.parent
        self.state_path = self.agent_dir / "CURRENT_STATE.md"

    def update(self, force_summary: bool = False):
        """Atualiza CURRENT_STATE.md baseado em execucoes recentes"""
        current_state = self._load_current_state()
        new_data = {}

        # 1. Atualiza timestamp
        new_data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # 2. Analisa execucoes recentes
        recent_runs = self._get_recent_runs(hours=24)
        if recent_runs:
            new_data['last_run'] = recent_runs[0]['timestamp']
            new_data['run_count_24h'] = len(recent_runs)

            # Detecta padroes de erro
            error_runs = [r for r in recent_runs if r.get('status') == 'error']
            if len(error_runs) > 3:
                new_data['alert'] = f"Alta taxa de erro: {len(error_runs)}/24h"
            else:
                new_data['alert'] = "Nenhum"

        # 3. Estimativa de uso de contexto
        new_data['context_usage'] = self._estimate_context_usage()

        # 4. Merge e salva
        updated_state = self._merge_state(current_state, new_data)
        self._save_state(updated_state)
        print(f"[heartbeat] Estado atualizado: {new_data['timestamp']}")

    def _load_current_state(self) -> Dict:
        """Parse CURRENT_STATE.md em dict estruturado"""
        if not self.state_path.exists():
            return {}

        content = self.state_path.read_text(encoding='utf-8')
        state = {'raw_sections': {}}

        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    state['raw_sections'][current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            state['raw_sections'][current_section] = '\n'.join(current_content)

        return state

    def _get_recent_runs(self, hours: int = 24) -> List[Dict]:
        """Lista runs dos ultimos N horas"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        runs = []

        runs_dir = self.workspace_dir / "runs"
        if not runs_dir.exists():
            return runs

        for run_dir in sorted(runs_dir.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue

            try:
                ts_str = run_dir.name[:19]
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00').replace('+00:00', ''))
            except:
                continue

            if ts < cutoff:
                break

            metrics_file = run_dir / "metrics.json"
            metrics = json.loads(metrics_file.read_text()) if metrics_file.exists() else {}

            runs.append({
                'dir': str(run_dir),
                'timestamp': ts.isoformat(),
                'status': metrics.get('status', 'unknown')
            })

        return runs

    def _estimate_context_usage(self) -> Dict:
        """Estima tokens no contexto atual"""
        context_pack = self.agent_dir / "CONTEXT_PACK.md"
        if not context_pack.exists():
            return {'tokens': 0, 'percentage': 0, 'status': 'not_found'}

        content = context_pack.read_text(encoding='utf-8')
        tokens = len(content) // 4
        percentage = min(100, (tokens / 128000) * 100)

        return {
            'tokens': tokens,
            'percentage': round(percentage, 1),
            'status': 'ok' if percentage < 50 else 'warning' if percentage < 80 else 'critical'
        }

    def _merge_state(self, old: Dict, new: Dict) -> str:
        """Merge dados novos com estado existente, formatando como markdown"""
        sections = old.get('raw_sections', {})

        context_task = sections.get('Contexto Ativo', '- Nenhuma tarefa ativa').strip()

        meta = f"""- Timestamp: {new['timestamp']}
- Versao: {old.get('version', 0) + 1}"""

        output = f"""# CURRENT_STATE.md - Estado Atual do Agente

## Metadados
{meta}

## Contexto Ativo

### Tarefa em Andamento
{context_task}

### Ultimas Execucoes (24h)
- Total: {new.get('run_count_24h', 0)} runs
- Ultimo: {new.get('last_run', 'N/A')}
- Alertas: {new.get('alert', 'Nenhum')}

## Contexto de Longo Prazo
- Versao do agente: 2.0.0
- Modelo padrao: llama-3.3-70b-versatile
- Ferramentas registradas: 15

## Metricas de Contexto
- Tokens estimados: {new.get('context_usage', {}).get('tokens', 'N/A')}
- Uso de contexto: {new.get('context_usage', {}).get('percentage', 'N/A')}%
- Status: {new.get('context_usage', {}).get('status', 'unknown')}
"""
        return output

    def _save_state(self, content: str):
        """Salva com backup do anterior"""
        if self.state_path.exists():
            backup = self.state_path.with_suffix('.md.bak')
            backup.write_text(self.state_path.read_text(encoding='utf-8'), encoding='utf-8')

        self.state_path.write_text(content, encoding='utf-8')


def main():
    if len(sys.argv) > 1:
        agent_dir = Path(sys.argv[1])
    else:
        agent_dir = Path(__file__).parent.parent

    hb = StateHeartbeat(agent_dir)
    hb.update(force_summary='--force' in sys.argv)


if __name__ == "__main__":
    main()