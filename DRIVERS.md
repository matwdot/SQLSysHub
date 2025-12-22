# Instalação de Drivers de Banco de Dados

Para usar conexões reais com bancos de dados, você precisa instalar os drivers apropriados:

## Firebird

### Opção 1: Driver FDB (Recomendado)
```bash
pip install fdb
```

### Opção 2: Driver FirebirdSQL (Recomendado para problemas de arquitetura)
```bash
pip install firebirdsql passlib
```

**Configuração típica:**
- Host: localhost (ou IP do servidor)
- Porta: 3050
- Usuário: SYSDBA
- Senha: masterkey
- Database: C:\caminho\para\database.fdb

### ⚠️ Problema de Arquitetura (Windows)

**Erro comum**: `WinError 193: %1 não é um aplicativo Win32 válido`

**Causa**: Incompatibilidade entre arquitetura do Python e Firebird
- Python 64-bit + Firebird 32-bit = ❌ Erro
- Python 32-bit + Firebird 64-bit = ❌ Erro

**Soluções:**

1. **Instalar Firebird 64-bit** (Recomendado)
   - Download: https://firebirdsql.org/en/downloads/
   - Escolha a versão 64-bit se usar Python 64-bit

2. **Usar driver alternativo**
   ```bash
   pip install firebirdsql passlib
   ```
   - Este driver é mais compatível com diferentes arquiteturas
   - Requer a biblioteca `passlib` como dependência

3. **Verificar arquitetura do Python**
   ```python
   import platform
   print(platform.architecture())  # ('64bit', 'WindowsPE') ou ('32bit', 'WindowsPE')
   ```

4. **Usar Python 32-bit** (se Firebird for 32-bit)
   - Instale Python 32-bit do python.org
   - Reinstale os pacotes necessários

## SQL Server
```bash
pip install pyodbc
```

**Pré-requisitos:**
- Microsoft ODBC Driver 17 for SQL Server deve estar instalado no sistema
- Download: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Configuração típica:**
- Host: localhost ou servidor
- Porta: 1433
- Usuário: sa ou usuário do domínio
- Senha: senha do usuário
- Database: nome do banco

## PostgreSQL
```bash
pip install psycopg2-binary
```

**Configuração típica:**
- Host: localhost
- Porta: 5432
- Usuário: postgres
- Senha: senha definida na instalação
- Database: nome do banco

## MySQL
```bash
pip install mysql-connector-python
```

**Configuração típica:**
- Host: localhost
- Porta: 3306
- Usuário: root
- Senha: senha definida na instalação
- Database: nome do banco

## Instalação de Todos os Drivers
Para instalar todos os drivers de uma vez:

```bash
pip install fdb pyodbc psycopg2-binary mysql-connector-python
```

## Notas Importantes

1. **Firebird**: O campo "Database" deve conter o caminho completo para o arquivo .fdb
2. **SQL Server**: Requer o ODBC Driver instalado no sistema operacional
3. **PostgreSQL**: Use psycopg2-binary para evitar problemas de compilação
4. **MySQL**: O mysql-connector-python é o driver oficial da Oracle

## Testando a Conexão

1. Instale o driver necessário
2. Configure os parâmetros de conexão na interface
3. Clique em "Conectar"
4. Se a conexão for bem-sucedida, o botão "Executar Query" será habilitado

## Troubleshooting

### Erro de Driver Não Encontrado
- Certifique-se de que instalou o driver correto
- Verifique se está usando o ambiente Python correto (virtual environment)

### Erro de Conexão Recusada
- Verifique se o servidor de banco está rodando
- Confirme host e porta
- Verifique firewall e configurações de rede

### Erro de Autenticação
- Confirme usuário e senha
- Verifique permissões do usuário no banco de dados

### Erro de Database Não Encontrado
- Confirme que o banco de dados existe
- Para Firebird, verifique o caminho completo do arquivo .fdb