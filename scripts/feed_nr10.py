#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-10 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr10.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR10_CONTENT = """# NR-10 – Segurança em Instalações e Serviços em Eletricidade

## Visão Geral

A **NR-10** estabelece os requisitos e condições mínimas para **garantir a segurança dos trabalhadores** que interagem com instalações elétricas e serviços em eletricidade, abrangendo geração, transmissão, distribuição e consumo.

## Campo de Aplicação

Aplica-se a:
- Instalações elétricas de edificações
- Estabelecimentos industriais
- Estabelecimentos comerciais
- Servicios de manutenção e reparo
- Construção, montagem e operação
- Qualquer trabalho com eletricidade

## Conceitos Fundamentais

### Sistema Elétrico
-Conjunto de componentes associados para gerar, transmitir, distribuir ou utilizar energia elétrica

### Riscos Elétricos
-Risco de choque elétrico (passagem de corrente pelo corpo)
-Risco de arco elétrico (faísca com altas temperaturas)
-Risco de incêndio e explosão
-Risco de campos eletromagnéticos

### Partes Vulneráveis do Corpo
-Coração (fibrilação ventricular)
-Pulmões (paralisia respiratória)
-Músculos (contrações involuntárias)
-Sistema nervoso central

## Medidas de Controle de Risco

### Hierarquia de Controles (NR-10)

1. **Desenergização**
   - Desligamento completo
   - Seccionamento
   - Impedimento de reenergização
   - Constatação da ausência de tensão

2. **Aterramento Funcional**
   - TN-S, TN-C, TN-C-S, TT, IT
   - Proteção contra sobretensões

3. **Equipotencialização**
   - Ligação de todas as partes metálicas
   - Aterramento de carcaças e estruturas

4. **Segurança por Distância**
   - Afastamento de partes energizadas
   - Zona de controle e zona de risco

5. **Dispositivos de Proteção**
   - DR (Diferencial Residual)
   - DPS (Dispositivo de Proteção contra Surtos)
   - Disjuntores e fusíveis

6. **Sinalização**
   - Placas de advertência
   - Bloqueios e tarjas

## Procedimentos de Trabalho

### Permissão de Trabalho (PT)

Documento obrigatório para trabalhos com:
- Partes energizadas
- Redes e instalações de alta tensão
- Serviços em altura com risco elétrico

### Conteúdo da PT
- Descrição do serviço
- Riscos identificados
- Medidas de segurança necessárias
- EPIs e EPCs requeridos
- Responsáveis e executantes
- Data, hora e local

### Técnicas de Trabalho

#### Desenergizado (preferencial)
1. Desligamento
2. Seccionamento
3. Bloqueio e etiquetagem (LOTO)
4. Constatação de ausência de tensão
5. Instalação de aterramento temporário
6. Proteção de partes energizadas
7. Liberação para serviço

#### Sob Tensão (excepcional)
1. Autorização formal do empregador
2. Análise de risco detalhada
3. Procedimento específico
4. Supervisor de trabalho presente
5. EPIs específicos para trabalho sob tensão

## NR-10 em Contexto

### Instalações Elétricas

#### Baixa Tensão (B.T.)
- Igual ou inferior a 1000V em corrente alternada
- Ou 1500V em corrente contínua

#### Alta Tensão (A.T.)
- Superior a 1000V em corrente alternada
- Ou superior a 1500V em corrente contínua

## Qualificação e Habilitação

### Trabalhador Capacitado
- Recebeu capacitação teórica e prática
- Conhece riscos da eletricidade
- Sabe procedimentos seguros

### Trabalhador Habilitado
- Trabalhador capacitado com curso específico
- Registro no CREA (quando aplicável)
- Autorizado pelo empregador

### Classes de Habilitação
-Classe 1: Instalação e manutenção em BT
-Classe 2: Instalação e manutenção em BT e AT
-Classe 3: Projetos em BT
-Classe 4: Projetos em BT e AT

## EPIs Específicos para Eletricidade

- Luvas isolantes de borracha ( classe 0 a 4 )
- Mangas isolantes
- Calçados isolantes
- Capacete de segurança dielétrico
- Óculos ou viseira de proteção
- Protetor facial contra arco elétrico
- Manga e calça de proteção
- Luvas de proteção mecânica sobre as isolantes

## Documentação Obrigatória

### Projeto das Instalações Elétricas
- Memorial descritivo
- Diagramas unifilares
- Especificações técnicas
- ART (Anotação de Responsabilidade Técnica)

### Inspeções e Manutenções
- Cronograma de manutenções
- Registros de inspeções
- Relatórios de ensaios
- Laudos de conformidade

### Registros de Treinamentos
- Capacitações realizadas
- Participantes e datas
- Conteúdos ministrados
- Avaliações de aprendizagem

## Penalidades

### Infrações Graves
- Trabalhar em instalação energizada sem autorização
- Não usar EPIs específicos para eletricidade
- Não seguir procedimentos de LOTO

### Infrações Muito Graves
- Fatalidade por falha de procedimento
- Acidente com múltiplas vítimas
- Descumprimento de embargo

## Acidentes Elétricos Mais Comuns

- Contato direto (toque em parte energizada)
- Contato indireto (toque em carcaça energizada)
- Arco elétrico (manobras incorretas)
- Falha de aterramento
- Uso de ferramentas inadequadas

## Dicas Práticas

1. SEMPRE desligue antes de trabalhar
2. Use LOTO mesmo em baixa tensão
3. TESTE antes de tocar
4. Use EPIs adequados à classe de tensão
5. MANTENHA distância de segurança
6. NÃO trabalhe sozinho em eletricidade
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k
        for k in memory["knowledge"]
        if "NR-10" in k.get("text", "") and "Eletricidade" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-10 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR10_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr10",
        }
    )
    _write_memory(memory)
    print("NR-10 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-10 ou instalações elétricas."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
