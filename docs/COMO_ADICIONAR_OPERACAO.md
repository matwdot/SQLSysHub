# Como Adicionar Nova Operação

Este guia explica como adicionar uma nova operação ao sistema de forma simples e organizada.

## Estrutura Atual

Cada operação agora tem seu próprio arquivo em `refactored_sqltools/core/operations/individual/`. Isso facilita:

- **Manutenção**: Cada operação é independente
- **Criação**: Basta criar um novo arquivo
- **Exclusão**: Basta remover o arquivo e a referência no registry
- **Testes**: Cada operação pode ter seus próprios testes

## Passo a Passo para Adicionar Nova Operação

### 1. Criar o Arquivo da Operação

Crie um novo arquivo em `refactored_sqltools/core/operations/individual/` com o nome da operação:

```python
# refactored_sqltools/core/operations/individual/minha_nova_operacao.py
"""
Minha Nova Operação

Descrição detalhada do que a operação faz.
"""

from ..base import BaseOperation, ValidationError


class MinhaNovaOperacao(BaseOperation):
    """Descrição breve da operação."""
    
    def __init__(self):
        super().__init__(
            name="Minha Nova Operação",
            description="Descrição detalhada da operação"
        )
    
    def validate_params(self, **params) -> bool:
        """Validar parâmetros se necessário."""
        # Exemplo para operação com parâmetros:
        # required_params = ['parametro1', 'parametro2']
        # self._validate_required_params(required_params, **params)
        return True
    
    def get_sql(self, **params) -> str:
        """Gerar o SQL da operação."""
        return "SELECT * FROM TABELA"
    
    def get_check_sql(self) -> str:
        """SQL para verificação (opcional)."""
        return "SELECT COUNT(*) FROM TABELA"
```

### 2. Registrar a Operação

Edite `refactored_sqltools/core/operations/registry.py`:

```python
# Adicionar o import
from .individual.minha_nova_operacao import MinhaNovaOperacao

# Na classe OperationRegistry, método _register_operations():
def _register_operations(self):
    """Register all predefined operations."""
    operations = [
        CancelarCupomOperation(),
        ApagarCertificadoOperation(),
        # ... outras operações ...
        MinhaNovaOperacao(),  # <- Adicionar aqui
    ]
    
    for operation in operations:
        self._operations[operation.name] = operation
```

### 3. Definir Tipo e Sessão

Ainda no `registry.py`, adicione a operação aos tipos e sessões apropriados:

```python
self._operation_types = {
    "PDV": [
        "Cancelar Cupom",
        # ...
    ],
    "Server": [
        "Limpar Tabelas do Fisco",
        # ...
        "Minha Nova Operação",  # <- Adicionar ao tipo apropriado
    ],
    "Ambos": [
        "Apagar Certificado"
    ]
}

self._sessions = {
    "SysPDV PDV": [
        # ...
    ],
    "SysPDV Server": [
        # ...
        "Minha Nova Operação",  # <- Adicionar à sessão apropriada
    ],
    "Outros": [
        # ...
    ]
}
```

### 4. Configurar Parâmetros (se necessário)

Se a operação precisar de parâmetros, adicione no método `get_operation_parameters()`:

```python
def get_operation_parameters(self, name: str) -> Dict[str, Any]:
    parameter_configs = {
        # ... outras operações ...
        "Minha Nova Operação": {
            "parametro1": {
                "type": "text",
                "label": "Parâmetro 1",
                "placeholder": "Digite o valor"
            },
            "parametro2": {
                "type": "date",
                "label": "Data",
                "default": "today"
            }
        }
    }
    
    return parameter_configs.get(name, {})
```

### 5. Atualizar o __init__.py (opcional)

Se quiser que a operação seja importável diretamente, adicione em `refactored_sqltools/core/operations/__init__.py`:

```python
from .individual.minha_nova_operacao import MinhaNovaOperacao

__all__ = [
    # ... outras operações ...
    'MinhaNovaOperacao'
]
```

### 6. Criar Testes

Crie testes para a nova operação:

```python
# tests/unit/test_minha_nova_operacao.py
import pytest
from refactored_sqltools.core.operations.individual.minha_nova_operacao import MinhaNovaOperacao


class TestMinhaNovaOperacao:
    
    def test_operation_initialization(self):
        """Test operation initialization."""
        operation = MinhaNovaOperacao()
        assert operation.name == "Minha Nova Operação"
        assert "Descrição detalhada" in operation.description
    
    def test_sql_generation(self):
        """Test SQL generation."""
        operation = MinhaNovaOperacao()
        sql = operation.get_sql()
        assert "SELECT" in sql
        assert "TABELA" in sql
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        operation = MinhaNovaOperacao()
        # Teste com parâmetros válidos
        assert operation.validate_params() == True
```

### 7. Testar a Integração

Execute os testes para verificar se tudo está funcionando:

```bash
# Testar se a operação foi registrada
python -c "from refactored_sqltools.core.operations.registry import operation_registry; print('Minha Nova Operação' in operation_registry.get_operation_names())"

# Executar testes unitários
python -m pytest tests/unit/test_minha_nova_operacao.py -v

# Executar testes de integração
python -m pytest tests/integration/test_core_functionality.py::TestCoreFunctionality::test_operation_registry_functionality -v
```

## Tipos de Parâmetros Suportados

### Texto
```python
"parametro": {
    "type": "text",
    "label": "Nome do Parâmetro",
    "placeholder": "Texto de exemplo",
    "default": "valor_padrao"
}
```

### Data
```python
"data_param": {
    "type": "date",
    "label": "Data",
    "default": "today"  # ou "month_ago"
}
```

### Número
```python
"numero_param": {
    "type": "text",  # Validado como número na operação
    "label": "Número",
    "placeholder": "Ex: 100",
    "default": "1"
}
```

## Validações Disponíveis

### Parâmetros Obrigatórios
```python
def validate_params(self, **params) -> bool:
    required_params = ['param1', 'param2']
    self._validate_required_params(required_params, **params)
    return True
```

### Intervalo de Datas
```python
def validate_params(self, **params) -> bool:
    self._validate_date_range(params['data_inicio'], params['data_fim'])
    return True
```

### Validação Customizada
```python
def validate_params(self, **params) -> bool:
    valor = params.get('valor')
    if valor and int(valor) <= 0:
        raise ValidationError("Valor deve ser maior que zero")
    return True
```

## Exemplo Completo

Veja os arquivos existentes em `refactored_sqltools/core/operations/individual/` para exemplos completos de operações com e sem parâmetros.

## Vantagens da Nova Estrutura

1. **Simplicidade**: Cada operação em seu próprio arquivo
2. **Manutenibilidade**: Fácil de encontrar e modificar operações
3. **Testabilidade**: Cada operação pode ter testes específicos
4. **Escalabilidade**: Adicionar novas operações não afeta as existentes
5. **Organização**: Código mais limpo e organizado