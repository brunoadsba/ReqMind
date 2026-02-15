# 📋 Plano de Implementação - Correções da Auditoria

**Data:** 08 de Fevereiro de 2026  
**Versão:** 1.0  
**Status:** 🟡 Aguardando Aprovação  
**Responsável:** Equipe de Desenvolvimento - ReqMind  

---

## 🎯 Visão Geral

Este documento apresenta o plano detalhado para implementação das correções identificadas na auditoria de segurança realizada em 08/02/2026. O plano está organizado em **3 fases** que devem ser executadas sequencialmente para garantir a estabilidade e segurança do sistema.

### Objetivos

- 🛡️ Eliminar vulnerabilidades de segurança críticas
- 🔧 Corrigir problemas de arquitetura e qualidade de código
- 📈 Melhorar a manutenibilidade do projeto
- ✅ Estabelecer padrões de qualidade para desenvolvimento futuro

---

## 📊 Resumo das Correções

| Fase | Prioridade | Quantidade | Estimativa |
|------|------------|------------|------------|
| Fase 1 | 🔴 Alta | 3 | 1-2 dias |
| Fase 2 | 🟡 Média | 3 | 2-3 dias |
| Fase 3 | 🟢 Baixa | 4+ | 2-3 dias |
| **Total** | - | **10+** | **5-8 dias** |

---

## 🚀 Fase 1: Correções Críticas de Segurança

**Prioridade:** 🔴 ALTA  
**Prazo:** 24-48 horas  
**Bloqueante:** Sim (deve ser concluída antes das outras fases)

### Tarefa 1.1: Remover Duplicação de Logger

**Arquivo:** [`src/workspace/core/agent.py`](src/workspace/core/agent.py:30)  
**Linha:** 30  
**Responsável:** Dev Backend  

#### Descrição
Remover a instância duplicada do logger na classe `Agent`.

#### Passos
1. [ ] Identificar todas as referências ao logger duplicado
2. [ ] Consolidar em uma única instância
3. [ ] Atualizar todas as chamadas de log no arquivo
4. [ ] Executar testes para verificar funcionamento

#### Código Esperado
```python
# Antes (problemático)
class Agent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)  # Linha 30
        # ... outro código ...
        self.logger = logging.getLogger(__name__)  # Duplicado!

# Depois (corrigido)
class Agent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)  # Única instância
```

#### Critérios de Aceitação
- [ ] Não há mais duplicação de logger
- [ ] Logs funcionam corretamente
- [ ] Testes passam sem erros

---

### Tarefa 1.2: Corrigir Vulnerabilidade de Command Injection

**Arquivo:** [`src/workspace/tools/code_tools.py`](src/workspace/tools/code_tools.py:17)  
**Linha:** 17  
**Responsável:** Dev Backend Sênior  
**⚠️ CRÍTICO:** Esta é a vulnerabilidade mais grave identificada

#### Descrição
Remover `shell=True` das chamadas `subprocess` e implementar validação adequada de entrada.

#### Passos
1. [ ] Analisar todas as chamadas `subprocess` no arquivo
2. [ ] Refatorar para usar lista de argumentos em vez de string
3. [ ] Implementar whitelist de comandos permitidos
4. [ ] Adicionar validação de entrada rigorosa
5. [ ] Criar testes de segurança específicos

#### Código Esperado
```python
# Antes (vulnerável)
result = subprocess.run(command, shell=True, capture_output=True, text=True)

# Depois (seguro)
ALLOWED_COMMANDS = ['git', 'python', 'pip', 'pytest']

def execute_command(command_args: list[str]) -> subprocess.CompletedProcess:
    """Execute command with security validations."""
    if not command_args:
        raise ValueError("Command cannot be empty")
    
    cmd = command_args[0]
    if cmd not in ALLOWED_COMMANDS:
        raise PermissionError(f"Command '{cmd}' not allowed")
    
    # Usar lista de argumentos, nunca shell=True
    result = subprocess.run(
        command_args,
        shell=False,  # ✅ Seguro
        capture_output=True,
        text=True,
        timeout=30  # Prevenir execuções longas
    )
    return result
```

#### Critérios de Aceitação
- [ ] `shell=True` completamente removido
- [ ] Validação de entrada implementada
- [ ] Whitelist de comandos ativo
- [ ] Testes de injeção de comando passam
- [ ] Code review aprovado por 2 desenvolvedores

---

### Tarefa 1.3: Corrigir Tipagem Inconsistente

**Arquivo:** [`src/workspace/core/agent.py`](src/workspace/core/agent.py:224)  
**Linhas:** 224 e 666  
**Responsável:** Dev Backend

#### Descrição
Corrigir a inconsistência de tipos na variável `tools_used`.

#### Passos
1. [ ] Identificar todas as ocorrências de `tools_used`
2. [ ] Definir tipo consistente (recomendado: `list[str]`)
3. [ ] Atualizar inicialização e todas as referências
4. [ ] Adicionar type hints apropriados
5. [ ] Executar mypy para validação de tipos

