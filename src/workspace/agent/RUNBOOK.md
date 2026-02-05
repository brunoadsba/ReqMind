# RUNBOOK.md - Manual de Operacoes

## Inicializacao de Sessao

### Pre-Execucao (Sempre)
1. Ler `CONTEXT_PACK.md` - carrega identidade, politicas e estilo
2. Ler `CURRENT_STATE.md` - carrega estado ativo e contexto
3. Verificar `consistency_check.py` - valida integridade
4. Opcional: Carregar ultimo summary de `memory/summaries/` se data > 24h

### Se CONTEXT_PACK.md nao existir
```python
from workspace.agent.scripts.compiler import ContextCompiler
from config import config

compiler = ContextCompiler(config.WORKSPACE_DIR)
compiler.compile_and_save()
```

## Durante Execucao

### Se usuario solicitar acao complexa
1. Avaliar se requer tool calling (use schemas disponiveis)
2. Executar em loop maximo 5 iteracoes
3. Logar cada chamada em `actions.log`
4. Se erro: seguir "Debugging Hierarchy"

### Se rate limit excedido
1. Retornar: "⏱️ Muitas requisicoes. Aguarde. Restantes: X"
2. Logar em WARNING
3. Nao processar mensagem

### Se tool calling falhar
1. Tentar retry automatico (1 vez)
2. Se persistir, tentar execucao sem tools
3. Se ambos falharem, retornar erro amigavel
4. Logar detalhes para investigacao

## Debugging Hierarchy (Ordem de Resolucao)

### 1. Verificar Input
- Faltam parametros?
- Input vazio ou malformado?
- Encoding correto (UTF-8)?

### 2. Verificar CURRENT_STATE.md
- Existe contexto relevante?
- Tarefa anterior bloqueia atual?
- Variaveis de sessao necessarias?

### 3. Consultar memory/facts.md
- Existe conhecimento de dominio relevante?
- Decisoes anteriores sobre tema similar?

### 4. Verificar Ultimos Runs
- Logs em `runs/` mostram padrao similar?
- Erros recorrentes nas ultimas 10 execucoes?
- Solucoes aplicadas anteriormente?

### 5. Se Ainda Bloqueado
- Gerar resposta parcial com o que foi possivel
- Incluir: "Nao consegui completar [acao] devido a [razao]"
- Nunca retornar stack trace ao usuario

## Finalizacao de Sessao

### Pos-Execucao
1. Gravar output em `runs/YYYY-MM-DDTHHMMSSZ_run_XXX/output.md`
2. Atualizar `CURRENT_STATE.md` (via heartbeat)
3. Se execucao > 5 min ou decisao critica: atualizar `memory/decisions.md`
4. Registrar metricas em `runs/.../metrics.json`

### Manutencao Periodica
- `heartbeat.py` - executar a cada 60 segundos
- `consistency_check.py` - executar diariamente
- `compiler.py` - executar quando arquivos da Camada 1 mudarem

## Procedimentos de Emergencia

### Se agent entrar em loop infinito
1. Verificar max_iterations (deve ser 5)
2. Se persistir, retornar mensagem padrao: "Timeout na execucao"
3. Logar estado completo para debugging

### Se CONTEXT_PACK ficar corrompido
1. Deletar CONTEXT_PACK.md
2. Executar compiler.py para regenerar
3. Verificar se hash mudou

### Se CURRENT_STATE ficar inconsistente
1. Restaurar de backup (.bak se existir)
2. Ou reinicializar com valores padrao
3. Executar heartbeat.py para sincronizar

## Metricas Criticas

### Limiares de Alerta
- Erros > 10% nas ultimas 24h = ALERTA
- Uso de contexto > 80% = WARNING
- Rate limiting > 50% requisicoes = ALERTA
- Latencia media > 5s = WARNING

### Acao em Caso de Alerta
1. Notificar admin (se configurado)
2. Escalar log para nivel INFO
3. Escrever detalhes em `runs/alert_YYYYMMDD_HHMMSS.log`

## Checklist de Deploy

- [ ] IDENTITY.md atualizado com versao correta
- [ ] POLICIES.md revisado e aprovado
- [ ] STYLE.md reflete tom desejado
- [ ] compiler.py executado sem erros
- [ ] consistency_check.py passa (True)
- [ ] CURRENT_STATE.md inicializado
- [ ] Backup de runs/ anterior realizado
- [ ] Teste basico executado (mensagem simples)
