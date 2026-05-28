# Padronizacoes do Projeto

Este projeto e um aplicativo desktop PyQt5 para utilitarios SQL do SysPDV. O codigo deve priorizar seguranca operacional, previsibilidade em banco de dados de cliente e manutencao simples.

## Arquitetura

- Mantenha a separacao atual por camadas:
  - `core/database`: drivers, conexoes e execucao SQL.
  - `core/operations`: regras de negocio e geracao/execucao de operacoes.
  - `core/workers`: execucao assincrona e comunicacao com a UI via sinais.
  - `ui`: componentes visuais e janelas.
  - `utils`: funcoes auxiliares sem dependencia de UI.
  - `config`: leitura e gravacao de configuracoes.
- A UI nao deve conter regra de negocio SQL alem de coletar parametros e disparar operacoes.
- Toda operacao deve ser registrada em `core/operations/registry.py` e implementada em modulo proprio dentro de `core/operations/individual`.
- Evite criar novos singletons globais. Quando necessario, documente o ciclo de vida e quem e dono do recurso.

## Banco de Dados

- Nao execute SQL diretamente pela UI quando existir uma `BaseOperation`; use um fluxo central que chame `validate_params()`, `get_sql()` e processe o resultado.
- Sempre valide parametros antes de montar ou executar SQL.
- Prefira consultas parametrizadas do driver em vez de interpolacao com `f-string`.
- Operacoes destrutivas devem exigir confirmacao explicita na UI e apresentar o escopo da alteracao.
- Nao compartilhe conexao/cursor entre threads sem garantia explicita do driver. A thread que cria a conexao deve ser a dona do uso dela, ou cada worker deve criar sua propria conexao.
- Preserve rollback em falhas e commit apenas apos execucao bem sucedida.

## Seguranca

- Nunca versionar senhas reais, tokens, chaves ou caminhos sensiveis de cliente.
- Nao salvar senha em texto claro no `settings.ini`.
- Se for necessario lembrar credenciais, use armazenamento seguro do sistema operacional, como Windows Credential Manager ou biblioteca equivalente.
- Evite defaults privilegiados como `SYSDBA/masterkey` em arquivos persistidos. Defaults de UI podem existir, mas nao devem ser tratados como segredo salvo.
- Nao imprimir traceback completo em producao quando puder expor SQL, paths, dados de cliente ou credenciais.
- Validar dados baixados de fontes externas por schema, origem e, quando possivel, integridade.

## Configuracao

- `settings.ini` deve armazenar apenas preferencias nao sensiveis.
- O caminho de configuracao deve funcionar tanto em desenvolvimento quanto em empacotamento PyInstaller.
- Em executavel, prefira diretorio gravavel do usuario para configuracoes, nao a pasta do binario.
- Mudancas de configuracao devem ser atomicas o suficiente para evitar arquivo corrompido em encerramento inesperado.

## UI PyQt5

- Componentes devem comunicar eventos por `pyqtSignal`.
- A UI deve permanecer responsiva durante conexao, download e execucao SQL.
- Textos visiveis devem estar em portugues claro e com encoding UTF-8 correto.
- Evite duplicar blocos grandes de estilo e dialogs; extraia helpers quando houver repeticao real.
- A tela de splash deve apenas verificar/carregar recursos sem bloquear indefinidamente a inicializacao.

## NCM / Siscomex

- O JSON de NCM deve ser carregado por `utils/ncm_manager.py`.
- O arquivo local empacotado deve ser usado como fallback confiavel.
- O arquivo baixado pelo usuario deve ser validado antes de substituir ou priorizar dados.
- Alteracoes em regras de vigencia devem ser cobertas por testes com datas fixas.

## Erros e Logs

- Mensagens para usuario devem ser curtas e acionaveis.
- Logs podem conter contexto tecnico, mas nao devem conter senha ou dados sensiveis.
- Evite `except:` amplo. Capture excecoes especificas sempre que possivel.
- Nao silencie erros estruturais; pelo menos registre em log com contexto seguro.

## Testes

- Novas regras em `core` devem ter testes unitarios.
- Operacoes SQL devem ter testes para validacao de parametros e geracao de SQL.
- `NCMManager` deve ter testes para caminho, carga, fallback e schema invalido.
- Workers devem ter testes de fluxo sem depender de banco real, usando dubles/mocks.
- Quando corrigir bug reportado, adicione teste que falharia antes da correcao.

## Estilo de Codigo

- Use UTF-8.
- Prefira type hints em codigo novo.
- Mantenha funcoes pequenas e com responsabilidade clara.
- Comentarios devem explicar decisoes ou riscos, nao repetir o codigo.
- Preserve nomes de operacoes ja exibidos ao usuario, a menos que a mudanca seja planejada.
- Evite refatoracoes grandes junto com correcoes de seguranca; corrija em passos pequenos e verificaveis.
