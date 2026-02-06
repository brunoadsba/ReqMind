#!/usr/bin/env python3
"""Script para popular memória inicial com fatos básicos sobre o usuário.

Este script adiciona informações essenciais sobre Bruno na memória estruturada
do bot, permitindo que o agente tenha contexto pessoal básico.
"""

import sys
from pathlib import Path

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from workspace.memory.memory_manager import MemoryManager


def init_bruno_memory():
    """Popula memória inicial com fatos básicos sobre Bruno"""
    mm = MemoryManager()
    
    # Fatos básicos sobre o usuário
    facts = [
        {
            "content": "O usuário do bot é Bruno, user_id 6974901522 no Telegram",
            "tags": ["usuario", "pessoal"],
            "source": "init_script"
        },
        {
            "content": "Bruno usa o bot Telegram @br_bruno_bot para assistência pessoal",
            "tags": ["usuario", "telegram"],
            "source": "init_script"
        },
        {
            "content": "Bruno trabalha principalmente com desenvolvimento de software em Python e Next.js",
            "tags": ["usuario", "tech", "preferencias"],
            "source": "init_script"
        },
        {
            "content": "Bruno prefere respostas diretas, objetivas e profissionais",
            "tags": ["usuario", "preferencias", "comunicacao"],
            "source": "init_script"
        },
        {
            "content": "O diretório oficial do projeto do bot é /home/brunoadsba/ReqMind/assistente",
            "tags": ["projeto", "path"],
            "source": "init_script"
        },
        {
            "content": "Bruno usa o bot para análise de código, pesquisa, organização de informações e tarefas diárias",
            "tags": ["usuario", "uso", "preferencias"],
            "source": "init_script"
        },
    ]
    
    added_count = 0
    skipped_count = 0
    
    for fact_data in facts:
        fact_id = mm.add_fact(
            content=fact_data["content"],
            source=fact_data["source"],
            tags=fact_data["tags"],
            auto_extract=False
        )
        if fact_id:
            added_count += 1
            print(f"✅ Fato adicionado: {fact_data['content'][:60]}...")
        else:
            skipped_count += 1
            print(f"⚠️  Fato bloqueado (dados sensíveis ou duplicado): {fact_data['content'][:60]}...")
    
    stats = mm.get_stats()
    print(f"\n📊 Estatísticas da memória:")
    print(f"   - Fatos adicionados nesta execução: {added_count}")
    print(f"   - Fatos bloqueados/duplicados: {skipped_count}")
    print(f"   - Total de fatos na memória: {stats['total_stored']}")
    print(f"   - Tamanho do vocabulário: {stats['facts']['vocab_size']}")
    
    return added_count


if __name__ == "__main__":
    print("🧠 Inicializando memória do usuário...\n")
    added = init_bruno_memory()
    print(f"\n✅ Concluído! {added} fatos adicionados à memória.")
