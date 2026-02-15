#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-33 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr33.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR33_CONTENT = """# NR-33 – Segurança e Saúde em Trabalhos em Espaços Confinados

## Visão Geral

A **NR-33** estabelece os requisitos para **identificação, entrada e trabalho em espaços confinados**, visando a proteção dos trabalhadores contra riscos ocupacionais existentes nestas áreas.

## Definições

### Espaço Confinado

Local que:
1. Não é projetado para ocupação humana contínua
2. Possui entrada e saída limitadas ou restritas
3. Pode acumular substâncias tóxicas, inflamáveis ou explosivas
4. Pode ter atmosfera deficiente de oxigênio
5. Pode causar soterramento ou afogamento

### Exemplos de Espaços Confinados

- Tanques de armazenamento
- Silos e reservatórios
- Caldeiras e vasos de pressão
- Tubulações e dutos
- Poços e caixas de inspeção
- Tanques de navios e vagões
- Fossas e galerias de esgoto
- Cofres e câmaras frigoríficas
- Estruturas navais e offshore

## Classificação dos Espaços Confinados

### Classe 1 (Grupo A)
Espaço confinado que contém ou tem potencial de conter:
- Atmosfera inflamável ou explosiva
- Gases ou vapores inflamáveis
- Poeiras combustíveis em concentração explosiva

### Classe 2 (Grupo B)
Espaço confinado que contém:
- Atmosfera tóxica
- Oxigênio em concentração abaixo de 19,5% ou acima de 23,5%
- Líquidos ou sólidos em quantidade suficiente para liberar上述有毒或可燃气体

### Classe 3 (Grupo C)
Espaço confinado que:
- Não possui atmosfera potencialmente perigosa
- Contém outros riscos reconhecidos
- Pode ser evacuado rapidamente em caso de emergência

## Riscos em Espaços Confinados

### Riscos Atmosféricos

1. **Deficiência de Oxigênio (< 19,5%)**
   - Desorientação
   - Perda de consciência
   - Morte por anoxia

2. **Excesso de Oxigênio (> 23,5%)**
   - Aceleração de combustão
   - Risco de incêndio/explosão

3. **Gases Tóxicos**
   - H2S (sulfureto de hidrogênio)
   - CO (monóxido de carbono)
   - CO2 (dióxido de carbono)
   - Amônia, cloro, etc.

4. **Gases/Inflamáveis**
   - GLP, metano, propano
   - Poeiras combustíveis

### Riscos Físicos

- Soterramento
- Afogamento
- Quedas
- Choques elétricos
- Temperaturas extremas
- Partes móveis de equipamentos
- Estruturas instáveis

### Riscos Biológicos

- Bactérias e fungos
- Vírus
- Parasitas
- Animais peçonhentos

## Requisitos para Entrada em Espaços Confinados

### Permissão de Entrada e Trabalho (PET)

Documento obrigatório que deve conter:
1. Identificação do espaço confinado
2. Riscos identificados
3. Medidas de controle adotadas
4. EPIs e EPCs necessários
5. Procedimentos de entrada e saída
6. Tempo máximo de exposição
7. Procedimentos de resgate
8. Nome e função de todos os trabalhadores
9. Nome do responsável pela autorização
10. Data, horário e período de validade

### Procedimentos Obrigatórios

#### Antes da Entrada

1. **Isolamento do Espaço**
   - Fechamento de válvulas e tampas
   - Bloqueio de energias (LOTO)
   - Drenagem e limpeza
   - Ventilação

2. **Teste de Atmosfera**
   - Oxigênio: 19,5% a 23,5%
   - Gases inflamáveis: LIE/10 (Limite Inferior de Explosividade)
   - Gases tóxicos: limites de tolerância

3. **Ventilação**
   - Natural ou mecânica
   - Garantir atmosfera segura
   - Manter ventilação durante todo o trabalho

4. **Autorização**
   - Emitir PET
   - Designar vigia
   - Confirmar disponibilidade de resgate

#### Durante a Entrada

