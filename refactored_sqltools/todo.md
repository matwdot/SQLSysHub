# TODO de Correcao

Status atualizado apos a rodada de correcoes.

## 1. Proteger Credenciais

- [x] Remover senha real e defaults sensiveis de `config/settings.ini`.
- [x] Adicionar `config/settings.ini` ao `.gitignore`.
- [x] Criar `config/settings.example.ini` sem senha real.
- [x] Alterar `ConfigManager` para nao persistir `password`.
- [x] Integrar armazenamento seguro opcional via `keyring` em `utils/credential_store.py`.
- [x] Ajustar `ConnectionPanel` para carregar senha do armazenamento seguro quando disponivel.
- [x] Desabilitar auto-connect quando nao houver senha segura carregada.
- [x] Testar que senha nao aparece no arquivo INI.

## 2. Corrigir Modelo de Threads e Conexao

- [x] Escolher modelo alvo: conexao nova por worker/operacao.
- [x] Remover reutilizacao de cursor/conexao criada por outro worker.
- [x] Fazer `connect` atuar como teste de conexao dentro do worker.
- [x] Fazer operacoes criarem `DatabaseManager` local por thread via `connection_config`.
- [x] Ajustar `DatabaseWorkerFactory` para aceitar `connection_config`.
- [x] Manter cleanup de conexoes locais no final do worker.

## 3. Centralizar Execucao de Operacoes

- [x] Fazer a UI executar operacoes registradas por `operation.execute(...)`.
- [x] Remover o uso efetivo de SQL preview como fonte da execucao.
- [x] Corrigir `BaseOperation._process_result()` para aceitar `QueryResult`.
- [x] Manter exibicao do SQL apenas como preview.
- [x] Cobrir fluxo central com testes unitarios.

## 4. Parametrizar SQL e Validar Entradas

- [x] Ajustar interface de drivers para `execute_query(query, params=None)`.
- [x] Ajustar `DatabaseManager.execute_query(..., params=None)`.
- [x] Parametrizar `CancelarCupomOperation`.
- [x] Parametrizar datas em `ConsultarNCMInexistenteOperation`.
- [x] Validar `numero_caixa` dentro da operacao.
- [x] Integrar `validate_connection_params()` ao fluxo de conexao.
- [x] Escapar valores de connection string ODBC no SQL Server.
- [x] Criar testes para entradas invalidas e parametros bindados.

## 5. Corrigir Configuracao e Caminhos

- [x] Mover config padrao para diretorio gravavel do usuario via `utils/paths.py`.
- [x] Corrigir caminho de JSON empacotado em `NCMManager`.
- [x] Remover caminho absoluto fixo do icone em `MainWindow`.
- [x] Centralizar resolucao de paths da aplicacao em `utils/paths.py`.
- [x] Validar sintaxe com `python -m compileall .`.

## 6. Validar JSON de NCM

- [x] Definir schema minimo esperado para o JSON do Siscomex.
- [x] Validar campos obrigatorios usados pelas regras.
- [x] Rejeitar payload vazio ou malformado antes de cachear.
- [x] Baixar para arquivo temporario e mover apenas apos validacao.
- [x] Registrar origem do arquivo em `get_json_info()`.
- [x] Criar testes para JSON valido e invalido.

## 7. Revisar Logs e Tratamento de Erros

- [x] Remover `traceback.print_exc()` do worker.
- [x] Usar logger sanitizado no erro de operacao customizada.
- [x] Evitar gravar senha em logs/config.
- [x] Trocar prints de cleanup por logger.
- [x] Reduzir risco de connection string sensivel em erro via escape e nao persistencia.

## 8. Corrigir Splash e Dependencias

- [x] Corrigir splash para verificar `firebirdsql`, que e o driver preferido.
- [x] Corrigir caminho do JSON para evitar download desnecessario quando o arquivo empacotado existe.
- [x] Manter falha de NCM/driver como aviso, sem bloquear app.
- [x] Tratar timeout/download como aviso pela logica existente.

## 9. Corrigir Encoding e Textos

- [x] Regravar arquivos centrais alterados em UTF-8 limpo.
- [x] Remover mojibake real dos arquivos Python modificados.
- [x] Conferir busca por padroes `NÃ`, `Ã`, `Â`, `ð` e `�`.
- [x] Manter caracteres acentuados validos quando ja existiam.

## 10. Criar Base de Testes

- [x] Criar estrutura `tests/`.
- [x] Adicionar testes para `ConfigManager`.
- [x] Adicionar testes para `NCMManager`.
- [x] Adicionar testes para `OperationRegistry` e operacoes individuais.
- [x] Adicionar teste para `DatabaseManager` com driver fake.
- [x] Adicionar regressao para `BaseOperation._process_result()`.
- [x] Adicionar teste de seguranca para senha fora do arquivo.
- [x] Atualizar README com comando de teste via `unittest`.

## Verificacao Executada

- [x] `python -m compileall .`
- [x] `python -m unittest discover -s tests`

## Observacoes

- O armazenamento seguro usa `keyring` quando disponivel. Sem `keyring`, a senha nao e persistida, por decisao segura.
- A splash agora verifica `firebirdsql` como driver preferencial. Ambientes que usam apenas `fdb` ainda devem instalar `firebirdsql` ou ajustar a verificacao para aceitar ambos explicitamente.
