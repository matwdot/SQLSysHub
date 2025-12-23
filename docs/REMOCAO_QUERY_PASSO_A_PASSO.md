# Remoção de Query - Passo a Passo Direto

## ⚠️ IMPORTANTE
As queries estão definidas em **3 lugares diferentes**. Você deve remover de TODOS os 3 locais para que a remoção seja efetiva.

## Passo 1: Remover do Interface (operation_selector.py)

**Arquivo:** `refactored_sqltools/ui/components/operation_selector.py`

No método `load_operations()`, remova o bloco da operação:

```python
# REMOVER ESTE BLOCO COMPLETO:
"Nome da Query": {
    "description": "Descrição da query",
    "execute_sql": "SELECT * FROM TABELA"
},
```

## Passo 2: Comentar no Registry (predefined.py)

**Arquivo:** `refactored_sqltools/core/operations/predefined.py`

### 2.1 Comentar a classe da operação:
```python
# class NomeDaOperationClass(BaseOperation):
#     """Descrição da operação."""
#     
#     def __init__(self):
#         super().__init__(
#             name="Nome da Query",
#             description="Descrição"
#         )
#     
#     def get_sql(self, **params) -> str:
#         return "SELECT * FROM TABELA"
```

### 2.2 Comentar no registro de operações:
```python
def _register_operations(self):
    operations = [
        CancelarCupomOperation(),
        # NomeDaOperationClass(),  # ← Comentar esta linha
        OutraOperation(),
    ]
```

## Passo 3: Remover das Importações (__init__.py)

**Arquivo:** `refactored_sqltools/core/operations/__init__.py`

### 3.1 Comentar na importação:
```python
from .predefined import (
    CancelarCupomOperation,
    # NomeDaOperationClass,  # ← Comentar esta linha
    OutraOperation,
)
```

### 3.2 Comentar no __all__:
```python
__all__ = [
    'BaseOperation',
    'CancelarCupomOperation',
    # 'NomeDaOperationClass',  # ← Comentar esta linha
    'OutraOperation',
]
```

## Passo 4: Verificar Remoção

Execute este teste para confirmar:

```python
from refactored_sqltools.core.operations.predefined import operation_registry

# Listar operações disponíveis
operations = operation_registry.list_operations()
print("Operações disponíveis:", list(operations.keys()))

# Verificar se a operação foi removida
try:
    operation_registry.get_operation("Nome da Query Removida")
    print("❌ ERRO: Query ainda existe!")
except KeyError:
    print("✅ Query removida com sucesso!")
```

## Passo 5: Limpar Cache (Opcional)

Se a query ainda aparecer, limpe o cache Python:

```bash
# Windows
Remove-Item -Path "refactored_sqltools\__pycache__" -Recurse -Force

# Linux/Mac  
rm -rf refactored_sqltools/__pycache__
```

## ✅ Checklist de Verificação

- [ ] Removido de `operation_selector.py` (método `load_operations`)
- [ ] Comentado classe em `predefined.py`
- [ ] Comentado registro em `predefined.py` (método `_register_operations`)
- [ ] Comentado importação em `__init__.py`
- [ ] Comentado no `__all__` em `__init__.py`
- [ ] Testado que a query não aparece mais
- [ ] Sistema inicia sem erros

## 🚨 Erros Comuns

### "cannot import name 'NomeOperation'"
**Causa:** Não removeu das importações no `__init__.py`
**Solução:** Comente a importação no arquivo `__init__.py`

### Query ainda aparece na interface
**Causa:** Não removeu do `operation_selector.py`
**Solução:** Remova o bloco completo da query no método `load_operations()`

### Sistema não carrega operações
**Causa:** Erro de sintaxe nos arquivos editados
**Solução:** Verifique vírgulas, parênteses e indentação

## 📝 Exemplo Completo

Para remover "Consultar Transações":

### operation_selector.py
```python
# REMOVER:
"Consultar Transações": {
    "description": "Consulta as transações na tabela TRANSACAO",
    "execute_sql": "SELECT * FROM TRANSACAO"
},
```

### predefined.py
```python
# COMENTAR:
# class ConsultarTransacoesOperation(BaseOperation):
#     def __init__(self):
#         super().__init__(name="Consultar Transações", ...)

# E COMENTAR NO REGISTRO:
# ConsultarTransacoesOperation(),
```

### __init__.py
```python
# COMENTAR:
# ConsultarTransacoesOperation,

# E NO __all__:
# 'ConsultarTransacoesOperation',
```

---

**💡 Dica:** Sempre faça backup antes de remover queries importantes!