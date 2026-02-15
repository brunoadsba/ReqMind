#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-35 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr35.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR35_CONTENT = """# NR-35 – Trabalho em Altura

## Visão Geral

A **NR-35** estabelece os requisitos para **segurança no trabalho em altura**, definindo procedimentos, EPIs, responsabilidades e competências necessárias para prevenir acidentes com quedas.

## Campo de Aplicação

Aplica-se a todo trabalho em altura, ou seja:
- Trabalho onde existe risco de queda capaz de lesionar o trabalhador
- Acima de 2,00 metros (referência do piso)
- Acima de 1,85 metros quando há risco de queda sobre superfícies cortantes ou penetrantes
- Qualquer altura em plataformas, escadas, estruturas sem proteção

## Definições Fundamentais

### Trabalho em Altura
Trabalho executado em níveis diferentes, com diferença de altura superior a 2,00m em relação ao piso inferior, onde exista risco de queda.

### Plataformas de Trabalho
Superfície temporária elevada para execução de trabalho em altura.

### Sistemas de Proteção Contra Queda de Altura (SPQA)
Conjunto de equipamentos e procedimentos que visam evitar ou deter a queda de trabalhadores.

## Análise de Risco

O empregador deve realizar análise de risco que contemple:
1. Identificação dos riscos de queda
2. Avaliação das condições do local de trabalho
3. Seleção dos sistemas de proteção adequados
4. Procedimentos de trabalho seguros

## Planejamentos Obrigatórios

### Permissão de Trabalho Especial (PTE)

Documento obrigatório para trabalhos em altura que contemple:
- Localização e descrição do serviço
- Riscos identificados e medidas de controle
- Tempo estimado de exposição
- Epis e EPCs necessários
- Nome e função dos trabalhadores envolvidos
- Responsável pela liberação do trabalho

### 安-planning de Resgate
- Plano de resgate para trabalho em altura
- Tempo máximo de permanência no sistema (10 minutos de suspensão inerte)
- Equipamento de resgate disponível

## Sistemas de Proteção Contra Quedas

### Proteção Coletiva

1. **Guarda-corpos**
   - Altura: 1,10m a 1,20m do piso
   - Travessão intermediário
   - Rodapé de 0,20m
   - Resistência mínima: 150kg/m

2. **Redes de Proteção**
   - Instaladas no máximo 2,00m abaixo do piso de trabalho
   - Malha máxima de 0,60m x 0,60m
   - Resistência mínima: 150kg/m²

3. **Barreiras físicas**
   - Cones e fitas de sinalização
   - Telas de proteção

### Proteção Individual

**Sistema de供緙ão individual contra quedas (SPQI)**

Componentes obrigatórios:
1. **Cinto de segurança tipo pára-quedista**
   - Anéis dorsais, peitorais ou laterais
   - Fivelas de ajuste
   - Costuras reforçadas

2. **Talabarte**
   - Comprimento: 0,90m a 1,80m
   - Gancho de abertura mínima 50mm
   - Absorvedor de energia (opcional ou integrado)

3. **Dispositivo trava-quedas**
   - Instalado em linha de vida ou cabo-guia
   - Movimentação livre (trecho de 0,60m mínimo)
   - Trava automática em caso de queda

4. **Linha de vida**
   - Corda flexível vertical ou horizontal
   - Ancoragem com resistência mínima de 1500kg
   - Cabo de aço ou corda sintética

5. **Absorvedor de energia**
   - Limitador de força de impacto (máximo 6kN)
   - Degradação visível após uso

## EPIs para Trabalho em Altura

### Obrigatórios
- Cinto de segurança tipo pára-quedista
- Talabarte com absorvedor
- Trava-quedas
- Capacete de segurança com jugular
- Calçado de segurança com solado antiaderente
- Luvas de proteção

### Recomendados
- Protetor solar
- Óculos de proteção
- Protetor auricular (ambientes ruidosos)
- Roupas apropriadas ao clima

## Procedimentos de Trabalho

