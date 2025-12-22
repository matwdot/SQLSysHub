# SQL SysHub - Database Query Manager

Uma aplicação GUI moderna em Python para gerenciamento e execução de queries em bancos de dados, com arquitetura modular e interface PyQt5.

## Características

- **Arquitetura Modular**: Código organizado em módulos especializados
- **Interface Moderna**: Design responsivo usando PyQt5
- **Suporte Multi-Database**: Firebird, SQL Server, PostgreSQL, MySQL
- **Editor de Query**: Editor SQL avançado
- **Visualização de Resultados**: Tabela interativa com funcionalidades avançadas
- **Threading**: Operações assíncronas para melhor performance
- **Extensível**: Arquitetura preparada para novos recursos

## Instalação

### Dependências Básicas
```bash
pip install -r requirements_pyqt.txt
```

### Para conexões reais, instale os drivers necessários:
```bash
# Firebird (recomendado - mais compatível)
pip install firebirdsql passlib

# Ou driver alternativo
pip install fdb

# SQL Server (requer ODBC Driver 17)
pip install pyodbc

# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysql-connector-python
```

**⚠️ Problema Firebird WinError 193?** Veja [SOLUCAO_FIREBIRD.md](SOLUCAO_FIREBIRD.md)

Veja [DRIVERS.md](DRIVERS.md) para instruções detalhadas.

## Como Executar

### Opção 1: Script launcher (recomendado)
```bash
python run_sqltools.py
```

### Opção 2: Módulo principal
```bash
python refactored_sqltools/main.py
```

### Opção 3: Como módulo Python
```bash
python -c "from refactored_sqltools.main import main; main()"
```

### Opções de linha de comando
```bash
# Mostrar ajuda
python run_sqltools.py --help

# Executar com debug
python run_sqltools.py --debug

# Definir estilo da interface
python run_sqltools.py --style Windows

# Mostrar versão
python run_sqltools.py --version
```

## Como Usar

### 1. Conexão com Banco de Dados
- Selecione o tipo de database no painel lateral
- Preencha os campos de conexão (Host, Porta, Usuário, Senha)
- Clique em "Conectar"

### 2. Executar Queries
- Digite sua query SQL no editor
- Clique em "Executar Query"
- Visualize os resultados na tabela abaixo

### 3. Copiar Resultados
- Após executar uma query, clique em "Copiar"
- Os resultados serão copiados para a área de transferência

## Estrutura do Projeto

### Arquitetura Refatorada
```
refactored_sqltools/
├── main.py                 # Ponto de entrada principal
├── core/                   # Lógica de negócio
│   ├── database/          # Gerenciamento de conexões
│   │   ├── manager.py     # Gerenciador principal
│   │   └── drivers/       # Drivers específicos
│   ├── operations/        # Operações predefinidas
│   └── workers/           # Workers para threading
├── ui/                    # Interface do usuário
│   ├── components/        # Componentes reutilizáveis
│   └── windows/           # Janelas principais
└── utils/                 # Utilitários e validadores
```

### Scripts de Execução
- `run_sqltools.py`: Launcher principal (recomendado)
- `refactored_sqltools/main.py`: Módulo principal
- `requirements_pyqt.txt`: Dependências PyQt5

## Funcionalidades Implementadas

### Interface
- ✅ Painel lateral para conexão
- ✅ Editor de query SQL
- ✅ Área de resultados com tabela
- ✅ Botões de ação (Conectar, Executar, Copiar, Limpar)
- ✅ Status de conexão e execução

### Funcionalidades
- ✅ **Conexões reais** com Firebird, SQL Server, PostgreSQL, MySQL
- ✅ **Execução de queries** SELECT, INSERT, UPDATE, DELETE
- ✅ **Exibição de resultados** em formato tabular com scrollbars
- ✅ **Cópia de resultados** para clipboard
- ✅ **Interface responsiva** e moderna com tema dark
- ✅ **Tratamento de erros** com mensagens informativas
- ✅ **Threading** para não travar a interface durante operações

## Vantagens da Implementação

- **Conexões Reais**: Suporte completo para múltiplos SGBDs
- **Performance**: Interface responsiva com threading para operações de I/O
- **Tema Dark**: Interface moderna e profissional
- **Tratamento de Erros**: Mensagens claras para diferentes tipos de erro
- **Flexibilidade**: Funciona com ou sem drivers instalados
- **Zero Config**: Interface pronta para uso imediato

## Tipos de Query Suportados

- **SELECT**: Consultas com resultados tabulares
- **INSERT/UPDATE/DELETE**: Operações de modificação com contagem de linhas afetadas
- **CREATE/DROP**: Comandos DDL
- **Stored Procedures**: Chamadas de procedimentos (dependendo do SGBD)

## Desenvolvimento e Testes

### Executar Testes
```bash
# Instalar dependências de teste
pip install -r requirements_test.txt

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=refactored_sqltools

# Executar testes específicos
pytest tests/unit/
pytest tests/integration/
```

### Estrutura de Testes
```
tests/
├── unit/                  # Testes unitários
├── integration/           # Testes de integração
├── property/              # Testes baseados em propriedades
└── conftest.py           # Configurações pytest
```

### Verificação do Sistema
```bash
python verify_system.py   # Verifica dependências e configuração
```

## Recursos Avançados

- **Auto-commit**: Transações automáticas para queries de modificação
- **Rollback**: Desfaz alterações em caso de erro
- **Encoding**: Suporte a UTF-8 para caracteres especiais
- **Connection Pooling**: Reutilização de conexões ativas