#### Código Esperado
```python
# Antes (inconsistente)
# Linha 224
tools_used: int = 0

# Linha 666
tools_used.append(tool_name)  # ❌ TypeError

# Depois (consistente)
# Linha 224
tools_used: list[str] = []  # ✅ Lista vazia

# Linha 666
tools_used.append(tool_name)  # ✅ Funciona corretamente
```

#### Critérios de Aceitação
- [ ] Tipo consistente em todas as ocorrências
- [ ] mypy passa sem erros
- [ ] Testes unitários passam
- [ ] Nenhum erro de tipo em runtime

---

## 🔄 Fase 2: Melhorias de Qualidade e Performance

**Prioridade:** 🟡 MÉDIA  
**Prazo:** 3-5 dias  
**Dependência:** Fase 1 concluída

### Tarefa 2.1: Otimizar Import de Regex

**Arquivo:** [`src/workspace/core/agent.py`](src/workspace/core/agent.py:514)  
**Linha:** 514  
**Responsável:** Dev Backend

#### Descrição
Mover import de `re` para o topo do arquivo, fora de loops.

#### Passos
1. [ ] Localizar import dentro do loop
2. [ ] Mover para topo do arquivo
3. [ ] Compilar padrões regex uma única vez
4. [ ] Medir performance antes/depois

#### Código Esperado
```python
# Antes (ineficiente)
for item in items:
    import re  # ❌ Import dentro do loop
    pattern = re.compile(r'...')
    match = pattern.match(item)

# Depois (otimizado)
import re  # ✅ Topo do arquivo

# Compilar uma única vez
PATTERN = re.compile(r'...')

for item in items:
    match = PATTERN.match(item)  # ✅ Reutiliza pattern compilado
```

#### Critérios de Aceitação
- [ ] Import removido do loop
- [ ] Pattern compilado globalmente
- [ ] Performance melhorada (medir com timeit)

---

### Tarefa 2.2: Externalizar User ID Hardcoded

**Arquivo:** [`src/workspace/tools/reminder_notifier.py`](src/workspace/tools/reminder_notifier.py:26)  
**Linha:** 26  
**Responsável:** Dev Backend

#### Descrição
Mover ID de usuário hardcoded para variável de ambiente ou configuração.

#### Passos
1. [ ] Adicionar variável ao `.env.example`
2. [ ] Criar configuração em `settings.py`
3. [ ] Atualizar referência no código
4. [ ] Documentar nova variável

#### Código Esperado
```python
# .env.example
DEFAULT_USER_ID=123456789

# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_USER_ID = int(os.getenv('DEFAULT_USER_ID', '0'))

# reminder_notifier.py
from config.settings import DEFAULT_USER_ID

# Uso
user_id = DEFAULT_USER_ID
```

#### Critérios de Aceitação
- [ ] Variável em `.env.example`
- [ ] Configuração centralizada
- [ ] Valor padrão seguro definido
- [ ] Documentação atualizada

---

### Tarefa 2.3: Externalizar Path Hardcoded

**Arquivo:** [`src/workspace/tools/code_tools.py`](src/workspace/tools/code_tools.py:8)  
**Linha:** 8  
**Responsável:** Dev Backend

#### Descrição
Mover path hardcoded para configuração dinâmica.

#### Passos
1. [ ] Identificar todos os paths hardcoded
2. [ ] Criar função utilitária para paths
3. [ ] Usar paths relativos ou variáveis de ambiente
4. [ ] Garantir compatibilidade com Docker

#### Código Esperado
```python
# Antes
WORKSPACE_DIR = "/home/user/workspace"  # Hardcoded

# Depois
import os
from pathlib import Path

# Usar path relativo ao projeto
WORKSPACE_DIR = Path(__file__).parent.parent.parent / "workspace"

# Ou via variável de ambiente
WORKSPACE_DIR = Path(os.getenv('WORKSPACE_DIR', './workspace'))
```

#### Critérios de Aceitação
- [ ] Nenhum path hardcoded no código
- [ ] Funciona em diferentes ambientes
- [ ] Compatível com Docker
- [ ] Testes passam em CI/CD

---

## ✨ Fase 3: Ajustes Finos e Padronização

**Prioridade:** 🟢 BAIXA  
**Prazo:** 2-3 dias  
**Dependência:** Fases 1 e 2 concluídas

### Tarefa 3.1: Limpar Imports Não Utilizados

**Arquivos:** Múltiplos  
**Responsável:** Dev Backend

#### Passos
1. [ ] Executar `autoflake` ou similar para identificar imports não usados
2. [ ] Remover imports identificados
3. [ ] Verificar que código ainda funciona
4. [ ] Adicionar verificação em pre-commit hook

#### Comandos
```bash
# Identificar imports não usados
autoflake --remove-all-unused-imports --recursive src/

# Ou com ruff
ruff check --select F401 src/
```

#### Critérios de Aceitação
- [ ] Nenhum import não utilizado
- [ ] Testes passam
- [ ] Pre-commit hook configurado

---

### Tarefa 3.2: Completar Docstrings

