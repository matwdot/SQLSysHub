# Design Document - SQLTools Refactoring

## Overview

Esta refatoração transforma o SQLTools.py monolítico em uma arquitetura modular baseada em padrões de design bem estabelecidos. O objetivo é manter toda a funcionalidade existente enquanto melhora a manutenibilidade, testabilidade e extensibilidade do código.

A nova arquitetura será implementada em uma pasta separada (`refactored_sqltools/`) para evitar conflitos com o código atual, permitindo uma migração gradual e segura.

## Architecture

A arquitetura refatorada segue o padrão de separação em camadas:

```
refactored_sqltools/
├── core/                    # Lógica de negócio
│   ├── database/           # Camada de dados
│   │   ├── manager.py      # Gerenciador central de conexões
│   │   └── drivers/        # Drivers modulares
│   │       ├── base.py     # Interface base para drivers
│   │       ├── firebird.py # Driver específico para Firebird
│   │       └── sqlserver.py# Driver específico para SQL Server
│   ├── operations/         # Operações de banco organizadas
│   │   ├── base.py         # Classe base para operações
│   │   └── predefined.py   # Operações pré-definidas do sistema
│   └── workers/            # Threads assíncronas
│       └── database_worker.py # Worker para operações de banco
├── ui/                      # Interface gráfica
│   ├── components/         # Componentes reutilizáveis
│   │   ├── connection_panel.py  # Painel de conexão
│   │   ├── operation_selector.py # Seletor de operações
│   │   ├── results_display.py   # Exibição de resultados
│   │   └── progress_indicator.py # Indicador de progresso
│   └── windows/            # Janelas principais
│       └── main_window.py  # Janela principal refatorada
└── utils/                   # Utilitários
    ├── exceptions.py       # Exceções customizadas
    └── validators.py       # Validadores de entrada
```

### Padrões de Design Aplicados

1. **Strategy Pattern**: Para drivers de banco de dados
2. **Template Method**: Para operações de banco
3. **Observer Pattern**: Para comunicação entre componentes UI
4. **Dependency Injection**: Para facilitar testes

## Components and Interfaces

### Database Layer

#### DatabaseDriver (Interface Base)
```python
class DatabaseDriver(ABC):
    @abstractmethod
    def connect(self, **kwargs) -> bool
    
    @abstractmethod
    def disconnect(self) -> None
    
    @abstractmethod
    def execute_query(self, query: str) -> Dict
    
    @abstractmethod
    def is_connected(self) -> bool
```

#### DatabaseManager
Gerencia múltiplos drivers e fornece uma interface unificada:
```python
class DatabaseManager:
    def __init__(self)
    def get_driver(self, db_type: str) -> DatabaseDriver
    def connect(self, db_type: str, **params) -> bool
    def execute_query(self, query: str) -> Dict
```

### Operations Layer

#### BaseOperation
```python
class BaseOperation(ABC):
    def __init__(self, name: str, description: str)
    
    @abstractmethod
    def get_sql(self, **params) -> str
    
    def validate_params(self, **params) -> bool
    def execute(self, db_manager: DatabaseManager, **params) -> Dict
```

### UI Components

#### ConnectionPanel
Componente reutilizável para gerenciar conexões:
```python
class ConnectionPanel(QWidget):
    connection_changed = pyqtSignal(bool)
    
    def __init__(self)
    def connect_database(self)
    def get_connection_params(self) -> Dict
```

#### ResultsDisplay
Componente para exibir resultados de queries:
```python
class ResultsDisplay(QWidget):
    def __init__(self)
    def display_table_results(self, columns: List, data: List)
    def display_text_results(self, message: str)
```

## Data Models

### Connection Parameters
```python
@dataclass
class ConnectionParams:
    db_type: str
    host: str
    port: str
    username: str
    password: str
    database: str
```

### Query Result
```python
@dataclass
class QueryResult:
    success: bool
    message: str
    columns: Optional[List[str]] = None
    data: Optional[List[Tuple]] = None
    rows_affected: Optional[int] = None
```

