# Arquitetura do Sistema SQL SysHub

## Visão Geral

O SQL SysHub é uma aplicação GUI moderna em Python para gerenciamento e execução de queries em bancos de dados, construída com arquitetura modular usando PyQt5. O sistema foi refatorado de uma implementação monolítica para uma arquitetura em camadas bem definidas.

## Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   MainWindow    │  │   Components    │  │   Workers    │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE NEGÓCIO                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ DatabaseManager │  │   Operations    │  │  Validators  │ │
│  │                 │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Database       │  │    Drivers      │  │  Exceptions  │ │
│  │  Drivers        │  │    (Base)       │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Estrutura de Diretórios

```
refactored_sqltools/
├── main.py                     # Ponto de entrada principal
├── core/                       # Lógica de negócio
│   ├── database/              # Gerenciamento de conexões
│   │   ├── manager.py         # DatabaseManager (Factory Pattern)
│   │   └── drivers/           # Drivers específicos por SGBD
│   │       ├── base.py        # Interface base (Abstract Factory)
│   │       ├── firebird.py    # Implementação Firebird
│   │       └── sqlserver.py   # Implementação SQL Server
│   ├── operations/            # Operações predefinidas
│   │   ├── base.py           # Classe base (Template Method)
│   │   └── predefined.py     # Registry de operações
│   └── workers/               # Workers para threading
│       └── database_worker.py # Worker assíncrono
├── ui/                        # Interface do usuário
│   ├── components/            # Componentes reutilizáveis
│   │   ├── connection_panel.py
│   │   ├── operation_selector.py
│   │   ├── results_display.py
│   │   ├── progress_indicator.py
│   │   └── sql_editor.py
│   └── windows/               # Janelas principais
│       └── main_window.py     # Janela principal
└── utils/                     # Utilitários
    ├── exceptions.py          # Exceções customizadas
    └── validators.py          # Validadores
```

## Padrões de Design Implementados

### 1. Factory Pattern
- **DatabaseManager**: Cria drivers apropriados baseado no tipo de banco
- **DatabaseWorkerFactory**: Cria workers para diferentes operações

### 2. Abstract Factory Pattern
- **DatabaseDriver**: Interface base para todos os drivers
- Implementações específicas: FirebirdDriver, SqlServerDriver

### 3. Template Method Pattern
- **BaseOperation**: Define fluxo de execução padrão
- Subclasses implementam métodos específicos (get_sql, validate_params)

### 4. Registry Pattern
- **OperationRegistry**: Registra e gerencia operações predefinidas

### 5. Observer Pattern
- **PyQt5 Signals/Slots**: Comunicação entre componentes UI

### 6. Worker Pattern
- **DatabaseWorker**: Execução assíncrona para não bloquear UI

## Componentes Principais

### Core Layer

#### DatabaseManager
- **Responsabilidade**: Gerenciar múltiplos drivers de banco
- **Funcionalidades**:
  - Factory para criação de drivers
  - Gerenciamento de conexões ativas
  - Execução de queries
  - Controle de estado de conexão

#### Database Drivers
- **Base**: Interface comum para todos os drivers
- **Firebird**: Implementação específica para Firebird
- **SQL Server**: Implementação específica para SQL Server
- **Extensibilidade**: Fácil adição de novos drivers

#### Operations
- **BaseOperation**: Template para operações de banco
- **PredefinedOperations**: Operações específicas do negócio
- **OperationRegistry**: Catálogo de operações disponíveis

### UI Layer

#### MainWindow
- **Responsabilidade**: Orquestrar todos os componentes UI
- **Funcionalidades**:
  - Integração de componentes
  - Gerenciamento de estado da aplicação
  - Coordenação de operações assíncronas

#### Components
- **ConnectionPanel**: Gerencia parâmetros de conexão
- **OperationSelector**: Seleção e configuração de operações
- **ResultsDisplay**: Exibição de resultados em tabela
- **SQLEditor**: Editor com syntax highlighting
- **ProgressIndicator**: Feedback visual de progresso

### Workers Layer

#### DatabaseWorker
- **Responsabilidade**: Execução assíncrona de operações
- **Funcionalidades**:
  - Threading para não bloquear UI
  - Relatório de progresso
  - Tratamento de erros
  - Cleanup de recursos

## Fluxo de Dados

### 1. Conexão com Banco
```
UI (ConnectionPanel) → MainWindow → DatabaseWorker → DatabaseManager → Driver
```

### 2. Execução de Query
```
UI (OperationSelector) → MainWindow → DatabaseWorker → DatabaseManager → Driver → Database
```

### 3. Exibição de Resultados
```
Database → Driver → DatabaseManager → DatabaseWorker → MainWindow → ResultsDisplay
```

## Tratamento de Erros

### Hierarquia de Exceções
```
SQLSysHubException (base)
├── ConnectionError
├── QueryExecutionError
└── ValidationError
```

### Estratégia de Tratamento
1. **Camada de Driver**: Captura erros específicos do SGBD
2. **Camada de Manager**: Padroniza erros para a aplicação
3. **Camada de Worker**: Propaga erros de forma assíncrona
4. **Camada de UI**: Exibe erros de forma amigável

## Threading e Concorrência

### Modelo de Threading
- **Main Thread**: UI e coordenação
- **Worker Threads**: Operações de banco de dados
- **Signal/Slot**: Comunicação thread-safe

### Prevenção de Problemas
- UI bloqueada durante operações longas
- Cancelamento gracioso de operações
- Cleanup automático de recursos
- Estado consistente da aplicação

## Extensibilidade

### Adição de Novos Drivers
1. Herdar de `DatabaseDriver`
2. Implementar métodos abstratos
3. Registrar no `DatabaseManager`

### Adição de Novas Operações
1. Herdar de `BaseOperation`
2. Implementar `get_sql()` e `validate_params()`
3. Registrar no `OperationRegistry`

### Adição de Novos Componentes UI
1. Herdar de componente PyQt5 apropriado
2. Implementar sinais necessários
3. Integrar na `MainWindow`

## Configuração e Deployment

### Dependências
- **Core**: PyQt5, qtawesome
- **Drivers**: firebirdsql, pyodbc, psycopg2, mysql-connector
- **Testes**: pytest, pytest-qt, pytest-cov

### Execução
- **Recomendado**: `python run_sqltools.py`
- **Alternativo**: `python refactored_sqltools/main.py`
- **Módulo**: `python -c "from refactored_sqltools.main import main; main()"`

### Testes
- **Unitários**: Componentes individuais
- **Integração**: Fluxos completos
- **UI**: Interações de interface

## Vantagens da Arquitetura

1. **Modularidade**: Componentes independentes e reutilizáveis
2. **Testabilidade**: Cada camada pode ser testada isoladamente
3. **Manutenibilidade**: Código organizado e bem estruturado
4. **Extensibilidade**: Fácil adição de novos recursos
5. **Performance**: Threading para operações assíncronas
6. **Robustez**: Tratamento abrangente de erros
7. **Usabilidade**: Interface responsiva e intuitiva

## Considerações de Performance

### Otimizações Implementadas
- Threading para operações de I/O
- Connection pooling implícito
- Lazy loading de componentes
- Cleanup automático de recursos

### Monitoramento
- Progress indicators para feedback
- Status bar para informações
- Logging configurável
- Tratamento de timeouts

Esta arquitetura garante que o sistema seja robusto, extensível e mantenha uma boa experiência do usuário, seguindo as melhores práticas de desenvolvimento de software.