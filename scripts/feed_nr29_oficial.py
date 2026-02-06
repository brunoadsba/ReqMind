#!/usr/bin/env python3
"""
Injeta o texto oficial da NR-29 (DOU) na memória RAG do bot.
Divide por seções (29.1, 29.2, ... ANEXO, Glossário) para buscas mais precisas.

Uso:
  PYTHONPATH=src python scripts/feed_nr29_oficial.py [caminho_para_nr29_oficial_dou.txt]

Se não informar caminho, usa scripts/nr29_oficial_dou.txt na raiz do projeto.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory


def split_nr29_by_sections(content: str) -> list[tuple[str, str]]:
    """
    Divide o texto da NR-29 em blocos por seção.
    Cada bloco começa em um título (29.1, 29.2, ANEXO I, Glossário) e vai até o próximo.
    Retorna lista de (titulo, texto) para cada bloco.
    """
    # Início de item numerado (29.1, 29.2.1), ANEXO I/II/..., ou Glossário
    pattern = re.compile(
        r"^(29\.\d+(?:\.\d+)*\s+|ANEXO\s+[IVXLCDM]+\s*(?:-\s*[^\n]*)?|Glossário\s*)$",
        re.MULTILINE,
    )
    starts = [m.start() for m in pattern.finditer(content)]
    sections = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(content)
        block = content[start:end].strip()
        if len(block) < 50:
            continue
        first_line = block.split("\n")[0].strip()[:80]
        sections.append((first_line, block))
    # Cabeçalho (antes do primeiro 29.1)
    if starts and starts[0] > 100:
        preamble = content[: starts[0]].strip()
        if len(preamble) > 100:
            sections.insert(0, ("NR-29 DOU cabeçalho e sumário", preamble))
    return sections


def main():
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if path_arg:
        path = Path(path_arg).resolve()
    else:
        path = project_root / "scripts" / "nr29_oficial_dou.txt"
    if not path.exists():
        print(f"Arquivo não encontrado: {path}")
        print("Crie o arquivo com o texto oficial da NR-29 (DOU) e execute novamente.")
        return 1

    content = path.read_text(encoding="utf-8")
    if len(content) < 500:
        print("Arquivo muito curto. Cole o texto completo da NR-29 (DOU) no arquivo.")
        return 1

    sections = split_nr29_by_sections(content)
    if not sections:
        # Fallback: um único bloco com todo o texto
        sections = [("NR-29 DOU completo", content)]

    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    # Evitar duplicar: remover entradas antigas do mesmo feed
    memory["knowledge"] = [
        k for k in memory["knowledge"]
        if k.get("source") != "nr29_oficial_dou"
    ]

    added = 0
    for title, text in sections:
        entry = {
            "text": f"NR-29 (texto oficial DOU)\n\n{text}" if not text.startswith("NR-29") else text,
            "timestamp": "2026-02-05",
            "source": "nr29_oficial_dou",
        }
        memory["knowledge"].append(entry)
        added += 1

    _write_memory(memory)
    print(f"NR-29 oficial (DOU) injetada na memória RAG: {added} seções.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
