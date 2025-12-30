# Sistema de Parâmetros para Queries

## Visão Geral

O sistema agora suporta queries com parâmetros que abrem uma tela separada para coleta de informações e **executam automaticamente** após a confirmação dos parâmetros.

## Como Funciona

### 1. Fluxo Automático (Novo)

1. **Seleção da Query**: Usuário seleciona uma query com parâmetros
2. **Diálogo de Parâmetros**: Sistema abre automaticamente uma tela separada
3. **Coleta de Dados**: Usuário preenche os parâmetros necessários
4. **Execução Automática**: Ao clicar "Executar Query", o sistema:
   - Valida os parâmetros
   - Fecha o diálogo
   - Formata a SQL com os parâmetros
   - **Executa automaticamente a query**

### 2. Diferença entre Tipos de Query

#### Queries COM Parâmetros (Execução Automática)
- **Exemplo**: "Buscar Produto por Código", "Ver NCMs a Vencer"
- **Fluxo**: Selecionar → Preencher parâmetros → Execução automática
- **Botão**: "Executar Query" (verde, destacado)

#### Queries SEM Parâmetros (Execução Manual)
- **Exemplo**: "Listar Todos os Produtos", "Cancelar Cupom"
- **Fluxo**: Selecionar → Clicar botão "Executar" manualmente
- **Botão**: "Executar" (azul, padrão)

### 3. Definição de Parâmetros

Queries que precisam de parâmetros devem incluir uma seção `parameters` na sua definição:

```python
"Nome da Query": {
    "description": "Descrição da query",
    "execute_sql": "SELECT * FROM TABELA WHERE CAMPO = '{parametro}'",
    "parameters": {
        "parametro": {
            "type": "text",
            "label": "Rótulo do Parâmetro",
            "placeholder": "Texto de ajuda"
        }
    }
}
```

### 4. Tipos de Parâmetros Suportados

#### Texto (`text`)
```python
"codigo_produto": {
    "type": "text",
    "label": "Código do Produto",
    "placeholder": "Digite o código do produto"
}
```

#### Data (`date`)
```python
"data_inicio": {
    "type": "date",
    "label": "Data Início",
    "default": "month_ago"  # ou "today" ou "yyyy-mm-dd"
}
```

### 5. Valores Padrão para Datas

- `"today"`: Data atual
- `"month_ago"`: 30 dias atrás
- `"yyyy-mm-dd"`: Data específica no formato ISO

### 6. Fluxo de Execução (Atualizado)

1. **Seleção da Query**: Usuário seleciona uma query com parâmetros
2. **Diálogo de Parâmetros**: Sistema abre automaticamente uma tela separada
3. **Coleta de Dados**: Usuário preenche os parâmetros necessários
4. **Execução Automática**: Usuário clica em "Executar Query" e o sistema:
   - Valida os parâmetros
   - Fecha o diálogo
   - Formata a SQL com os valores
   - **Executa automaticamente a query**
5. **Resultados**: Query é executada e resultados são exibidos imediatamente

## Exemplos Implementados

### Buscar Produto por Código
- **Parâmetros**: Código do produto
- **Tipo**: Campo de texto
- **Execução**: Automática após confirmar parâmetros

### Ver NCMs a Vencer
- **Parâmetros**: Data início e data fim
- **Tipo**: Campos de data com calendário
- **Padrão**: Último mês até hoje
- **Execução**: Automática após confirmar parâmetros

## Paginação de Resultados

### Como Funciona
Queries com muitos resultados podem usar paginação para melhorar a performance e usabilidade:

1. **Registros por Página**: Define quantos registros mostrar (ex: 100, 500, 1000)
2. **Página**: Define qual página visualizar (1, 2, 3...)
3. **Cálculo Automático**: Sistema calcula automaticamente os valores OFFSET e LIMIT
4. **Query de Contagem**: Mostra o total de registros disponíveis

### Exemplo de Uso
- Total de registros: 2.500
- Registros por página: 100
- Página 1: registros 1-100
- Página 2: registros 101-200
- Página 25: registros 2401-2500

### Implementação SQL
```sql
-- Query de contagem (executada primeiro)
SELECT COUNT(*) AS TOTAL_REGISTROS FROM ...

-- Query paginada (executada depois)
SELECT ... FROM ... ORDER BY ... ROWS {offset} TO {limit}
```

Onde:
- `offset = (página - 1) * registros_por_página + 1`
- `limit = offset + registros_por_página - 1`

## Vantagens da Nova Abordagem

1. **Interface Limpa**: Sessão principal não fica poluída com campos de parâmetros
2. **Fluxo Otimizado**: Execução automática elimina clique extra no botão "Executar"
3. **Feedback Visual**: Botão "Executar Query" deixa claro que a query será executada
4. **Usabilidade**: Diálogo modal força o usuário a preencher os dados antes de prosseguir
5. **Validação**: Parâmetros são validados antes da execução automática
6. **Flexibilidade**: Cada query pode ter seus próprios parâmetros específicos

## Implementação Técnica

### Componentes Envolvidos

1. **OperationSelector**: Detecta queries com parâmetros e emite sinal
2. **ParameterDialog**: Tela modal para coleta de parâmetros
3. **MainWindow**: Coordena a exibição do diálogo e coleta dos dados

### Sinais e Slots

- `parameters_requested`: Emitido quando query com parâmetros é selecionada
- `parameters_confirmed`: Emitido quando usuário confirma os parâmetros
- `set_parameters`: Método para definir parâmetros coletados

## Adicionando Novas Queries com Parâmetros

Para adicionar uma nova query com parâmetros:

1. Defina a query no `operation_selector.py`
2. Inclua a seção `parameters` com a configuração dos campos
3. Use placeholders `{nome_parametro}` no SQL
4. Teste a funcionalidade

Exemplo:
```python
"Consultar Vendas por Período": {
    "description": "Consulta vendas em um período específico",
    "execute_sql": """
        SELECT * FROM VENDAS 
        WHERE DATA_VENDA BETWEEN '{data_inicio}' AND '{data_fim}'
        AND VENDEDOR = '{vendedor}'
    """,
    "parameters": {
        "data_inicio": {
            "type": "date",
            "label": "Data Início",
            "default": "month_ago"
        },
        "data_fim": {
            "type": "date",
            "label": "Data Fim", 
            "default": "today"
        },
        "vendedor": {
            "type": "text",
            "label": "Código do Vendedor",
            "placeholder": "Digite o código do vendedor"
        }
    }
}
```