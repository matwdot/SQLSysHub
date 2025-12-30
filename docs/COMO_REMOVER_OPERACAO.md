# Como Remover Operação

Este guia explica como remover uma operação existente do sistema de forma segura.

## Passo a Passo para Remover Operação

### 1. Identificar a Operação

Primeiro, identifique qual operação você quer remover:

```python
from refactored_sqltools.core.operations.registry import operation_registry

# Listar todas as operações
for name in operation_registry.get_operation_names():
    print(f"- {name}")
```

### 2. Remover do Registry

Edite `refactored_sqltools/core/operations/registry.py`:

```python
# Remover o import
# from .individual.operacao_a_remover import OperacaoARemover  # <- Comentar ou remover

# Na classe OperationRegistry, método _register_operations():
def _register_operations(self):
    """Register all predefined operations."""
    operations = [
        CancelarCupomOperation(),
        ApagarCertificadoOperation(),
        # OperacaoARemover(),  # <- Comentar ou remover
        # ... outras operações ...
    ]
```

### 3. Remover dos Tipos e Sessões

Ainda no `registry.py`, remova a operação dos tipos e sessões:

```python
self._operation_types = {
    "PDV": [
        "Cancelar Cupom",
        # "Operação A Remover",  # <- Remover
    ],
    "Server": [
        "Limpar Tabelas do Fisco",
        # "Operação A Remover",  # <- Remover
    ],
    "Ambos": [
        "Apagar Certificado"
    ]
}

self._sessions = {
    "SysPDV PDV": [
        # "Operação A Remover",  # <- Remover
    ],
    "SysPDV Server": [
        # "Operação A Remover",  # <- Remover
    ],
    "Outros": [
        # ...
    ]
}
```

### 4. Remover Configuração de Parâmetros

Se a operação tinha parâmetros, remova do método `get_operation_parameters()`:

```python
def get_operation_parameters(self, name: str) -> Dict[str, Any]:
    parameter_configs = {
        # "Operação A Remover": {  # <- Remover todo este bloco
        #     "parametro1": {
        #         "type": "text",
        #         "label": "Parâmetro 1"
        #     }
        # },
        # ... outras operações ...
    }
    
    return parameter_configs.get(name, {})
```

### 5. Remover do __init__.py

Se a operação estava no `__init__.py`, remova:

```python
# refactored_sqltools/core/operations/__init__.py

# Remover o import
# from .individual.operacao_a_remover import OperacaoARemover

__all__ = [
    # ... outras operações ...
    # 'OperacaoARemover'  # <- Remover
]
```

### 6. Remover o Arquivo da Operação

Agora você pode remover o arquivo da operação:

```bash
# No Windows
del refactored_sqltools\core\operations\individual\operacao_a_remover.py

# No Linux/Mac
rm refactored_sqltools/core/operations/individual/operacao_a_remover.py
```

### 7. Remover Testes Relacionados

Remova os testes específicos da operação:

```bash
# No Windows
del tests\unit\test_operacao_a_remover.py

# No Linux/Mac
rm tests/unit/test_operacao_a_remover.py
```

### 8. Verificar Remoção

Execute os testes para verificar se a remoção foi bem-sucedida:

```bash
# Verificar se a operação foi removida do registry
python -c "from refactored_sqltools.core.operations.registry import operation_registry; print('Operação A Remover' not in operation_registry.get_operation_names())"

# Executar testes de integração
python -m pytest tests/integration/test_core_functionality.py::TestCoreFunctionality::test_operation_registry_functionality -v
```

## Checklist de Remoção

- [ ] Remover import no `registry.py`
- [ ] Remover da lista de operações em `_register_operations()`
- [ ] Remover de `_operation_types`
- [ ] Remover de `_sessions`
- [ ] Remover configuração de parâmetros (se houver)
- [ ] Remover do `__init__.py` (se estiver lá)
- [ ] Remover arquivo da operação
- [ ] Remover testes relacionados
- [ ] Verificar que os testes passam

## Remoção Temporária vs Permanente

### Remoção Temporária
Para remover temporariamente (manter o código mas não disponibilizar):

```python
# Apenas comente as linhas no registry.py
# OperacaoARemover(),  # Temporariamente removida
```

### Remoção Permanente
Para remover permanentemente, siga todos os passos acima e delete os arquivos.

## Cuidados Importantes

1. **Backup**: Sempre faça backup antes de remover operações
2. **Dependências**: Verifique se outras partes do código dependem da operação
3. **Testes**: Execute todos os testes após a remoção
4. **Documentação**: Atualize a documentação se necessário

## Exemplo de Remoção Segura

```python
# Antes de remover, teste se a operação existe
from refactored_sqltools.core.operations.registry import operation_registry

try:
    operation = operation_registry.get_operation("Operação A Remover")
    print(f"Operação encontrada: {operation.description}")
    print("Proceda com a remoção seguindo os passos acima")
except KeyError:
    print("Operação já foi removida ou não existe")
```

## Recuperação de Operação Removida

Se você removeu uma operação por engano, pode recuperá-la:

1. Restaure o arquivo da operação do backup ou controle de versão
2. Siga os passos de "Como Adicionar Nova Operação"
3. Execute os testes para verificar se tudo está funcionando

## Vantagens da Nova Estrutura para Remoção

1. **Isolamento**: Cada operação é independente
2. **Simplicidade**: Remover um arquivo é mais simples que editar um arquivo grande
3. **Segurança**: Menos chance de quebrar outras operações
4. **Rastreabilidade**: Fácil de ver o que foi removido no controle de versão