### Antes do Trabalho
1. Análise de risco realizada
2. PTE emitida e autorizada
3. Local isolado e sinalizado
4. EPIs inspecionados e adequados
5. Sistema de resgate preparado
6. Condições climáticas favoráveis

### Durante o Trabalho
1. Permanecer conectado ao SPQI
2. Não ultrapassar bordas sem proteção
3. Manter área de trabalho organizada
4. Comunicar qualquer irregularidade
5. Respeitar tempo máximo de exposição

### Após o Trabalho
1. Remover EPIs corretamente
2. Inspecionar equipamentos
3. Guardar em local adequado
4. Documentar incidentes
5. Liberar área

## Capacitação

### Trabalhador Autorizado
- Capacitação periódica (máximo bienal)
- Conhece riscos e procedimentos
- Usa corretamente EPIs
- Identifica situações de emergência

### Supervisor de Trabalho em Altura
- Curso específico (mínimo 8 horas)
- Supervisiona trabalhos
- Autoriza emissão de PTE
- Atua em emergências

## 安-ergências

### Plano de Resgate
Obrigatório para trabalhos em altura:
1. Meios de evacuação
2. Técnicas de resgate
3. Equipamentos disponíveis
4. Procedimentos de primeiros socorros
5. Comunicação de emergência

### Primeiros Socorros em Quedas
1. Manter trabalhador imóvel
2. Liberar vias aéreas
3. Controlar sangramentos
4. Manuter temperatura corporal
5. Acionar socorro especializado

### Tempo Crítico
- **Suspensão inerte:** máximo 10 minutos
- Após este tempo, iniciar resgate

## Infraestrutura e Locais de Trabalho

### Escadas de Mão
- Apoiadas em superfície firme
- Extensão mínima de 1,00m acima do ponto de acesso
- Proibido trabalhar nos 2 últimos degraus
- Não usar escadas danificadas

### Escadas com Plataforma
- Plataformas com guarda-corpos
- Piso antiderrapante
- Acesso seguro

### Andaimes
- Projetados por profissional habilitado
- Capacidade de carga verificada
- Ancorados à estrutura
- Guarda-corpos completos

### Plataformas Elevatórias
- Inspeção diária
- Operador treinado
- Área de trabalho isolada

## Responsabilidades

### Do Empregador
- Garantir ambiente seguro
- Fornecer EPIs adequados
- Capacitar trabalhadores
- Implementar procedimentos
- Supervisionar trabalhos

### Do Trabalhador
- Cumprir procedimentos
- Usar EPIs corretamente
- Inspecionar equipamentos
- Reportar situações de risco
- Participar de capacitações

## Principais Causas de Acidentes

- Falta de proteção em bordas
- Uso inadequado de EPIs
- Escadas em mau estado
- Desatenção do trabalhador
- Condições climáticas adversas
- Sobrecarga de plataformas

## Penalidades

### Graves
- Não fornecer SPQ adequado
- Não capacitar trabalhadores
- Não emitir PTE

### Muito Graves
- Trabalho sem proteção em altura
- Acidentes com incapacidade
- Descumprimento de interdição

## Dicas de Segurança

1. **ANTES:** Planeje, analise riscos, prepare equipamentos
2. **DURANTE:** Mantenha-se conectado, respeite limites
3. **DEPOIS:** Resgate, inspeção, documentação
4. **NUNCA:** Trabalhe em altura em condições adversas
5. **SEMPRE:** Use sistema completo de proteção
"""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    existing = [
        k
        for k in memory["knowledge"]
        if "NR-35" in k.get("text", "") and "Trabalho em Altura" in k.get("text", "")
    ]
    if existing:
        print("Conteúdo da NR-35 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append(
        {
            "text": NR35_CONTENT,
            "timestamp": "2026-02-06",
            "source": "feed_nr35",
        }
    )
    _write_memory(memory)
    print("NR-35 injetada na memória RAG com sucesso.")
    print(
        "O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-35 ou trabalho em altura."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
