# Estrutura do Projeto SQL SysHub

## Visão Geral
Este documento descreve a estrutura final do projeto SQL SysHub após a refatoração e limpeza.

## Estrutura de Diretórios

```
ncm-inexistente/
│
├── refactored_sqltools/          # Aplicação principal
│   ├── main.py                   # Ponto de entrada
│   ├── __init__.py
│   ├── README.md                 # Documentação do módulo
│   │
│   ├── core/                     # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── database/             # Gerenciamento de banco de dados
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # DatabaseManager
│   │   │   └── drivers/          # Drivers específicos
│   │   │       ├── __init__.py
│   │   │       ├── base.py       # Classe base
│   │   │       ├── firebird.py   # Driver Firebird
│   │   │       └── sqlserver.py  # Driver SQL Server
│   │   │
│   │   ├── operations/           # Operações predefinidas
│   │   │   ├── __init__.py
│   │   │   └── predefined.py     # Queries predefinidas
│   │   │
│   │   └── workers/              # Workers para threading
│   │       ├── __init__.py
│   │       └── database_worker.py # DatabaseWorker
│   │
│   ├── ui/                       # Interface do usuário
│   │   ├── __init__.py
│   │   ├── components/           # Componentes reutilizáveis
│   │   │   ├── __init__.py
│   │   │   ├── connection_panel.py
│   │   │   ├── operation_selector.py
│   │   │   ├── progress_indicator.py
│   │   │   └── results_display.py
│   │   │
│   │   └── windows/              # Janelas principais
│   │       ├── __init__.py
│   │       └── main_window.py    # MainWindow
│   │
│   └── utils/                    # Utilitários
│       ├── __init__.py
│       ├── exceptions.py         # Exceções customizadas
│       └── validators.py         # Validadores
│
├── tests/                        # Testes
│   ├── __init__.py
│   ├── conftest.py              # Configurações pytest
│   ├── unit/                    # Testes unitários
│   ├── integration/             # Testes de integração
│   └── property/                # Testes baseados em propriedades
│
├── imagens/                     # Recursos visuais
│   └── cmLogo.png
│
├── .kiro/                       # Configurações Kiro IDE
│   └── specs/                   # Especificações do projeto
│
├── run_sqltools.py              # Launcher principal
├── verify_system.py             # Verificação do sistema
│
├── requirements_pyqt.txt        # Dependências PyQt5
├── requirements_test.txt        # Dependências de teste
├── pytest.ini                   # Configuração pytest
│
├── README.md                    # Documentação principal
├── DRIVERS.md                   # Documentação de drivers
├── SOLUCAO_FIREBIRD.md         # Solução para problemas Firebird
├── PROJECT_STRUCTURE.md        # Este arquivo
│
└── .gitignore                   # Arquivos ignorados pelo Git
```

## Arquivos Principais

### Executáveis
- **run_sqltools.py**: Forma recomendada de executar a aplicação
- **refactored_sqltools/main.py**: Ponto de entrada alternativo

### Configuração
- **requirements_pyqt.txt**: Dependências principais (PyQt5)
- **requirements_test.txt**: Dependências para testes
- **pytest.ini**: Configuração do pytest

### Documentação
- **README.md**: Documentação principal do projeto
- **DRIVERS.md**: Instruções para instalação de drivers
- **SOLUCAO_FIREBIRD.md**: Solução para problemas específicos do Firebird
- **PROJECT_STRUCTURE.md**: Estrutura do projeto (este arquivo)

## Módulos Principais

### Core (refactored_sqltools/core/)
Contém a lógica de negócio da aplicação:
- **database/**: Gerenciamento de conexões e drivers
- **operations/**: Operações e queries predefinidas
- **workers/**: Workers para execução assíncrona

### UI (refactored_sqltools/ui/)
Interface do usuário em PyQt5:
- **components/**: Componentes reutilizáveis
- **windows/**: Janelas principais da aplicação

### Utils (refactored_sqltools/utils/)
Utilitários e helpers:
- **exceptions.py**: Exceções customizadas
- **validators.py**: Validadores de entrada

## Testes

### Estrutura de Testes
- **unit/**: Testes unitários de componentes individuais
- **integration/**: Testes de integração entre módulos
- **property/**: Testes baseados em propriedades (hypothesis)

### Executar Testes
```bash
pytest                          # Todos os testes
pytest tests/unit/             # Apenas testes unitários
pytest tests/integration/      # Apenas testes de integração
pytest --cov=refactored_sqltools  # Com cobertura
```

## Como Executar

### Método Recomendado
```bash
python run_sqltools.py
```

### Métodos Alternativos
```bash
python refactored_sqltools/main.py
python -c "from refactored_sqltools.main import main; main()"
```

### Opções de Linha de Comando
```bash
python run_sqltools.py --help      # Ajuda
python run_sqltools.py --debug     # Modo debug
python run_sqltools.py --version   # Versão
python run_sqltools.py --style Windows  # Estilo da interface
```

## Arquivos Removidos na Limpeza

Os seguintes arquivos foram removidos por não serem mais necessários:
- **SQLTools.py**: Versão original (substituída pela refatorada)
- **build_simple.py**: Protótipo de build
- **main_pyqt.py**: Protótipo PyQt
- **demo_ui_components.py**: Demo de componentes
- **prompt.md**: Documentação temporária
- **REFATORACAO_PROPOSTA.md**: Proposta de refatoração
- **RESUMO_REFATORACAO.md**: Resumo da refatoração
- **requirements.txt**: Requirements antigo
- **version_info.txt**: Informações de versão
- **exemplo_implementacao/**: Pasta de exemplos

## Próximos Passos

1. Implementar drivers adicionais (PostgreSQL, MySQL)
2. Adicionar mais operações predefinidas
3. Melhorar a interface com mais recursos
4. Expandir a cobertura de testes
5. Adicionar documentação de API
