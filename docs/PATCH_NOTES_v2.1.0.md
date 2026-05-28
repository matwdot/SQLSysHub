# Patch Notes — SQL SysHub v2.1.0

**Data:** Maio 2026

---

## Visão Geral

Esta release representa uma **reformulação completa** do SQL SysHub. Todo o código foi reestruturado em uma arquitetura limpa com separação clara entre camadas (core, ui, utils, config), corrigindo problemas de segurança, encoding, threading e qualidade identificados na versão anterior (v2.0.1).

---

## Principais Mudanças

### 🧱 Arquitetura

| Mudança | Detalhes |
|---------|----------|
| Separação em camadas | `core/` (lógica de negócio), `ui/` (interface), `utils/` (utilitários), `config/` (configuração) |
| Drivers com interface abstrata | `BaseDriver` define contrato; `FirebirdDriver` e `SqlServerDriver` implementam |
| Operações registradas | `OperationRegistry` centraliza descoberta e execução de operações |
| Workers assíncronos | `DatabaseWorker` com `QThread` para operações sem travar a UI |
| Gerenciamento de paths centralizado | `utils/paths.py` resolve caminhos corretamente em dev e no executável empacotado |

### 🔒 Segurança

- Senha **não é mais persistida** no `settings.ini`
- Armazenamento seguro via `keyring` (`utils/credential_store.py`)
- `settings.ini` movido para `.gitignore`; `settings.example.ini` criado sem credenciais
- Conexão string do ODBC tem valores escapados
- `traceback.print_exc()` removido do worker (logs sanitizados)

### 🖥️ Interface

- Splash screen com verificações de ambiente (Python, PyQt, driver, NCM, diretórios, config)
- Gerenciador de temas dark/light (`ui/theme_manager.py`)
- Componentes de UI refatorados com Fluent Design consistente
- Preview de SQL, calendário, painel de parâmetros aprimorados

### 🗄️ Banco de Dados

- Conexão não é mais reutilizada entre workers (cada operação cria a própria conexão)
- Parâmetros bindados no SQL (previne SQL injection)
- `DatabaseManager` local por thread via `connection_config`
- Suporte a Firebird (firebirdsql) e SQL Server (ODBC)

### 📦 NCM (Tabela Siscomex)

- JSON de NCM **não é mais empacotado** no repositório (removido `Tabela_NCM_Vigente_20260101.json` ~136k linhas)
- Download automático do JSON do Siscomex na splash screen
- Validação de schema e payload antes do cache
- Fallback para arquivo offline se download falhar

### ✅ Testes

- Estrutura completa de testes: `unit/`, `integration/`, `performance/`, `property/`
- Testes unitários para validadores, operações, drivers, componentes de UI
- Testes de propriedade com Hypothesis (validação de entradas)
- Testes de concorrência e performance
- Cobertura configurada via pytest-cov
- Diretório de testes morto (`refactored_sqltools/tests/`) removido

### 🔧 CI/CD

- Workflow `build-release.yml` atualizado:
  - Python `3.11` → **`3.14`**
  - **Job de teste** obrigatório antes do build (`pytest`)
  - Ignora testes de integração, performance e UI no CI
- `Pillow` movido para `requirements_build.txt` com versão fixa
- `qtawesome` removido do build (não é mais usado no código)
- `qfluentwidgets` instalado via `requirements_build.txt`

---

## Arquivos Novos

```
refactored_sqltools/
├── .gitignore
├── agent.md
├── todo.md
├── config/settings.example.ini
├── ui/theme_manager.py
├── utils/credential_store.py
├── utils/paths.py
├── insumos_ui/              # Assets de design (ZIPs, HTML, PNG)
tests/
├── property/                # Testes de propriedade (Hypothesis)
├── coverage_analysis.py     # Script de análise de cobertura
├── quality_monitor.py       # Script de monitoramento de qualidade
```

## Arquivos Removidos

```
refactored_sqltools/
├── config/settings.ini              # (agora no .gitignore)
├── json/Tabela_NCM_Vigente_20260101.json  # (~136k linhas)
├── core/operations/individual/buscar_produto_codigo.py
├── tests/                          # Diretório de testes morto
tests/
├── integration/test_complete_workflows.py.backup
├── integration/test_complete_workflows.py.removed
├── integration/test_core_functionality.py.backup
├── integration/test_core_functionality.py.removed
├── unit/test_database_driver_base.py
coverage.json                       # (agora no .gitignore)
quality_metrics/                    # (agora no .gitignore)
```

---

## Operações Disponíveis (6)

| Operação | Descrição |
|----------|-----------|
| Cancelar Cupom | Cancela cupons fiscais no banco |
| Apagar Certificado | Remove certificados digitais |
| Corrigir Erro de Equipamento | Corrige erros de equipamento no PDV |
| Limpar Tabelas do Fisco | Limpa tabelas fiscais |
| Consultar NCM Inexistente | Consulta NCMs sem cadastro |
| Ver NCMs a Vencer | Lista NCMs próximas do vencimento |

---

## Como Atualizar

Para usuários da v2.0.1:

1. Baixe o executável mais recente em [GitHub Releases](https://github.com/matwdot/SQLSysHub/releases/latest)
2. Extraia o ZIP e execute `SQLSysHub.exe`
3. Na primeira execução, a splash screen fará o download automático da tabela NCM
4. Configure a conexão com o banco de dados (a senha não é mais persistida em disco)

---

**Full Changelog:** https://github.com/matwdot/SQLSysHub/compare/v2.0.1...v2.1.0
