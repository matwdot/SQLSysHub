# Solução para Erro Firebird WinError 193

## Problema
```
Erro na conexão: [WinError 193] %1 não é um aplicativo Win32 válido
```

## Causa
Incompatibilidade de arquitetura entre Python e Firebird:
- Python 64-bit + Firebird 32-bit = ❌ Erro
- Python 32-bit + Firebird 64-bit = ❌ Erro

## ✅ Solução Implementada

A aplicação agora usa automaticamente o driver `firebirdsql` que é mais compatível:

```bash
pip install firebirdsql passlib
```

**Nota**: O driver `firebirdsql` requer a biblioteca `passlib` como dependência.

## Como Funciona

1. **Detecção Automática**: A aplicação tenta primeiro o driver `firebirdsql`
2. **Fallback**: Se falhar, tenta o driver `fdb`
3. **Mensagens Claras**: Mostra exatamente qual é o problema

## Configuração para Firebird

### Conexão Local
- **Host**: localhost (ou deixe vazio)
- **Porta**: 3050
- **Usuário**: SYSDBA
- **Senha**: masterkey
- **Database**: `C:\caminho\completo\para\database.fdb`

### Conexão Remota
- **Host**: IP do servidor
- **Porta**: 3050
- **Usuário**: SYSDBA
- **Senha**: senha do servidor
- **Database**: `database.fdb` (apenas o nome)

## Teste de Conexão

1. Abra a aplicação: `python main.py`
2. Configure os parâmetros de conexão
3. Clique em "Conectar"
4. Se conectar com sucesso, execute uma query de teste:

```sql
SELECT FIRST 5 * FROM RDB$RELATIONS;
```

## Outras Soluções (se ainda não funcionar)

### 1. Instalar Firebird 64-bit
- Download: https://firebirdsql.org/en/downloads/
- Escolha a versão 64-bit
- Reinstale o serviço

### 2. Usar Python 32-bit
- Download Python 32-bit do python.org
- Reinstale os pacotes necessários

### 3. Verificar Serviço Firebird
```cmd
# Verificar se está rodando
sc query FirebirdServerDefaultInstance

# Iniciar serviço
net start FirebirdServerDefaultInstance
```

## Verificação de Arquitetura

Para verificar a arquitetura do seu Python:
```python
import platform
print(f"Python: {platform.architecture()[0]}")
```

## Status da Solução

✅ **Resolvido**: A aplicação agora funciona com Firebird usando o driver `firebirdsql`
✅ **Automático**: Detecção e seleção automática do melhor driver
✅ **Compatível**: Funciona com diferentes arquiteturas