### Operation Definition
```python
@dataclass
class OperationDefinition:
    name: str
    description: str
    sql_template: str
    requires_dates: bool = False
    has_check_sql: bool = False
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Functional Equivalence
*For any* operation supported by the original SQLTools.py, executing the same operation with the same parameters on the refactored system should produce equivalent results
**Validates: Requirements 1.1**

### Property 2: Firebird Connection Consistency
*For any* valid Firebird connection parameters, the refactored Firebird driver should successfully connect when the original system would connect
**Validates: Requirements 2.2**

### Property 3: SQL Server Connection Consistency  
*For any* valid SQL Server connection parameters, the refactored SQL Server driver should successfully connect when the original system would connect
**Validates: Requirements 2.3**

### Property 4: Result Format Consistency
*For any* query executed across different database drivers, the result format should be consistent (same structure for columns, data, and metadata)
**Validates: Requirements 2.4**

### Property 5: Connection State Independence
*For any* sequence of connection operations on different drivers, each driver should maintain its connection state independently without affecting others
**Validates: Requirements 2.5**

### Property 6: Parameter Validation
*For any* operation with invalid parameters, the system should reject the operation before execution and provide appropriate error messages
**Validates: Requirements 4.2**

### Property 7: NCM Query Date Range Support
*For any* valid date range parameters, NCM queries should execute successfully and include the date range in the generated SQL
**Validates: Requirements 4.3**

### Property 8: Output Format Consistency
*For any* operation result, the output format should be consistent regardless of the operation type or database driver used
**Validates: Requirements 4.4**

### Property 9: Progress Signal Emission
*For any* database operation, progress signals should be emitted at appropriate intervals during execution
**Validates: Requirements 5.2**

### Property 10: Exception Propagation
*For any* database operation that encounters an error, exceptions should be properly propagated from worker threads to the main thread
**Validates: Requirements 5.3**

### Property 11: Completion Signal Accuracy
*For any* completed database operation, completion signals should be emitted with accurate result data
**Validates: Requirements 5.4**

### Property 12: Resource Cleanup
*For any* database operation, all resources (connections, cursors, threads) should be properly cleaned up after completion or failure
**Validates: Requirements 5.5**

## Error Handling

### Exception Hierarchy
```python
class SQLSysHubException(Exception):
    """Base exception for SQL SysHub"""

class ConnectionError(SQLSysHubException):
    """Raised when database connection fails"""

class QueryExecutionError(SQLSysHubException):
    """Raised when query execution fails"""

class ValidationError(SQLSysHubException):
    """Raised when parameter validation fails"""
```

### Error Recovery
- Connection failures: Retry mechanism with exponential backoff
- Query failures: Rollback transactions and provide detailed error messages
- UI errors: Graceful degradation with user feedback

## Testing Strategy

### Dual Testing Approach

A estratégia de testes combina testes unitários e testes baseados em propriedades para garantir cobertura abrangente:

#### Unit Testing
- Testes específicos para cada componente isoladamente
- Verificação de casos extremos e condições de erro
- Testes de integração entre componentes
- Mocking de dependências externas (bancos de dados) quando apropriado

#### Property-Based Testing
- Utilização da biblioteca **Hypothesis** para Python
- Cada teste de propriedade deve executar no mínimo 100 iterações
- Testes de propriedades devem ser marcados com comentários explícitos referenciando as propriedades de correção do documento de design
- Formato obrigatório para marcação: '**Feature: sqltools-refactoring, Property {number}: {property_text}**'
- Cada propriedade de correção deve ser implementada por um ÚNICO teste baseado em propriedades

#### Testing Requirements
- Cobertura mínima de 80% para código de negócio
- Todos os drivers de banco devem ter testes unitários
- Todas as propriedades de correção devem ter testes baseados em propriedades correspondentes
- Testes de UI devem usar pytest-qt para componentes PyQt5
- Testes devem ser executados em ambiente isolado com bancos de dados de teste