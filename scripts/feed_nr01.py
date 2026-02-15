#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-1 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr01.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR1_CONTENT = """# NR-1 – Disposições Gerais e Gerenciamento de Riscos Ocupacionais

## Visão Geral

A **NR-1** estabelece os requisitos para o **Gerenciamento de Riscos Ocupacionais (GRO)**, sendo a norma fundamental que integra todas as outras Normas Regulamentadoras. Ela define as bases do Sistema de Gestão de Segurança e Saúde no Trabalho (SGSST).

## Campo de Aplicação

Aplica-se a:
- Estabelecimentos que possuam empregados regidos pela CLT
- Órgãos públicos da administração direta e indireta
- Estabelecimentos de serviços de saúde
- Indústrias em geral
- Construção civil
- Agricultura e pecuária

## Princípios Fundamentais

### 1. Hierarquia de Controles
1. Eliminação do risco
2. Substituição da fonte de risco
3. Controle engineering
4. Controle administrativo
5. Equipamento de Proteção Individual (EPI)

### 2. Análise de Risco
A análise de risco deve considerar:
- Natureza do agente (físico, químico, biológico, ergonômico, de acidente)
- Tempo de exposição do trabalhador
- Quantidade do agente no ambiente
- Características pessoais do trabalhador

## Documentação Obrigatória

### Documentos do SGSST
- Política de Segurança e Saúde no Trabalho
- Objetivos do SGSST
- Indicadores de avaliação do SGSST
- Registros de perigos e riscos ocupacionais
- Programa de Gerenciamento de Riscos (PGR)
- Análise Ergonômica do Trabalho (AET) - quando aplicável

### Cadastros e Registros
- Cadastro de empregados
- Registro de Riscos Ambientais (LTCAT)
- Programa de Controle Médico de Saúde Ocupacional (PCMSO)
- Comunicações de Acidentes de Trabalho (CAT)

## Programa de Gerenciamento de Riscos (PGR)

O PGR deve conter:
1. Inventário de perigos e avaliação de riscos ocupacionais
2. Plano de ação com medidas de prevenção
3. Descrição das funções e trabalhos
4. Medidas de controle adotadas
5. Critérios para monitoramento e avaliação
6. Periodicidade de revisão

## Responsabilidades

### Do Empregador
- Garantir ambiente de trabalho seguro
- Fornecer EPIs adequados
- Promover treinamentos
- Implementar SGSST
- Fiscalizar cumprimento das normas

### Dos Empregados
- Cumprir procedimentos de segurança
- Usar corretamente EPIs
- Reportar situações de risco
- Participar de treinamentos

## Penalidades

- Advertência escrita (infrações leves)
- Multa (infrações médias e graves)
- Embargo/interdição (riscos graves e iminentes)
- Responsabilização criminal (acidentes graves/fatais)

## Integração com Outras NRs

A NR-1 é a norma-mãe e integra-se com:
- NR-5 (CIPA)
- NR-6 (EPI)
- NR-7 (PCMSO)
- NR-9 (PPRA)
- NR-17 (Ergonomia)
- NR-35 (Trabalho em Altura)

## Conceitos-Chave

- **Risco ocupacional**: Potencial de causar dano à saúde
- **Perigo**: Fonte ou situação com potencial de causar dano
- **Exposição**: Contato do trabalhador com o risco
- **Gro**: Processo completo de identificação, análise e controle
- **Medida de controle**: Ação para eliminar ou reduzir riscos

## Indicadores de Desempenho

- Taxa de frequência de acidentes
- Taxa de gravidade de acidentes
- Número de não conformidades
- Percentual de treinamentos realizados
- Eficácia das ações corretivas

## Cronograma de Implementação

2024-2025: Transição do PPRA/PCMSO para o PGR unificado
2025: Obrigatoriedade completa do novo modelo
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k
        for k in memory["knowledge"]
        if "NR-1" in k.get("text", "") and "Disposições Gerais" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-1 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR1_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr01",
        }
    )
    _write_memory(memory)
    print("NR-1 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-1 ou gerenciamento de riscos."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