1. **Vigia**
   - Trabalhadores designado fora do espaço
   - Manter comunicação constante
   - Acionar resgate se necessário
   - Não pode abandonar o posto

2. **EPIs Obrigatórios**
   - Cinto de segurança com talabarte
   - Respirador autônomo (quando necessário)
   - Capacete de segurança
   - Calçado de segurança
   - Luvas de proteção
   - Detector de gás pessoal

3. **Comunicação**
   - Contato visual ou por rádio
   - Sinais predefinidos
   - Check-ins periódicos

#### Após a Entrada

1. Remover trabalhadores do espaço
2. Fechar e sinalizar o espaço
3. Cancelar a PET
4. Documentar incidentes

## Responsabilidades

### Do Empregador

1. Identificar todos os espaços confinados
2. Classificar os espaços (Classe 1, 2 ou 3)
3. Elaborar procedimentos específicos
4. Capacitar trabalhadores
5. Fornecer EPIs adequados
6. Implementar medidas de resgate
7. Manter registros atualizados

### Do Trabalhador

1. Cumprir procedimentos estabelecidos
2. Usar EPIs corretamente
3. Comunicar situações de risco
4. Participar de capacitações
5. Interromper trabalho em caso de risco

### Do Responsável Técnico

1. Elaborar e revisar procedimentos
2. Supervisionar trabalhos
3. Autorizar emissão de PET
4. Decidir sobre procedimentos de resgate

## Capacitação

### Mínimo de 16 horas

1. Definições e identificação de espaços confinados
2. Riscos atmosféricos e físicos
3. Procedimentos de entrada
4. Uso de EPIs e detectores de gás
5. Ventilação e atmosférica
6. Procedimentos de resgate e primeiros socorros
7. Legislação aplicável

### Recycling

Periodicidade definida pelo empregador (mínimo bienal)

## Sistemas de Resgate

### Requisitos

1. Plano de resgate documentado
2. Equipamentos de resgate disponíveis
3. Treinamento de equipes de resgate
4. Tempo de resposta máximo: 4 minutos
5. Contato com serviços de emergência

### Equipamentos de Resgate

- Respirador autônomo de emergência
- Cinto de resgate
- Talabartes e cordas
- Maca de elevação
- Kit de primeiros socorros
- Comunicação (rádio)

## Monitoramento Contínuo

### Detectores Portáteis

Deve medir continuamente:
- Oxigênio (O2)
- Gases inflamáveis (LEL)
- Monóxido de carbono (CO)
- Sulfureto de hidrogênio (H2S)

### Calibração

- Antes de cada uso
- Por profissional habilitado
- Registro de calibração

## Penalidades

### Graves

- Não identificar espaços confinados
- Não emitir PET
- Trabalhar sem autorização

### Muito Graves

- Fatalidade em espaço confinado
- Trabalhadores sem capacitação
- Não disponibilizar equipamentos de resgate

## Dicas de Segurança

1. **NUNCA** entre sem autorização e PET
2. **SEMPRE** teste a atmosfera antes de entrar
3. **MANTENHA** ventilação durante todo o trabalho
4. **DESIGNE** vigia qualificado
5. **TENHA** plano de resgate pronto
6. **USE** EPIs adequados
7. **COMunique** qualquer irregularidade
8. **NÃO** apresse procedimentos

## Emergências Mais Comuns

- Desmaio por deficiência de oxigênio
- Envenenamento por H2S ou CO
- Soterramento
- Afogamento
- Incêndio ou explosão

## NR-33 e Outras NRs

A NR-33 integra-se com:
- NR-1 (Disposições Gerais)
- NR-5 (CIPA)
- NR-6 (EPI)
- NR-10 (Eletricidade)
- NR-35 (Trabalho em Altura)
- NR-23 (Proteção Contra Incêndios)
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k
        for k in memory["knowledge"]
        if "NR-33" in k.get("text", "") and "Espaço Confinado" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-33 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR33_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr33",
        }
    )
    _write_memory(memory)
    print("NR-33 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-33 ou espaço confinado."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
