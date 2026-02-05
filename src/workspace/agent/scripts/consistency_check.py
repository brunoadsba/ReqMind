#!/usr/bin/env python3
"""consistency_check.py - Valida integridade entre as 3 camadas Autor: Gemini CLI-Cursor Mode Data: 2026-02-04 Versao: 1.0.0 """

import hashlib
import json
from pathlib import Path
from typing import Dict, List
import sys


class ConsistencyChecker:
    """Valida integridade da arquitetura de 3 camadas"""

    def __init__(self, agent_dir: Path = None):
        if agent_dir is None:
            agent_dir = Path(__file__).parent.parent
        self.agent_dir = Path(agent_dir).resolve()

    def check(self) -> Dict:
        """Executa bateria de validacoes"""
        results = {
            'layer_1_integrity': self._check_layer_1(),
            'cross_layer_consistency': self._check_cross_layer(),
            'context_pack_freshness': self._check_context_pack(),
            'tests_passed': 0,
            'tests_total': 0,
            'passed': True
        }

        results['tests_total'] = sum(
            r.get('total', 0) for r in [results['layer_1_integrity'], results['cross_layer_consistency']]
        )
        results['tests_passed'] = sum(
            r.get('passed', 0) for r in [results['layer_1_integrity'], results['cross_layer_consistency']]
        )

        results['passed'] = all(
            r.get('ok', False) for r in [results['layer_1_integrity'], results['cross_layer_consistency']]
        )

        return results

    def _check_layer_1(self) -> Dict:
        """Valida arquivos core da camada 1"""
        required = [
            'IDENTITY.md',
            'POLICIES.md',
            'STYLE.md',
            'EXAMPLES.md',
            'RUNBOOK.md',
            'CURRENT_STATE.md'
        ]
        optional = ['CONTEXT_PACK.md', 'META.md', 'CHANGELOG.md']

        missing = [f for f in required if not (self.agent_dir / f).exists()]
        present_optional = [f for f in optional if (self.agent_dir / f).exists()]

        return {
            'ok': len(missing) == 0,
            'type': 'layer_1_integrity',
            'total': len(required) + len(optional),
            'passed': len(required) - len(missing) + len(present_optional),
            'missing_required': missing,
            'present_optional': present_optional,
            'required_total': len(required),
            'required_ok': len(required) - len(missing)
        }

    def _check_cross_layer(self) -> Dict:
        """Verifica se hashes/versoes alinham entre camadas"""
        identity = self.agent_dir / "IDENTITY.md"
        context_pack = self.agent_dir / "CONTEXT_PACK.md"

        if not (identity.exists() and context_pack.exists()):
            return {
                'ok': False,
                'type': 'cross_layer_consistency',
                'total': 1,
                'passed': 0,
                'error': 'Arquivos essenciais ausentes'
            }

        identity_hash = hashlib.md5(identity.read_bytes()).hexdigest()[:8]
        pack_content = context_pack.read_text(encoding='utf-8')

        pack_synced = identity_hash in pack_content

        return {
            'ok': pack_synced,
            'type': 'cross_layer_consistency',
            'total': 1,
            'passed': 1 if pack_synced else 0,
            'identity_hash': identity_hash,
            'context_pack_synced': pack_synced
        }

    def _check_context_pack(self) -> Dict:
        """Verifica se CONTEXT_PACK.md esta atualizado"""
        context_pack = self.agent_dir / "CONTEXT_PACK.md"

        if not context_pack.exists():
            return {
                'ok': False,
                'status': 'missing',
                'message': 'CONTEXT_PACK.md nao encontrado - execute compiler.py'
            }

        content = context_pack.read_text(encoding='utf-8')
        tokens = len(content) // 4

        return {
            'ok': tokens < 128000,
            'status': 'ok' if tokens < 128000 else 'oversized',
            'tokens': tokens,
            'message': f'Context Pack: {tokens} tokens'
        }

    def print_report(self, results: Dict):
        """Imprime relatorio formatado"""
        print("=" * 60)
        print("CONSISTENCY CHECK - Relatorio de Integridade")
        print("=" * 60)

        layer1 = results['layer_1_integrity']
        print(f"\n[Layer 1 - Fonte da Verdade]")
        print(f"  Status: {'OK' if layer1['ok'] else 'FALHA'}")
        print(f"  Arquivos OK: {layer1['required_ok']}/{layer1['required_total']}")
        if layer1.get('missing_required'):
            print(f"  Faltando: {', '.join(layer1['missing_required'])}")

        cross = results['cross_layer_consistency']
        print(f"\n[Cross-Layer Consistency]")
        print(f"  Status: {'OK' if cross['ok'] else 'FALHA'}")
        if 'identity_hash' in cross:
            print(f"  Identity Hash: {cross['identity_hash']}")
            print(f"  Context Pack Synced: {cross['context_pack_synced']}")

        context = results['context_pack_freshness']
        print(f"\n[Context Pack Status]")
        print(f"  Status: {context['status'].upper()}")
        if 'tokens' in context:
            print(f"  Tokens: {context['tokens']}")
        print(f"  Mensagem: {context['message']}")

        print(f"\n[Totais]")
        print(f"  Tests: {results['tests_passed']}/{results['tests_total']} passaram")
        print(f"  Resultado Final: {'APROVADO' if results['passed'] else 'REPROVADO'}")
        print("=" * 60)


def main():
    if len(sys.argv) > 1:
        agent_dir = Path(sys.argv[1])
    else:
        agent_dir = Path(__file__).parent.parent

    checker = ConsistencyChecker(agent_dir)
    results = checker.check()
    checker.print_report(results)

    sys.exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()