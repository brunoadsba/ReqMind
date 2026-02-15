#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-5 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr05.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR5_CONTENT = """# NR-5 – Comissão Interna de Prevenção de Acidentes e de Assédio (CIPA)

## Visão Geral

A **NR-5** estabelece os requisitos para constituição, composição e funcionamento da **Comissão Interna de Prevenção de Acidentes e de Assédio (CIPA)**, órgão responsável pela prevenção de acidentes e doenças relacionadas ao trabalho.

## Campo de Aplicação

A NR-5 é obrigatória para:
- Estabelecimentos com **mais de 20 empregados**
- Órgãos públicos da administração direta e indireta
- Estabelecimentos de serviços de saúde
- Indústrias, comércio e prestação de serviços

## Composição da CIPA

### Representante do Empregador
-Designado pelo empregador
-Pode acumular função (exceto em casos específicos)
-Representa a gestão na comissão

### Representante dos Empregados
-Eleitos pelos empregados (votação secreta)
-Mandato de 1 ano (permitida uma recondução)
-Dispensa do trabalho durante o mandato (exceto justa causa)
-Não podem ser despedida até 12 meses após o final do mandato

### Quantidade de Membros
-1 a 20 empregados: 1 membro + 1 suplente
-21 a 300 empregados: 2 a 4 membros + igual número de suplentes
-301 a 500 empregados: 4 a 6 membros + igual número de suplentes
-501 a 1000 empregados: 6 a 8 membros + igual número de suplentes
-Acima de 1000: 8 a 12 membros + igual número de suplentes

## Processo Eleitoral

### Etapas
1. Publicação de Edital (15 dias antes da votação)
2. Inscrição de candidatos
3. Campanhas educativas
4. Votação (registro de presença)
5. Apuração e divulgação dos resultados
6. Posse dos eleitos

### Elegibilidade
-Pode se candidatar qualquer empregado estável
-Não podem ser candidatos: empregador, gestores com poder de demissão

## Atribuições da CIPA

### Preventivas
-Identificar riscos no ambiente de trabalho
-Propor medidas de prevenção
-Participar da elaboração do PGR
-Fiscalizar o uso de EPIs

### Investigativas
-Investigar acidentes e doenças ocupacionais
-Analisar causas e propor ações corretivas
-Elaborar relatórios de investigação

### Educativas
-Promover eventos de conscientização
-Desenvolver campanhas educativas
-Orientar sobre uso de EPIs e EPCs

### Deliberativas
-Aprovar o calendário de datas comemorativas
-Deliberar sobre treinamentos
-Propor políticas de SST

## Reuniões da CIPA

### Ordinárias
-Periodicidade determinada pela CIPA (máximo mensal)
-Convocação com antecedência mínima de 7 dias
-Registro em ata (leitura e aprovação)

### Extraordinárias
-Convocada pelo presidente ou pela maioria dos membros
-Tratamento de acidentes graves ou situações de emergência
-Quórum: maioria simples dos membros

## Atas da CIPA

Devem conter:
-Data, hora e local da reunião
-Presença de cada membro
-Assuntos tratados
-Votações e decisões
-Assinatura dos presentes

## Treinamento da CIPA

### Cipeiros
-Duração: 20 horas (mínimo)
-Conteúdo: normas de SST, investigação de acidentes, ergonomia
-Realizado dentro do horário de trabalho

### Presidente da CIPA
-Duração: 40 horas (mínimo)
-Conteúdo avançado: gestão de riscos, legislação
-Certificação obrigatória

## Prevenção de Assédio

Desde 2023, a CIPA inclui a prevenção ao assédio moral e sexual:
-Identificação de situações de assédio
-Orientação aos empregados
-Coordenação com ouvidoria
-Colaboração na investigação de casos

## Indicadores de Desempenho da CIPA

-Taxa de participação nas reuniões
-Número de propostas apresentadas
-Eficácia das ações propostas
-Redução de acidentes
-Índice de treinamentos realizados

## Penalidades

-Empregador não constitui CIPA: multa
-Impedimento de funcionamento: interdição
-Despedida de cipeiro sem justa causa: reversão + indenização

## Críticas Comuns à CIPA

- Reuniões meramente formais
- Falta de autonomia real
- Membros sem conhecimento técnico
- Não integração com o SGSST
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k
        for k in memory["knowledge"]
        if "NR-5" in k.get("text", "") and "CIPA" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-5 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR5_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr05",
        }
    )
    _write_memory(memory)
    print("NR-5 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-5 ou CIPA."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
