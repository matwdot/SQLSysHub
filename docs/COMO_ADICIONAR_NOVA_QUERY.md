# Como Adicionar uma Nova Query ao SQL SysHub

Este documento fornece um guia completo e detalhado para adicionar uma nova query/operação ao sistema SQL SysHub.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Passo a Passo Detalhado](#passo-a-passo-detalhado)
4. [Exemplos Práticos](#exemplos-práticos)
5. [Adicionando Parâmetros](#adicionando-parâmetros)
6. [Testando a Nova Operação](#testando-a-nova-operação)
7. [Boas Práticas](#boas-práticas)
8. [Troubleshooting](#troubleshooting)

## Visão Geral

O sistema SQL SysHub utiliza um padrão de **Registry** para gerenciar operações predefinidas. Cada operação é uma classe que herda de `BaseOperation` e implementa a lógica específica para gerar e executar SQL.

### Benefícios desta Arquitetura:
- ✅ **Extensibilidade**: Fácil adição de novas operações
- ✅ **Manutenibilidade**: Código organizado e modular
- ✅ **Testabilidade**: Cada operação pode ser testada independentemente
- ✅ **Reutilização**: Operações podem ser reutilizadas em diferentes contextos

## Arquitetura do Sistema

```
refactored_sqltools/
├── core/
│   └── operations/
│       ├── base.py              # Classe base BaseOperation
│       └── predefined.py        # Operações predefinidas + Registry
├── ui/
│   └── components/
│       └── operation_selector.py # Interface para seleção
└── tests/
    ├── unit/
    └── integration/
```

### Fluxo de Execução:
1. **Registro**: Operação é registrada no `OperationRegistry`
2. **Seleção**: Usuário seleciona operação na interface
3. **Validação**: Parâmetros são validados (se necessário)
4. **Execução**: SQL é gerado e executado no banco
5. **Resultado**: Dados são exibidos na interface

## Passo a Passo Detalhado

### 1. 📝 Criar a Classe da Operação

Navegue até `refactored_sqltools/core/operations/predefined.py` e adicione uma nova classe:

```python
class MinhaNovaOperation(BaseOperation):
    """
    Descrição detalhada da minha nova operação.
    
    Esta operação realiza [descrever o que faz] e é útil para [contexto de uso].
    
    Parâmetros:
        param1 (str): Descrição do parâmetro 1
        param2 (int): Descrição do parâmetro 2
    
    Retorna:
        QueryResult com [descrever o que retorna]
    """
    
    def __init__(self):
        super().__init__(
            name="Nome da Operação",
            description="Descrição clara e concisa do que a operação faz"
        )
    
    def get_sql(self, **params) -> str:
        """
        Gera o SQL para esta operação.
        
        Args:
            **params: Parâmetros da operação
            
        Returns:
            str: SQL formatado para execução
        """
        return "SELECT * FROM minha_tabela"
    
    def validate_params(self, **params) -> bool:
        """
        Valida os parâmetros da operação.
        
        Args:
            **params: Parâmetros a serem validados
            
        Returns:
            bool: True se válidos
            
        Raises:
            ValidationError: Se parâmetros inválidos
        """
        # Implementar validação se necessário
        return True
    
    def get_check_sql(self) -> str:
        """
        SQL para verificar estado antes da operação (opcional).
        
        Returns:
            str: SQL de verificação
        """
        return "SELECT COUNT(*) FROM minha_tabela"
```

### 2. 🔗 Registrar a Operação

No mesmo arquivo, adicione sua operação à lista no método `_register_operations()`:

```python
def _register_operations(self):
    """Register all predefined operations."""
    operations = [
        CancelarCupomOperation(),
        ApagarCertificadoOperation(),
        CorrigirErroEquipamentoOperation(),
        LimparTabelasFiscoOperation(),
        ConsultarTransacoesOperation(),
        ConsultarProprioOperation(),
        ConsultarNCMInexistenteOperation(),
        MinhaNovaOperation(),  # ← Adicione aqui
    ]
    
    for operation in operations:
        self._operations[operation.name] = operation
```

### 3. 🎨 Atualizar Interface (Automático)

A interface é atualizada automaticamente! O sistema:
- ✅ Detecta automaticamente novas operações
- ✅ Adiciona ao combo box de seleção
- ✅ Exibe descrição quando selecionada
- ✅ Gerencia parâmetros dinamicamente

**Não é necessário modificar manualmente a interface!**

### 4. ✅ Verificar Integração

Execute o sistema para verificar se a operação aparece:

```bash
python run_sqltools.py
```

A nova operação deve aparecer na lista de operações disponíveis.

## Exemplos Práticos

### Exemplo 1: Query Simples (SELECT)

```python
class ConsultarUsuariosOperation(BaseOperation):
    """Consulta todos os usuários do sistema com informações básicas."""
    
    def __init__(self):
        super().__init__(
            name="Consultar Usuários",
            description="Lista todos os usuários cadastrados no sistema com código, nome, email e data de cadastro"
        )
    
    def get_sql(self, **params) -> str:
        return """
        SELECT 
            USUCOD AS CODIGO,
            USUNOM AS NOME,
            USUEML AS EMAIL,
            USUDAT AS DATA_CADASTRO,
            CASE USUSTS 
                WHEN 'A' THEN 'Ativo'
                WHEN 'I' THEN 'Inativo'
                ELSE 'Indefinido'
            END AS STATUS
        FROM USUARIO 
        WHERE USUNOM IS NOT NULL
        ORDER BY USUNOM
        """
    
    def get_check_sql(self) -> str:
        return "SELECT COUNT(*) AS TOTAL_USUARIOS FROM USUARIO"
```

### Exemplo 2: Query com Parâmetros e Validação

```python
class ConsultarVendasPeriodoOperation(BaseOperation):
    """Consulta vendas realizadas em um período específico."""
    
    def __init__(self):
        super().__init__(
            name="Consultar Vendas por Período",
            description="Consulta vendas realizadas entre duas datas específicas com detalhes do cliente e valores"
        )
    
    def validate_params(self, **params) -> bool:
        """Valida parâmetros de data."""
        required_params = ['data_inicio', 'data_fim']
        self._validate_required_params(required_params, **params)
        
        # Validação customizada
        from datetime import datetime
        try:
            data_inicio = datetime.strptime(params['data_inicio'], '%Y-%m-%d')
            data_fim = datetime.strptime(params['data_fim'], '%Y-%m-%d')
            
            if data_inicio > data_fim:
                raise ValidationError("Data de início deve ser anterior à data de fim")
                
            # Verificar se não é muito no passado (exemplo: máximo 5 anos)
            from datetime import timedelta
            cinco_anos_atras = datetime.now() - timedelta(days=5*365)
            if data_inicio < cinco_anos_atras:
                raise ValidationError("Data de início não pode ser superior a 5 anos no passado")
                
        except ValueError:
            raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")
        
        return True
    
    def get_sql(self, **params) -> str:
        data_inicio = params['data_inicio']
        data_fim = params['data_fim']
        
        return f"""
        SELECT 
            V.VENDAT AS DATA_VENDA,
            V.VENNUM AS NUMERO_VENDA,
            C.CLINOM AS CLIENTE,
            C.CLICPF AS CPF_CLIENTE,
            V.VENTOT AS VALOR_TOTAL,
            V.VENDSC AS DESCONTO,
            VEN.VENNOM AS VENDEDOR,
            CASE V.VENSTS
                WHEN 'A' THEN 'Aprovada'
                WHEN 'C' THEN 'Cancelada'
                WHEN 'P' THEN 'Pendente'
                ELSE 'Indefinido'
            END AS STATUS
        FROM VENDA V
        INNER JOIN CLIENTE C ON V.CLICOD = C.CLICOD
        LEFT JOIN VENDEDOR VEN ON V.VENCOD = VEN.VENCOD
        WHERE V.VENDAT BETWEEN '{data_inicio}' AND '{data_fim}'
          AND V.VENSTS IN ('A', 'P')  -- Apenas aprovadas e pendentes
        ORDER BY V.VENDAT DESC, V.VENNUM DESC
        """
    
    def get_check_sql(self) -> str:
        return """
        SELECT 
            MIN(VENDAT) AS PRIMEIRA_VENDA,
            MAX(VENDAT) AS ULTIMA_VENDA,
            COUNT(*) AS TOTAL_VENDAS
        FROM VENDA
        """
```

### Exemplo 3: Query de Atualização com Segurança

```python
class AtualizarStatusProdutoOperation(BaseOperation):
    """Atualiza status de produtos inativos para ativo com validações de segurança."""
    
    def __init__(self):
        super().__init__(
            name="Ativar Produtos Inativos",
            description="Ativa todos os produtos que estão com status inativo, exceto produtos descontinuados"
        )
    
    def get_sql(self, **params) -> str:
        return """
        UPDATE PRODUTO 
        SET PROSTA = 'A',
            PRODTA = CURRENT_DATE,
            PROUSR = 'SISTEMA'
        WHERE PROSTA = 'I' 
          AND PROTIP <> 'D'  -- Não ativar descontinuados
          AND PRODAT >= CURRENT_DATE - 365  -- Apenas produtos cadastrados no último ano
        """
    
    def get_check_sql(self) -> str:
        return """
        SELECT 
            COUNT(*) AS PRODUTOS_INATIVOS,
            COUNT(CASE WHEN PROTIP = 'D' THEN 1 END) AS DESCONTINUADOS,
            COUNT(CASE WHEN PRODAT < CURRENT_DATE - 365 THEN 1 END) AS ANTIGOS
        FROM PRODUTO 
        WHERE PROSTA = 'I'
        """
```

### Exemplo 4: Query Complexa com EXECUTE BLOCK

```python
class ManutencaoSistemaOperation(BaseOperation):
    """Executa rotina de manutenção completa do sistema."""
    
    def __init__(self):
        super().__init__(
            name="Manutenção do Sistema",
            description="Executa limpeza de dados temporários, reindexação e otimização do banco"
        )
    
    def validate_params(self, **params) -> bool:
        """Validação especial para operações de manutenção."""
        # Verificar se é horário adequado (exemplo: fora do horário comercial)
        from datetime import datetime
        agora = datetime.now()
        
        if 8 <= agora.hour <= 18:  # Horário comercial
            raise ValidationError(
                "Manutenção só pode ser executada fora do horário comercial (18h às 8h)"
            )
        
        return True
    
    def get_sql(self, **params) -> str:
        return """
        EXECUTE BLOCK AS 
        DECLARE VARIABLE dias_limite INTEGER;
        DECLARE VARIABLE registros_removidos INTEGER;
        BEGIN
          dias_limite = 30;
          registros_removidos = 0;
          
          -- 1. Remove logs antigos
          DELETE FROM LOG_SISTEMA 
          WHERE LOGDAT < CURRENT_DATE - :dias_limite;
          registros_removidos = registros_removidos + ROW_COUNT;
          
          -- 2. Remove sessões expiradas
          DELETE FROM SESSAO_USUARIO 
          WHERE SESDAT < CURRENT_DATE - 1;
          registros_removidos = registros_removidos + ROW_COUNT;
          
          -- 3. Remove arquivos temporários
          DELETE FROM ARQUIVO_TEMP 
          WHERE ARQDAT < CURRENT_DATE - 7;
          registros_removidos = registros_removidos + ROW_COUNT;
          
          -- 4. Atualiza estatísticas
          UPDATE SISTEMA_CONFIG 
          SET CFGVAL = CAST(:registros_removidos AS VARCHAR(20))
          WHERE CFGNOM = 'ULTIMA_MANUTENCAO_REGISTROS';
          
          UPDATE SISTEMA_CONFIG 
          SET CFGVAL = CAST(CURRENT_TIMESTAMP AS VARCHAR(30))
          WHERE CFGNOM = 'ULTIMA_MANUTENCAO_DATA';
          
          -- 5. Commit das alterações
          COMMIT;
        END
        """
    
    def get_check_sql(self) -> str:
        return """
        SELECT 
            (SELECT COUNT(*) FROM LOG_SISTEMA WHERE LOGDAT < CURRENT_DATE - 30) AS LOGS_ANTIGOS,
            (SELECT COUNT(*) FROM SESSAO_USUARIO WHERE SESDAT < CURRENT_DATE - 1) AS SESSOES_EXPIRADAS,
            (SELECT COUNT(*) FROM ARQUIVO_TEMP WHERE ARQDAT < CURRENT_DATE - 7) AS ARQUIVOS_TEMP,
            (SELECT CFGVAL FROM SISTEMA_CONFIG WHERE CFGNOM = 'ULTIMA_MANUTENCAO_DATA') AS ULTIMA_MANUTENCAO
        FROM RDB$DATABASE
        """
```

## Adicionando Parâmetros

### Parâmetros Automáticos

O sistema detecta automaticamente alguns tipos de parâmetros:

#### 1. Parâmetros de Data
Se sua operação usar `data_inicio` e `data_fim`, campos de data aparecerão automaticamente:

```python
def validate_params(self, **params) -> bool:
    required_params = ['data_inicio', 'data_fim']  # ← Detectado automaticamente
    self._validate_required_params(required_params, **params)
    return True
```

#### 2. Parâmetros Customizados
Para parâmetros específicos, override o método `get_required_params()`:

```python
class ConsultarProdutoPorCodigoOperation(BaseOperation):
    """Consulta produto por código específico."""
    
    def get_required_params(self) -> list:
        """Define parâmetros necessários para esta operação."""
        return [
            {
                'name': 'codigo_produto',
                'type': 'string',
                'label': 'Código do Produto',
                'placeholder': 'Digite o código do produto',
                'required': True
            },
            {
                'name': 'incluir_inativos',
                'type': 'boolean',
                'label': 'Incluir produtos inativos',
                'default': False,
                'required': False
            }
        ]
    
    def validate_params(self, **params) -> bool:
        codigo = params.get('codigo_produto', '').strip()
        if not codigo:
            raise ValidationError("Código do produto é obrigatório")
        
        if len(codigo) > 20:
            raise ValidationError("Código do produto deve ter no máximo 20 caracteres")
        
        return True
    
    def get_sql(self, **params) -> str:
        codigo = params['codigo_produto']
        incluir_inativos = params.get('incluir_inativos', False)
        
        sql = f"""
        SELECT 
            PROCOD AS CODIGO,
            PRONOM AS NOME,
            PROVAL AS VALOR,
            PROEST AS ESTOQUE,
            PROSTA AS STATUS
        FROM PRODUTO 
        WHERE PROCOD = '{codigo}'
        """
        
        if not incluir_inativos:
            sql += " AND PROSTA = 'A'"
        
        return sql
```

## Testando a Nova Operação

### 1. 🧪 Teste Unitário

Crie um teste em `tests/unit/test_operations.py`:

```python
import pytest
from refactored_sqltools.core.operations.predefined import MinhaNovaOperation
from refactored_sqltools.utils.exceptions import ValidationError

class TestMinhaNovaOperation:
    """Testes para MinhaNovaOperation."""
    
    def test_operation_properties(self):
        """Testa propriedades básicas da operação."""
        operation = MinhaNovaOperation()
        
        assert operation.name == "Nome da Operação"
        assert "descrição" in operation.description.lower()
        assert operation.description is not None
        assert len(operation.description) > 10  # Descrição deve ser significativa
    
    def test_sql_generation(self):
        """Testa geração de SQL."""
        operation = MinhaNovaOperation()
        
        sql = operation.get_sql()
        assert sql is not None
        assert len(sql.strip()) > 0
        assert "SELECT" in sql.upper() or "UPDATE" in sql.upper() or "DELETE" in sql.upper()
    
    def test_parameter_validation_success(self):
        """Testa validação de parâmetros válidos."""
        operation = MinhaNovaOperation()
        
        # Teste com parâmetros válidos
        result = operation.validate_params(param1="valor1", param2=123)
        assert result is True
    
    def test_parameter_validation_failure(self):
        """Testa validação de parâmetros inválidos."""
        operation = MinhaNovaOperation()
        
        # Teste com parâmetros inválidos
        with pytest.raises(ValidationError):
            operation.validate_params(param_invalido="valor")
    
    def test_check_sql(self):
        """Testa SQL de verificação se implementado."""
        operation = MinhaNovaOperation()
        
        if hasattr(operation, 'get_check_sql'):
            check_sql = operation.get_check_sql()
            assert check_sql is not None
            assert "SELECT" in check_sql.upper()
```

### 2. 🔗 Teste de Integração

Adicione um teste em `tests/integration/test_operations.py`:

```python
from unittest.mock import Mock
from refactored_sqltools.core.operations.predefined import MinhaNovaOperation
from refactored_sqltools.core.database.drivers.base import QueryResult

def test_minha_nova_operation_integration():
    """Testa integração completa da MinhaNovaOperation."""
    
    # Setup
    operation = MinhaNovaOperation()
    mock_db_manager = Mock()
    
    # Mock resultado bem-sucedido
    mock_result = QueryResult(
        success=True,
        message="Query executada com sucesso",
        columns=["CODIGO", "NOME", "EMAIL"],
        data=[
            ("001", "João Silva", "joao@email.com"),
            ("002", "Maria Santos", "maria@email.com")
        ]
    )
    mock_db_manager.execute_query.return_value = mock_result
    
    # Execução
    sql = operation.get_sql()
    result = mock_db_manager.execute_query(sql)
    
    # Verificações
    assert result.success is True
    assert "sucesso" in result.message.lower()
    assert len(result.columns) == 3
    assert len(result.data) == 2
    assert result.data[0][1] == "João Silva"
    
    # Verificar se SQL foi chamado corretamente
    mock_db_manager.execute_query.assert_called_once_with(sql)

def test_operation_registry_integration():
    """Testa se a operação foi registrada corretamente."""
    from refactored_sqltools.core.operations.predefined import operation_registry
    
    # Verificar se a operação está no registry
    operations = operation_registry.list_operations()
    assert "Nome da Operação" in operations
    
    # Verificar se pode ser recuperada
    operation = operation_registry.get_operation("Nome da Operação")
    assert operation is not None
    assert isinstance(operation, MinhaNovaOperation)
```

### 3. 🖥️ Teste Manual

1. **Execute a aplicação:**
   ```bash
   python run_sqltools.py
   ```

2. **Teste o fluxo completo:**
   - ✅ Conecte-se a um banco de dados
   - ✅ Verifique se sua operação aparece na lista
   - ✅ Selecione a operação
   - ✅ Preencha parâmetros (se houver)
   - ✅ Execute e verifique os resultados
   - ✅ Teste cenários de erro

3. **Checklist de teste manual:**
   - [ ] Operação aparece na lista
   - [ ] Descrição é exibida corretamente
   - [ ] Parâmetros são solicitados (se aplicável)
   - [ ] Validação funciona (teste valores inválidos)
   - [ ] SQL é executado sem erros
   - [ ] Resultados são exibidos corretamente
   - [ ] Mensagens de erro são claras

## Boas Práticas

### 1. 📝 Nomenclatura e Documentação

```python
# ✅ BOM
class ConsultarVendasMensaisOperation(BaseOperation):
    """
    Consulta vendas agrupadas por mês com totalizadores.
    
    Esta operação gera um relatório mensal de vendas incluindo:
    - Total de vendas por mês
    - Valor total vendido
    - Ticket médio
    - Comparativo com mês anterior
    
    Útil para análises gerenciais e relatórios de performance.
    """

# ❌ RUIM
class Operation1(BaseOperation):
    """Faz consulta."""
```

### 2. 🔒 Validação Robusta

```python
# ✅ BOM
def validate_params(self, **params) -> bool:
    # Validar parâmetros obrigatórios
    required_params = ['data_inicio', 'data_fim']
    self._validate_required_params(required_params, **params)
    
    # Validações específicas
    data_inicio = params['data_inicio']
    data_fim = params['data_fim']
    
    # Validar formato
    try:
        datetime.strptime(data_inicio, '%Y-%m-%d')
        datetime.strptime(data_fim, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")
    
    # Validar lógica de negócio
    if data_inicio > data_fim:
        raise ValidationError("Data de início deve ser anterior à data de fim")
    
    return True

# ❌ RUIM
def validate_params(self, **params) -> bool:
    return True  # Sem validação
```

### 3. 🛡️ SQL Seguro

```python
# ✅ BOM - SQL parametrizado e seguro
def get_sql(self, **params) -> str:
    data_inicio = params['data_inicio']  # Já validado
    data_fim = params['data_fim']        # Já validado
    
    return f"""
    SELECT 
        V.VENDAT AS DATA_VENDA,
        V.VENNUM AS NUMERO_VENDA,
        V.VENTOT AS VALOR_TOTAL
    FROM VENDA V
    WHERE V.VENDAT BETWEEN '{data_inicio}' AND '{data_fim}'
      AND V.VENSTS = 'A'
    ORDER BY V.VENDAT DESC
    """

# ❌ RUIM - Vulnerável a SQL injection
def get_sql(self, **params) -> str:
    # Nunca faça isso sem validação!
    return f"SELECT * FROM VENDA WHERE VENDAT = '{params['data']}'"
```

### 4. ⚡ Performance

```python
# ✅ BOM - Considera performance
def get_sql(self, **params) -> str:
    return """
    SELECT 
        V.VENDAT,
        V.VENNUM,
        V.VENTOT
    FROM VENDA V
    WHERE V.VENDAT BETWEEN '2024-01-01' AND '2024-12-31'
      AND V.VENSTS = 'A'
    ORDER BY V.VENDAT DESC
    ROWS 1000  -- Limita resultados para evitar sobrecarga
    """

# ❌ RUIM - Pode retornar milhões de registros
def get_sql(self, **params) -> str:
    return "SELECT * FROM VENDA"  # Sem filtros nem limites
```

### 5. 🎯 Tratamento de Erros

```python
# ✅ BOM
def validate_params(self, **params) -> bool:
    try:
        codigo_produto = params.get('codigo_produto', '').strip()
        
        if not codigo_produto:
            raise ValidationError("Código do produto é obrigatório")
        
        if not codigo_produto.isalnum():
            raise ValidationError("Código do produto deve conter apenas letras e números")
        
        if len(codigo_produto) > 20:
            raise ValidationError("Código do produto deve ter no máximo 20 caracteres")
        
        return True
        
    except KeyError as e:
        raise ValidationError(f"Parâmetro obrigatório ausente: {e}")
    except Exception as e:
        raise ValidationError(f"Erro na validação: {str(e)}")

# ❌ RUIM
def validate_params(self, **params) -> bool:
    codigo_produto = params['codigo_produto']  # Pode gerar KeyError
    # Sem tratamento de erros
    return True
```

## Troubleshooting

### Problema: Operação não aparece na interface

**Possíveis causas:**
1. Operação não foi registrada no `_register_operations()`
2. Erro de sintaxe na classe
3. Erro de importação

**Solução:**
```python
# Verificar se está registrada
def _register_operations(self):
    operations = [
        # ... outras operações ...
        MinhaNovaOperation(),  # ← Verificar se está aqui
    ]

# Testar importação
python -c "from refactored_sqltools.core.operations.predefined import MinhaNovaOperation; print('OK')"
```

### Problema: Erro de validação não funciona

**Possível causa:** Método `validate_params` não está sendo chamado

**Solução:**
```python
# Verificar se o método está correto
def validate_params(self, **params) -> bool:  # ← Nome correto
    # ... validação ...
    return True
```

### Problema: SQL não executa

**Possíveis causas:**
1. Erro de sintaxe SQL
2. Tabelas/campos não existem
3. Permissões insuficientes

**Solução:**
```python
# Testar SQL diretamente no banco primeiro
def get_check_sql(self) -> str:
    return "SELECT 1 FROM RDB$DATABASE"  # SQL simples para testar conexão
```

### Problema: Parâmetros não aparecem

**Possível causa:** Parâmetros não estão sendo detectados automaticamente

**Solução:**
```python
# Implementar get_required_params() explicitamente
def get_required_params(self) -> list:
    return [
        {
            'name': 'meu_parametro',
            'type': 'string',
            'label': 'Meu Parâmetro',
            'required': True
        }
    ]
```

## 📚 Recursos Adicionais

### Documentação Relacionada
- [Como Remover uma Query](COMO_REMOVER_QUERY.md)
- [Arquitetura do Sistema](ARQUITETURA_SISTEMA.md)
- [Guia de Testes](../tests/README.md)

### Exemplos no Código
- `ConsultarNCMInexistenteOperation` - Exemplo com parâmetros de data
- `LimparTabelasFiscoOperation` - Exemplo de operação complexa
- `ConsultarTransacoesOperation` - Exemplo simples

### Ferramentas Úteis
- **Validação SQL**: Teste sempre no banco antes de implementar
- **Logs**: Use `logging` para debug durante desenvolvimento
- **Testes**: Execute `pytest tests/` para validar mudanças

---

**💡 Dica:** Sempre comece com um exemplo simples e vá adicionando complexidade gradualmente. O sistema foi projetado para ser extensível e fácil de usar!