**Arquivos:** Múltiplos  
**Responsável:** Dev Backend

#### Padrão a Seguir (Google Style)
```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed, explaining the purpose
    and any important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When input is invalid.
        PermissionError: When access is denied.

    Example:
        >>> function_name("test", 42)
        True
    """
```

#### Critérios de Aceitação
- [ ] Todas as funções públicas documentadas
- [ ] Todas as classes documentadas
- [ ] Padrão consistente em todo o projeto

---

### Tarefa 3.3: Remover Código Comentado Morto

**Arquivos:** Múltiplos  
**Responsável:** Dev Backend

#### Passos
1. [ ] Buscar por código comentado no projeto
2. [ ] Verificar se está versionado no Git
3. [ ] Remover código morto
4. [ ] Commit separado para facilitar rollback

#### Critérios de Aceitação
- [ ] Nenhum código comentado desnecessário
- [ ] Histórico preservado no Git
- [ ] Código mais limpo e legível

---

### Tarefa 3.4: Padronizar Idioma do Código

**Arquivos:** Múltiplos  
**Responsável:** Dev Backend

#### Convenção a Adotar
- **Código:** Inglês (variáveis, funções, classes)
- **Documentação:** Português (README, docstrings, comentários)
- **Commits:** Português (ou seguir padrão do projeto)

#### Exemplo
```python
# Antes (misturado)
def processar_mensagem(user_id: int) -> str:
    """Processa a mensagem do usuário."""
    resultado = calculate_result(user_id)
    return resultado

# Depois (padronizado)
def process_message(user_id: int) -> str:
    """Processa a mensagem do usuário.
    
    Args:
        user_id: ID do usuário no Telegram.
        
    Returns:
        Resultado do processamento.
    """
    result = calculate_result(user_id)
    return result
```

#### Critérios de Aceitação
- [ ] Guia de estilo documentado
- [ ] Código padronizado em inglês
- [ ] Documentação em português
- [ ] Revisão de código completa

---

## ✅ Critérios de Aceitação Gerais

### Para Cada Fase

- [ ] Todas as tarefas concluídas
- [ ] Code review aprovado
- [ ] Testes unitários passando (>80% cobertura)
- [ ] Testes de integração passando
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado

### Critérios Finais

- [ ] Auditoria de segurança re-executada sem vulnerabilidades críticas
- [ ] mypy passa sem erros de tipagem
- [ ] ruff/flake8 passa sem warnings
- [ ] Pipeline de CI/CD verde
- [ ] Deploy em staging validado

---

## 📅 Cronograma Sugerido

| Semana | Fase | Atividades | Responsável |
|--------|------|------------|-------------|
| **Semana 1** | Fase 1 | Correções críticas de segurança | Dev Backend |
| | | - Tarefa 1.1: Logger | |
| | | - Tarefa 1.2: Command Injection | |
| | | - Tarefa 1.3: Tipagem | |
| **Semana 2** | Fase 2 | Melhorias de qualidade | Dev Backend |
| | | - Tarefa 2.1: Regex | |
| | | - Tarefa 2.2: User ID | |
| | | - Tarefa 2.3: Path | |
| **Semana 3** | Fase 3 | Ajustes finos | Dev Backend |
| | | - Tarefa 3.1: Imports | |
| | | - Tarefa 3.2: Docstrings | |
| | | - Tarefa 3.3: Código morto | |
| | | - Tarefa 3.4: Idioma | |
| | | Testes finais e deploy | |

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Quebra de funcionalidade existente | Média | Alto | Testes completos antes e depois; rollback planejado |
| Introdução de novos bugs | Média | Médio | Code review rigoroso; testes automatizados |
| Atraso no cronograma | Baixa | Médio | Priorização clara; escopo bem definido |
| Incompatibilidade com ambiente de produção | Baixa | Alto | Testes em ambiente de staging idêntico à produção |
| Perda de código útil ao remover código morto | Baixa | Baixo | Revisão cuidadosa; commits atômicos |

---

## 📚 Recursos Necessários

### Ferramentas
- Python 3.11+
- mypy (type checking)
- ruff (linting)
- pytest (testing)
- Git

### Ambientes
- Ambiente de desenvolvimento local
- Ambiente de staging
- Acesso ao ambiente de produção (apenas para deploy)

### Pessoas
- 1 Desenvolvedor Backend (principal)
- 1 Revisor de Código (code review)
- 1 QA (testes finais)

---

## 📖 Referências

- [Relatório de Auditoria](AUDITORIA_2026-02-08.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## 📝 Histórico de Revisões

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 08/02/2026 | Equipe ReqMind | Criação inicial do plano |

---

## ✅ Aprovações

| Papel | Nome | Assinatura | Data |
|-------|------|------------|------|
| Tech Lead | | | |
| Security Lead | | | |
| Product Owner | | | |

---

**Próximos Passos:**
1. Revisar e aprovar este plano
2. Agendar kickoff com a equipe
3. Iniciar Fase 1 imediatamente após aprovação

---

*Documento gerado em: 08/02/2026*  
*Última atualização: 08/02/2026*
