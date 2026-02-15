#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-6 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr06.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR6_CONTENT = """# NR-6 – Equipamento de Proteção Individual (EPI)

## Visão Geral

A **NR-6** estabelece os requisitos para **fornecimento, uso e manutenção de Equipamentos de Proteção Individual (EPI)**, definindo obrigações de empregadores e empregados na prevenção de riscos ocupacionais.

## Definições

### Equipamento de Proteção Individual (EPI)
Todo dispositivo ou produto, de uso individual, utilizado pelo trabalhador, destinado à proteção contra riscos que amacem a segurança e a saúde.

### Equipamento de Proteção Coletiva (EPC)
Dispositivo de uso coletivo, destinado a proteger a saúde e a integridade física dos trabalhadores.

**Princípio:** EPC tem prioridade sobre EPI.

## Classificação dos EPIs

### Por Natureza do Risco

#### Proteção da Cabeça
- Capacetes de segurança
- Protetores auditivos
- Protetores faciais
- Óculos de proteção

#### Proteção dos Ouvidos
- Protetores auditivos tipo concha
- Protetores auditivos tipo plug

#### Proteção Respiratória
- Máscaras descartáveis (PFF-1, PFF-2, PFF-3)
- Máscaras semi-faciais
- Máscaras faciais integrais
- Respiradores com suprimento de ar

#### Proteção dos Membros Superiores
- Luvas de proteção (vários tipos)
- Mangas de proteção
- Dedeiras de segurança
- Braçadeiras de proteção

#### Proteção do Tronco
- Coletes de segurança
- Aventais protetores
- Capas de proteção

#### Proteção dos Membros Inferiores
- Calçados de segurança
- Botinas de segurança
- Sapatos sociais com biqueira
- Órtese de proteção

#### Proteção Contra Quedas
- Cinto de segurança tipo pára-quedista
- Talabarte
- Absorvedor de energia
- trava-quedas
- Sistemas anti-queda

## Fornecimento de EPI

### Obrigações do Empregador
1. Fornecer EPIs adequados aos riscos
2. Treinar o trabalhador para uso correto
3. Substituir imediatamente quando danificado
4. Responsabilizar-se pela higienização e manutenção
5. Comunicar qualquer irregularidade ao usuário

### Critérios para Seleção
- Adequado ao risco específico
- Confortável ao trabalhador
- Não agravar o risco
- Permitir ajustes e regulagens
- Ser durável e de fácil higienização

### CA - Certificado de Aprovação

Todo EPI deve possuir:
- Número do CA válido
- Validade conforme especificação do fabricante
- Laudo de conformidade
- Indicação do fabricante

## Programa de Conservação de EPI

### Higienização
- Diária ou conforme necessidade
- Produtos adequados ao material
- Secagem completa antes do reuse

### Manutenção
- Periódica (conforme manual do fabricante)
- Registro de manutenções realizadas
- Substituição de peças desgastadas

### Armazenamento
- Local adequado (limpo, seco, ventilado)
- Separado por tipo de EPI
- Protegido de contaminação

## Uso de EPI

### Obrigações do Trabalhador
1. Usar o EPI apenas para a finalidade prevista
2. Zelar pela conservação
3. Comunicar ao empregador qualquer defeito
4. Responsabilizar-se pela higienização pessoal
5. Não fazer modificações no EPI

### Não Uso de EPI

Situacionalidades que equivalem a EPI inexistente:
- EPI inadequado ao risco
- EPI sem certificação
- EPI fora do prazo de validade
- EPI mal ajustado
- EPI danificado em uso

## EPIs para Riscos Específicos

### Riscos Químicos
- Luvas, avental, mangas de PVC ou neoprene
- Respiradores com filtros químicos
- Óculos ou viseiras

### Riscos Biológicos
- Luvas de procedimento
- Máscaras cirúrgicas ou N95
- Aventais descartáveis
- Protetores oculares

### Riscos Físicos (ruído)
- Protetores auditivos (concha ou plug)
- SNR mínimo conforme nível de ruído

### Riscos Ergonômicos
- Luvas anti-vibração
- Cinto de segurança para trabalho em altura
- Joelheiras para trabalho em地面

## Treinamento para Uso de EPI

### Conteúdo Mínimo
1. Finalidade e tipos de EPI
2. Riscos que protege
3. Limites de proteção
4. Conservação e higienização
5. Colocação e ajuste
6. Vedações de uso

### Periodicidade
- Na admissão
- Quando houver mudança de função
- Periodicamente (mínimo anual)
- Quando necessário por troca de EPI

## Penalidades

### Empregador
- Não fornecer EPI: multa e possível interdição
- Não treinar: multa agravada
- Fornecer EPI inadequado: multa e responsabilização

### Trabalhador
- Não usar EPI: advertência
- Recusa reiterada: demissão por justa causa
- Danificar EPI por negligência: responsabilização

## Principais Erros na Gestão de EPI

-Fornecer EPI genérico sem análise de risco
-Não treinar adequadamente
-Confundir EPI com uniforme
-Não inspecionar antes do uso
-Permitir uso de EPI danificado
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k for k in memory["knowledge"] if "NR-6" in k.get("text", "") and "EPI" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-6 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR6_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr06",
        }
    )
    _write_memory(memory)
    print("NR-6 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-6 ou EPIs."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
