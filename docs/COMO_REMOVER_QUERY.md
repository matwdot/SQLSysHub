# Como Remover uma Query do SQL SysHub

Este documento fornece um guia completo e seguro para remover uma query/operação existente do sistema SQL SysHub.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Antes de Remover](#antes-de-remover)
3. [Passo a Passo](#passo-a-passo)
4. [Verificações de Segurança](#verificações-de-segurança)
5. [Alternativas à Remoção](#alternativas-à-remoção)
6. [Backup e Recuperação](#backup-e-recuperação)
7. [Testando a Remoção](#testando-a-remoção)
8. [Troubleshooting](#troubleshooting)

## Visão Geral

⚠️ **ATENÇÃO**: Remover uma operação é uma ação **irreversível** que pode afetar:
- Usuários que dependem da operação
- Scripts automatizados
- Relatórios e processos de negócio
- Integrações com outros sistemas

**Sempre considere alternativas antes de remover completamente uma operação.**

## Antes de Remover

### 1. 🔍 Análise de Impacto

Antes de remover qualquer operação, faça uma análise completa:

```bash
# 1. Verificar se a operação está sendo usada
grep -r "Nome da Operação" . --include="*.py" --include="*.md" --include="*.txt"

# 2. Verificar logs de uso (se disponível)
grep "Nome da Operação" logs/*.log

# 3. Verificar testes que podem depender da operação
grep -r "NomeDaOperationClass" tests/
```

### 2. 📊 Checklist de Verificação

- [ ] **Documentação**: A operação está documentada? Há dependências?
- [ ] **Usuários**: Alguém usa esta operação regularmente?
- [ ] **Automação**: Existe algum script que chama esta operação?
- [ ] **Testes**: Há testes que dependem desta operação?
- [ ] **Dados**: A remoção pode causar perda de dados?
- [ ] **Alternativas**: Existe uma operação equivalente?

### 3. 🗣️ Comunicação

Se a operação é usada por outros:
1. **Notifique** os usuários com antecedência
2. **Documente** o motivo da remoção
3. **Forneça** alternativas quando possível
4. **Estabeleça** um cronograma de remoção

## Passo a Passo

### Método 1: Remoção Completa (Permanente)

#### 1. 🗑️ Remover do Registry

Edite `refactored_sqltools/core/operations/predefined.py`:

```python
def _register_operations(self):
    """Register all predefined operations."""
    operations = [
        CancelarCupomOperation(),
        ApagarCertificadoOperation(),
        CorrigirErroEquipamentoOperation(),
        # OperacaoParaRemover(),  # ← Comente ou remova esta linha
        LimparTabelasFiscoOperation(),
        ConsultarTransacoesOperation(),
        ConsultarProprioOperation(),
        ConsultarNCMInexistenteOperation(),
    ]
    
    for operation in operations:
        self._operations[operation.name] = operation
```

#### 2. 🗂️ Remover a Classe

No mesmo arquivo, remova ou comente a classe completa:

```python
# Remova ou comente todo este bloco
"""
class OperacaoParaRemover(BaseOperation):
    '''Operação que será removida.'''
    
    def __init__(self):
        super().__init__(
            name="Operação Para Remover",
            description="Esta operação será removida"
        )
    
    def get_sql(self, **params) -> str:
        return "SELECT * FROM TABELA"
"""
```

#### 3. 🧪 Remover Testes Relacionados

Remova ou atualize testes em `tests/`:

```python
# Em tests/unit/test_operations.py
"""
def test_operacao_para_remover():
    '''Teste da operação removida.'''
    # Remover este teste completamente
    pass
"""

# Em tests/integration/test_operations.py
"""
def test_operacao_para_remover_integration():
    '''Teste de integração da operação removida.'''
    # Remover este teste completamente
    pass
"""
```

### Método 2: Desabilitação Temporária (Reversível)

#### 1. 🚫 Desabilitar no Registry

```python
def _register_operations(self):
    """Register all predefined operations."""
    operations = [
        CancelarCupomOperation(),
        ApagarCertificadoOperation(),
        # Temporariamente desabilitada - Remover em versão futura
        # OperacaoParaRemover(),  # TODO: Remover em v3.0
        CorrigirErroEquipamentoOperation(),
        # ... outras operações
    ]
```

#### 2. 🏷️ Marcar como Deprecated

```python
class OperacaoParaRemover(BaseOperation):
    """
    Operação que será removida em versão futura.
    
    ⚠️ DEPRECATED: Esta operação será removida na versão 3.0.
    Use 'NovaOperacaoEquivalente' como alternativa.
    """
    
    def __init__(self):
        super().__init__(
            name="[DEPRECATED] Operação Para Remover",
            description="⚠️ DEPRECATED: Esta operação será removida. Use 'Nova Operação' como alternativa."
        )
    
    def get_sql(self, **params) -> str:
        # Adicionar warning nos logs
        import logging
        logging.warning("Operação 'Operação Para Remover' está deprecated e será removida na v3.0")
        
        return "SELECT * FROM TABELA"
```

### Método 3: Remoção Gradual (Recomendado)

#### Fase 1: Marcar como Deprecated (Versão N)
```python
class OperacaoAntiga(BaseOperation):
    """⚠️ DEPRECATED: Use NovaOperacao em seu lugar."""
    
    def __init__(self):
        super().__init__(
            name="[DEPRECATED] Operação Antiga",
            description="⚠️ Esta operação será removida na próxima versão. Use 'Nova Operação' como alternativa."
        )
```

#### Fase 2: Remover da Interface (Versão N+1)
```python
def _register_operations(self):
    operations = [
        # OperacaoAntiga(),  # Removida da interface, mas classe ainda existe
        NovaOperacao(),
        # ... outras operações
    ]
```

#### Fase 3: Remoção Completa (Versão N+2)
```python
# Remover completamente a classe OperacaoAntiga
```

## Verificações de Segurança

### 1. 🔒 Verificar Dependências

```python
# Script para verificar dependências
def verificar_dependencias_operacao(nome_operacao):
    """Verifica se algum código depende da operação."""
    
    import os
    import re
    
    dependencias = []
    
    # Verificar arquivos Python
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if nome_operacao in content:
                            dependencias.append(filepath)
                except:
                    pass
    
    return dependencias

# Uso
deps = verificar_dependencias_operacao("OperacaoParaRemover")
if deps:
    print("⚠️ Arquivos que referenciam a operação:")
    for dep in deps:
        print(f"  - {dep}")
else:
    print("✅ Nenhuma dependência encontrada")
```

### 2. 🧪 Executar Testes

```bash
# Executar todos os testes para verificar se nada quebrou
python -m pytest tests/ -v

# Executar testes específicos de operações
python -m pytest tests/unit/test_operations.py -v
python -m pytest tests/integration/test_operations.py -v
```

### 3. 🔍 Verificar Registry

```python
# Script para verificar se o registry está consistente
def verificar_registry():
    """Verifica se todas as operações registradas existem."""
    
    from refactored_sqltools.core.operations.predefined import operation_registry
    
    try:
        operations = operation_registry.list_operations()
        print(f"✅ Registry carregado com {len(operations)} operações:")
        
        for name in operations:
            try:
                op = operation_registry.get_operation(name)
                print(f"  ✅ {name}")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                
    except Exception as e:
        print(f"❌ Erro no registry: {e}")

# Executar verificação
verificar_registry()
```

## Alternativas à Remoção

### 1. 🔄 Refatoração

Em vez de remover, considere refatorar:

```python
# Antes - Operação antiga
class OperacaoAntiga(BaseOperation):
    def get_sql(self, **params) -> str:
        return "SELECT * FROM TABELA_ANTIGA"

# Depois - Operação atualizada
class OperacaoAtualizada(BaseOperation):
    """Versão atualizada da operação antiga com melhorias."""
    
    def __init__(self):
        super().__init__(
            name="Operação Atualizada",  # Novo nome
            description="Versão melhorada da operação anterior com novos recursos"
        )
    
    def get_sql(self, **params) -> str:
        return """
        SELECT 
            T.CAMPO1,
            T.CAMPO2,
            T.DATA_ATUALIZACAO
        FROM TABELA_NOVA T
        WHERE T.STATUS = 'A'
        ORDER BY T.DATA_ATUALIZACAO DESC
        """
```

### 2. 🔀 Redirecionamento

Redirecione para uma operação equivalente:

```python
class OperacaoAntiga(BaseOperation):
    """Redirecionamento para nova operação."""
    
    def __init__(self):
        super().__init__(
            name="Operação Antiga (Redirecionada)",
            description="Esta operação foi movida. Use 'Nova Operação' para a funcionalidade atualizada."
        )
    
    def get_sql(self, **params) -> str:
        # Redirecionar para nova operação
        from .predefined import NovaOperacao
        nova_op = NovaOperacao()
        return nova_op.get_sql(**params)
```

### 3. 🏷️ Categorização

Organize operações em categorias:

```python
class OperacaoEspecializada(BaseOperation):
    """Operação para casos específicos."""
    
    def __init__(self):
        super().__init__(
            name="[AVANÇADO] Operação Especializada",
            description="Operação para usuários avançados. Use com cuidado."
        )
```

## Backup e Recuperação

### 1. 💾 Criar Backup

Antes de remover, sempre faça backup:

```bash
# Backup do arquivo de operações
cp refactored_sqltools/core/operations/predefined.py \
   refactored_sqltools/core/operations/predefined.py.backup.$(date +%Y%m%d)

# Backup dos testes
cp -r tests/ tests.backup.$(date +%Y%m%d)/

# Backup da documentação
cp -r docs/ docs.backup.$(date +%Y%m%d)/
```

### 2. 📝 Documentar Remoção

Crie um registro da remoção:

```markdown
# CHANGELOG.md

## [Versão 2.1.0] - 2024-12-22

### Removido
- **OperacaoParaRemover**: Removida devido a [motivo]
  - **Alternativa**: Use `NovaOperacao` para funcionalidade similar
  - **Migração**: [instruções de migração]
  - **Backup**: Código disponível em `backup/operacao_removida.py`
```

### 3. 🔄 Script de Recuperação

```python
# scripts/recuperar_operacao.py
"""
Script para recuperar operação removida.
Uso: python scripts/recuperar_operacao.py OperacaoParaRemover
"""

import sys
import shutil
from datetime import datetime

def recuperar_operacao(nome_operacao):
    """Recupera operação do backup."""
    
    backup_file = f"backup/predefined.py.backup.{datetime.now().strftime('%Y%m%d')}"
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup não encontrado: {backup_file}")
        return False
    
    print(f"🔄 Recuperando {nome_operacao} do backup...")
    
    # Implementar lógica de recuperação
    # ...
    
    print(f"✅ Operação {nome_operacao} recuperada com sucesso!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python recuperar_operacao.py <NomeOperacao>")
        sys.exit(1)
    
    recuperar_operacao(sys.argv[1])
```

## Testando a Remoção

### 1. 🧪 Testes Automatizados

```python
# tests/test_remocao.py
"""Testes para verificar remoção de operações."""

import pytest
from refactored_sqltools.core.operations.predefined import operation_registry

def test_operacao_removida_nao_existe():
    """Verifica se operação removida não está mais disponível."""
    
    operations = operation_registry.list_operations()
    
    # Verificar se operação foi realmente removida
    assert "Operação Para Remover" not in operations
    
    # Verificar se tentar acessar gera erro apropriado
    with pytest.raises(KeyError):
        operation_registry.get_operation("Operação Para Remover")

def test_operacoes_restantes_funcionam():
    """Verifica se operações restantes ainda funcionam."""
    
    operations = operation_registry.list_operations()
    
    # Verificar se operações essenciais ainda existem
    operacoes_essenciais = [
        "Cancelar Cupom",
        "Consultar Transações",
        "Consultar Proprio"
    ]
    
    for op_name in operacoes_essenciais:
        assert op_name in operations
        
        # Verificar se pode ser instanciada
        op = operation_registry.get_operation(op_name)
        assert op is not None
        assert hasattr(op, 'get_sql')

def test_registry_consistencia():
    """Verifica consistência do registry após remoção."""
    
    operations = operation_registry.list_operations()
    
    # Verificar se todas as operações listadas podem ser acessadas
    for op_name in operations:
        try:
            op = operation_registry.get_operation(op_name)
            assert op is not None
        except Exception as e:
            pytest.fail(f"Operação {op_name} não pode ser acessada: {e}")
```

### 2. 🖥️ Teste Manual

```bash
# 1. Executar aplicação
python run_sqltools.py

# 2. Verificar interface
# - Operação removida não deve aparecer na lista
# - Outras operações devem funcionar normalmente
# - Não deve haver erros de carregamento

# 3. Verificar logs
tail -f logs/application.log
# Não deve haver erros relacionados à operação removida
```

### 3. 📊 Checklist de Teste

- [ ] **Registry**: Operação não aparece na lista
- [ ] **Interface**: Operação não aparece no combo box
- [ ] **Testes**: Todos os testes passam
- [ ] **Logs**: Sem erros relacionados à remoção
- [ ] **Performance**: Sistema carrega normalmente
- [ ] **Funcionalidade**: Outras operações funcionam
- [ ] **Backup**: Backup foi criado corretamente

## Troubleshooting

### Problema: Erro ao carregar registry

**Sintoma:**
```
KeyError: 'OperacaoRemovida' not found
```

**Causa:** Referência à operação removida ainda existe no código

**Solução:**
```bash
# Encontrar todas as referências
grep -r "OperacaoRemovida" . --include="*.py"

# Remover ou comentar as referências encontradas
```

### Problema: Testes falhando

**Sintoma:**
```
AssertionError: Operação 'X' não encontrada
```

**Causa:** Testes ainda esperam a operação removida

**Solução:**
```python
# Atualizar ou remover testes que dependem da operação
def test_operacoes_disponiveis():
    operations = operation_registry.list_operations()
    
    # Remover operação da lista esperada
    expected_operations = [
        "Cancelar Cupom",
        # "Operacao Removida",  # ← Remover esta linha
        "Consultar Transações"
    ]
```

### Problema: Interface com erro

**Sintoma:** Interface não carrega ou mostra erro

**Causa:** Referência à operação removida na interface

**Solução:**
```python
# Verificar operation_selector.py
# Remover referências à operação removida
```

### Problema: Usuários reportam operação ausente

**Sintoma:** Usuários não encontram operação que usavam

**Solução:**
1. **Comunicar** a remoção e alternativas
2. **Documentar** no changelog
3. **Fornecer** script de migração se necessário
4. **Considerar** restaurar temporariamente se crítico

## 📚 Recursos Adicionais

### Documentação Relacionada
- [Como Adicionar uma Nova Query](COMO_ADICIONAR_NOVA_QUERY.md)
- [Arquitetura do Sistema](ARQUITETURA_SISTEMA.md)
- [Guia de Versionamento](VERSIONAMENTO.md)

### Scripts Úteis
- `scripts/backup_operacoes.py` - Backup automático
- `scripts/verificar_dependencias.py` - Análise de dependências
- `scripts/migrar_operacao.py` - Migração entre operações

### Boas Práticas
1. **Sempre** faça backup antes de remover
2. **Comunique** mudanças com antecedência
3. **Forneça** alternativas quando possível
4. **Documente** o processo de remoção
5. **Teste** thoroughly após remoção
6. **Monitore** por problemas pós-remoção

---

**⚠️ Lembrete**: A remoção de operações é uma ação séria que pode impactar usuários e sistemas. Sempre considere alternativas e siga o processo gradual quando possível.