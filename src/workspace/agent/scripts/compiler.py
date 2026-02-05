#!/usr/bin/env python3
"""compiler.py - Compila arquivos da Camada 1 em CONTEXT_PACK.md Autor: Gemini CLI-Cursor Mode Data: 2026-02-04 Versao: 1.0.0 """

import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import sys


class ContextCompiler:
    """Compila arquivos da Camada 1 em CONTEXT_PACK.md otimizado"""

    def __init__(self, agent_dir: Path = None):
        if agent_dir is None:
            agent_dir = Path(__file__).parent.parent
        self.agent_dir = Path(agent_dir).resolve()
        self.context_pack_path = self.agent_dir / "CONTEXT_PACK.md"

    def compile(self) -> Tuple[str, str]:
        """ Compila todos os arquivos da Camada 1 em CONTEXT_PACK.md

        Returns: (content, hash) da geracao
        """
        sections = []

        # 1. Identidade (sempre primeiro)
        identity = self._load_section("IDENTITY.md", max_tokens=200)
        sections.append(self._format_section("Identidade", identity))

        # 2. Regras Absolutas (top 5 do POLICIES.md)
        policies = self._extract_critical_policies()
        sections.append(self._format_section("Regras Absolutas", policies))

        # 3. Estilo (resumo)
        style = self._load_section("STYLE.md", max_tokens=150)
        sections.append(self._format_section("Estilo", style))

        # 4. Exemplos Chave (selecao inteligente)
        examples = self._select_relevant_examples()
        sections.append(self._format_section("Exemplos", examples))

        # 5. Estado Atual (ultra-resumido)
        current = self._summarize_current_state()
        sections.append(self._format_section("Estado", current))

        # 6. Metadados
        content = self._assemble(sections)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        return content, content_hash

    def _load_section(self, filename: str, max_tokens: int = None) -> str:
        """Carrega arquivo com limite de tokens (estimativa: 4 chars/token)"""
        path = self.agent_dir / filename
        if not path.exists():
            return f"[Arquivo {filename} nao encontrado]"

        content = path.read_text(encoding='utf-8')

        if max_tokens:
            max_chars = max_tokens * 4
            if len(content) > max_chars:
                content = content[:max_chars].rsplit('\n', 1)[0]
                content += "\n... [truncado para limites de contexto]"

        return content

    def _extract_critical_policies(self) -> str:
        """Extrai apenas as regras criticas (linhas com NUNCA/SEMPRE/TOP priority)"""
        path = self.agent_dir / "POLICIES.md"
        if not path.exists():
            return "[Sem politicas definidas]"

        content = path.read_text(encoding='utf-8')
        critical = []

        for line in content.split('\n'):
            if re.match(r'^\s*(\d+\.|[-*])\s*(NUNCA|SEMPRE|TOP|CRITICO)', line, re.IGNORECASE):
                critical.append(line.strip())
            if len(critical) >= 10:
                break

        return '\n'.join(critical) if critical else "[Nenhuma politica critica encontrada]"

    def _select_relevant_examples(self) -> str:
        """Seleciona exemplos relevantes"""
        path = self.agent_dir / "EXAMPLES.md"
        if not path.exists():
            return "[Sem exemplos]"

        content = path.read_text(encoding='utf-8')
        examples = []

        for section in re.split(r'##\s+Categoria:', content)[1:3]:
            if section.strip():
                examples.append("## Categoria:" + section)

        return '\n\n'.join(examples) if examples else "[Nenhum exemplo selecionado]"

    def _summarize_current_state(self) -> str:
        """Resume CURRENT_STATE.md em bullet points essenciais"""
        path = self.agent_dir / "CURRENT_STATE.md"
        if not path.exists():
            return "- Estado: inicial\n- Tarefa: nenhuma"

        content = path.read_text(encoding='utf-8')

        task_match = re.search(r'### Tarefa em Andamento.*?(###|$)', content, re.DOTALL)
        if task_match:
            lines = [l.strip() for l in task_match.group(0).split('\n') if l.strip() and not l.startswith('#')][:5]
            return '\n'.join(f'- {l}' for l in lines)

        return "- Estado: ativo\n- Tarefa: em andamento"

    def _format_section(self, title: str, content: str) -> str:
        return f"## {title}\n{content}\n\n"

    def _assemble(self, sections: List[str]) -> str:
        # Calculate hash of source files
        identity_path = self.agent_dir / "IDENTITY.md"
        identity_hash = ""
        if identity_path.exists():
            identity_hash = hashlib.md5(identity_path.read_bytes()).hexdigest()[:8]

        from datetime import timezone
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        header = f"""<!-- GERADO AUTOMATICAMENTE POR compiler.py NAO EDITE MANUALMENTE Timestamp: {timestamp} Hash: {identity_hash} -->"""
        return header + "\n\n" + "".join(sections)

    def compile_and_save(self) -> Tuple[str, str]:
        """Compila e salva o CONTEXT_PACK.md"""
        content, content_hash = self.compile()

        if self.context_pack_path.exists():
            old_content = self.context_pack_path.read_text(encoding='utf-8')
            old_hash_match = re.search(r'Hash:\s*([a-f0-9]+)', old_content)
            if old_hash_match and old_hash_match.group(1) == content_hash:
                print(f"[compiler] Context Pack inalterado (hash: {content_hash})")
                return content, content_hash

        self.context_pack_path.write_text(content, encoding='utf-8')
        print(f"[compiler] Context Pack atualizado (hash: {content_hash})")
        return content, content_hash


def main():
    if len(sys.argv) > 1:
        agent_dir = Path(sys.argv[1])
    else:
        agent_dir = Path(__file__).parent.parent

    compiler = ContextCompiler(agent_dir)
    content, hash_val = compiler.compile_and_save()

    # Verifica tamanho
    tokens = len(content) // 4
    print(f"[compiler] Tokens estimados: {tokens}")
    print(f"[compiler] Arquivo: {compiler.context_pack_path}")


if __name__ == "__main__":
    main()