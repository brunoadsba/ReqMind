#!/usr/bin/env python3
"""
Injeta o conteúdo da NR-29 na memória RAG do bot.
Uso: PYTHONPATH=src python scripts/feed_nr29_to_memory.py
"""

import sys
from pathlib import Path

# Garante que src está no path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from workspace.tools.impl.rag_memory import load_memory, _write_memory

NR29_CONTENT = """# NR-29 – Segurança e Saúde no Trabalho Portuário

## Visão geral

A **NR-29** estabelece os requisitos de **Segurança e Saúde no Trabalho Portuário**, aplicáveis a **portos organizados** e **instalações portuárias**, abrangendo trabalhadores portuários **avulsos e vinculados**, operações, equipamentos e infraestrutura.

É uma norma **curta em extensão**, porém **densa e altamente específica** do ambiente portuário.

## Aplicação da NR-29

Aplica-se a: portos organizados; instalações portuárias; operações de carga, descarga, movimentação e armazenagem; atividades no cais, pátios, armazéns e a bordo de embarcações atracadas.

## Atores do porto e responsabilidades

**Autoridade Portuária (ex.: CODEBA):** Infraestrutura segura do porto; condições do cais, defensas e guarda-corpos; iluminação, vias internas e sinalização; áreas comuns.

**Operador Portuário:** Execução da operação portuária; segurança da operação; equipamentos; EPIs dos trabalhadores; procedimentos operacionais e cumprimento das NRs.

**OGMO – Órgão Gestor de Mão de Obra:** Entidade autônoma; administra mão de obra portuária avulsa; cadastro, escala, capacitação e treinamentos.

**Trabalhadores Portuários:** Cumprir procedimentos de segurança; usar corretamente EPIs; participar dos treinamentos obrigatórios.

## Infraestrutura portuária segura

Bordas de cais protegidas; guarda-corpos adequados; defensas em bom estado; pisos regulares e antiderrapantes; iluminação suficiente; sinalização clara de riscos; acesso seguro navio–terra (passadiços e escadas).

## Operações portuárias

Carga e descarga; estivagem e desestivagem; peação e desapeação; arrumação de cargas no porão. A norma foca na segurança da execução.

## Equipamentos portuários

Guindastes de cais, portêineres, transtêineres, spreader, grabs, empilhadeiras portuárias. Exigências: inspeção periódica; manutenção comprovada; operadores habilitados; dispositivos de segurança funcionais. Equipamento sem inspeção válida = não conformidade grave.

## Trabalho a bordo de embarcação atracada

Iluminação adequada no porão; ventilação quando necessária; escadas seguras; controle de acesso; sinalização de risco.

## Cargas perigosas

Identificação correta; segregação por compatibilidade; sinalização adequada; procedimentos específicos; plano de emergência. Ausência de controle pode justificar suspensão da operação.

## EPI e EPC

EPIs mínimos: capacete, calçado de segurança, colete refletivo. EPC tem prioridade sobre EPI. EPI inadequado equivale a EPI inexistente.

## Riscos críticos

Queda no cais; atropelamento por veículos internos; esmagamento por carga suspensa; queda de objetos; condições climáticas (vento, chuva, maresia).

## Trânsito interno portuário

Segregação entre pedestres e veículos; controle de velocidade; sinalização horizontal e vertical; iluminação adequada.

## Treinamento e capacitação

Treinamento inicial e periódico obrigatórios; registro formal; trabalhador sem treinamento não deve operar.

## Fiscalização e suspensão

O TST pode recomendar paralisação em caso de risco grave e iminente, falha estrutural, equipamento inseguro, ausência de procedimento essencial. Sempre com registro técnico e comunicação à chefia.

## Integração com outras NRs

NR-06 (EPI), NR-11 (movimentação de materiais), NR-12 (máquinas e equipamentos), NR-33 (espaço confinado), NR-35 (trabalho em altura). A NR-29 adapta essas normas à realidade portuária.

## Erros comuns do TST iniciante

Confundir responsabilidades entre Autoridade Portuária, Operador e OGMO; corrigir operador em público; não registrar orientações; improvisar interpretação; ignorar cultura portuária; excesso de rigidez sem critério técnico.

## Perfil eficaz do TST portuário

Postura firme e calma; domínio da NR-29; boa comunicação; registro técnico consistente; diálogo sem abrir mão da norma.

## Checklist prático de inspeção

Guarda-corpos e bordas do cais; iluminação; equipamentos com inspeção válida; uso correto de EPI; sinalização de riscos; controle de trânsito interno; procedimentos para cargas perigosas; registro de não conformidades.

## Conclusão

A NR-29 é a espinha dorsal da segurança no porto. Dominar seus conceitos, responsabilidades e riscos críticos permite ao TST atuar com segurança técnica, respaldo institucional e eficácia preventiva."""


def main():
    memory = load_memory()
    if "knowledge" not in memory:
        memory["knowledge"] = []

    # Evita duplicar se já existir entrada com NR-29
    existing = [k for k in memory["knowledge"] if "NR-29" in k.get("text", "") and "Segurança e Saúde no Trabalho Portuário" in k.get("text", "")]
    if existing:
        print("Conteúdo da NR-29 já está na memória. Nada a fazer.")
        return 0

    memory["knowledge"].append({
        "text": NR29_CONTENT,
        "timestamp": "2026-02-05",
        "source": "feed_nr29",
    })
    _write_memory(memory)
    print("NR-29 injetada na memória RAG com sucesso.")
    print("O bot poderá usar rag_search para consultar quando o usuário perguntar sobre NR-29 ou trabalho portuário.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
