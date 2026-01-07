# SQL SysHub

Aplicação para gerenciamento e execução de queries em bancos de dados com interface gráfica moderna.

## Bancos Suportados

- Firebird
- SQL Server
- PostgreSQL
- MySQL

## Operações Disponíveis

### Apagar Certificado
Remove o certificado digital do sistema, limpando os campos de certificado, senha e número de série.

### Buscar Produto por Código
Localiza um produto específico pelo código, retornando código, descrição e NCM.

### Cancelar Cupom
Cancela cupons fiscais definindo STACUP e STACUPVRF como 'F'. Pode ser aplicado a todos os caixas ou filtrado por número específico.

### Consultar NCM Inexistente
Busca transações rejeitadas por NCM inexistente em um período de datas. Retorna nota, data, produto, descrição, caixa e mensagem de erro.

### Corrigir Erro de Equipamento
Remove o número de série do caixa para corrigir erros de equipamento.

### Limpar Tabelas do Fisco
Remove todos os dados das tabelas fiscais (FISCO_PRODUTOAUX, FISCO_DOCUMENTOFISCAL, FISCO_CUPOMFISCAL, etc).

### Ver NCMs a Vencer
Consulta NCMs próximos do vencimento usando arquivo JSON do Siscomex. Considera vendas do último ano e classifica por status: VENCIDO, A VENCER (próximo), A VENCER ou NCM NÃO ENCONTRADO.

## Como Usar

1. Selecione o tipo de banco no painel lateral
2. Preencha os dados de conexão (Host, Porta, Usuário, Senha)
3. Clique em "Conectar"
4. Escolha uma operação predefinida ou digite sua query SQL
5. Execute e visualize os resultados na tabela

## Requisitos

- Windows 7 ou superior
- Drivers de banco conforme necessário (Firebird, ODBC para SQL Server)
