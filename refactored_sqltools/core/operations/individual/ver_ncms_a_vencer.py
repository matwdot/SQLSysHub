"""
Ver NCMs a Vencer Operation

Consulta NCMs usando arquivo JSON local para verificar vigência atualizada,
considerando vendas do último ano (com paginação).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..base import BaseOperation, ValidationError, OperationResult


class VerNCMsAVencerOperation(BaseOperation):
    """Consulta NCMs usando arquivo JSON local para verificar vigência atualizada, considerando vendas do último ano."""
    
    def __init__(self):
        super().__init__(
            name="Ver NCMs a Vencer",
            description='Consulta NCMs usando arquivo JSON local para verificar vigência atualizada, considerando vendas do último ano.<br><br>📎 <a href="https://portalunico.siscomex.gov.br/classif/#/sumario?perfil=publico">Link para consulta de NCMs</a>'
        )
        self._ncm_cache = None  # Cache para dados do arquivo JSON
    
    def _load_ncm_data_from_json(self) -> Optional[Dict[str, Dict]]:
        """
        Busca dados de NCMs do arquivo JSON local usando o NCMManager global.
        
        Returns:
            Dict com NCMs indexados por código, ou None se houver erro
        """
        if self._ncm_cache is not None:
            return self._ncm_cache
            
        try:
            # Usar o NCMManager global (já carregado na splash screen)
            from refactored_sqltools.utils.ncm_manager import get_ncm_manager
            
            ncm_manager = get_ncm_manager()
            ncm_data = ncm_manager.get_ncm_data()
            
            if ncm_data is not None:
                self._ncm_cache = ncm_data
                print(f"✅ Dados NCM obtidos do cache global: {len(ncm_data)} NCMs")
                print(f"📅 Data da última atualização: {ncm_manager.get_last_update()}")
                return ncm_data
            
            # Fallback: tentar carregar diretamente se não estiver no cache
            print("📁 Cache global vazio, tentando carregar arquivo JSON...")
            success, msg = ncm_manager.load_json()
            
            if success:
                self._ncm_cache = ncm_manager.get_ncm_data()
                print(f"✅ {msg}")
                return self._ncm_cache
            else:
                print(f"❌ {msg}")
                return None
            
        except Exception as e:
            print(f"❌ Erro ao obter dados NCM: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Converte string de data DD/MM/YYYY para datetime.
        
        Args:
            date_str: Data no formato DD/MM/YYYY
            
        Returns:
            datetime object ou None se inválida
        """
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except Exception:
            return None
    
    def _get_ncm_status(self, ncm_code: str, ncm_data: Dict) -> Dict:
        """
        Determina o status de vigência do NCM baseado nos dados da API.
        
        Args:
            ncm_code: Código do NCM
            ncm_data: Dados da API do Siscomex
            
        Returns:
            Dict com informações do status
        """
        if not ncm_data or ncm_code not in ncm_data:
            return {
                'fim_vigencia': 'NCM NÃO ENCONTRADO',
                'status': 'NCM NÃO ENCONTRADO',
                'data_fim_api': None,
                'deve_mostrar': True  # Mostra NCMs não encontrados para análise
            }
        
        ncm_info = ncm_data[ncm_code]
        data_fim_str = ncm_info.get('Data_Fim', '')
        data_fim = self._parse_date(data_fim_str)
        
        if not data_fim:
            return {
                'fim_vigencia': data_fim_str or 'DATA INVÁLIDA',
                'status': 'DATA INVÁLIDA',
                'data_fim_api': None,
                'deve_mostrar': True  # Mostra datas inválidas para análise
            }
        
        hoje = datetime.now()
        
        # Se data fim é 31/12/9999, considera como vigente indefinidamente
        if data_fim.year == 9999:
            return {
                'fim_vigencia': data_fim_str,
                'status': 'VIGENTE',
                'data_fim_api': data_fim,
                'deve_mostrar': False  # NÃO mostra NCMs vigentes indefinidamente
            }
        
        # Calcular status baseado na proximidade do vencimento
        dias_restantes = (data_fim - hoje).days
        
        if data_fim < hoje:
            status = 'VENCIDO'
            deve_mostrar = True
        elif dias_restantes <= 5:
            status = 'A VENCER (próximo)'
            deve_mostrar = True
        elif dias_restantes <= 365:
            status = 'A VENCER'
            deve_mostrar = True
        else:
            status = 'VIGENTE'
            deve_mostrar = False  # NÃO mostra NCMs com mais de 365 dias
        
        return {
            'fim_vigencia': data_fim_str,
            'status': status,
            'data_fim_api': data_fim,
            'deve_mostrar': deve_mostrar,
            'dias_restantes': dias_restantes if data_fim >= hoje else f"Vencido há {abs(dias_restantes)} dias"
        }
    def validate_params(self, **params) -> bool:
        """Validate pagination parameters."""
        required_params = ['registros_por_pagina', 'pagina']
        self._validate_required_params(required_params, **params)
        
        try:
            registros_por_pagina = int(params['registros_por_pagina'])
            pagina = int(params['pagina'])
            
            if registros_por_pagina <= 0:
                raise ValidationError("Registros por página deve ser maior que zero")
            if pagina <= 0:
                raise ValidationError("Página deve ser maior que zero")
                
        except ValueError:
            raise ValidationError("Registros por página e página devem ser números inteiros")
            
        return True
    
    def execute(self, db_manager, **params) -> OperationResult:
        """
        Execute a operação consultando o arquivo JSON local para dados atualizados.
        Se o arquivo falhar, usa dados locais da tabela NCM como fallback.
        """
        try:
            # Validar parâmetros
            self.validate_params(**params)
            
            # Tentar buscar dados do arquivo JSON
            print("📁 Tentando carregar dados do arquivo JSON local...")
            ncm_data = self._load_ncm_data_from_json()
            
            if ncm_data is None:
                # Fallback: usar dados locais da tabela NCM
                print("⚠️ Arquivo JSON indisponível, usando dados locais da tabela NCM...")
                return self._execute_with_local_data(db_manager, **params)
            
            # Usar dados do arquivo JSON
            print(f"✅ Arquivo JSON carregado com sucesso! Processando com {len(ncm_data)} NCMs...")
            return self._execute_with_api_data(db_manager, ncm_data, **params)
            
        except ValidationError as e:
            return OperationResult(
                success=False,
                message=f"Erro de validação: {str(e)}"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                message=f"Falha na operação: {str(e)}"
            )
    
    def _execute_with_api_data(self, db_manager, ncm_data: Dict, **params) -> OperationResult:
        """Executa usando APENAS dados do arquivo JSON local para determinar vigência."""
        # Buscar produtos com NCM do banco (query simplificada - sem dados de vigência do banco)
        sql_produtos = self.get_sql(**params)
        result = db_manager.execute_query(sql_produtos)
        
        # QueryResult é um objeto, não um dicionário
        if not result.success:
            return OperationResult(
                success=False,
                message=f"Falha ao consultar produtos no banco de dados: {result.message}"
            )
        
        # Processar resultados usando APENAS dados do arquivo JSON
        produtos = result.data or []
        colunas_resultado = [
            'CODIGO', 'DESCRICAO', 'NCM', 
            'FIM_VIGENCIA', 'STATUS', 'QTD_VENDIDA_ANO'
        ]
        
        dados_processados = []
        
        print(f"📊 Processando {len(produtos)} produtos usando dados do arquivo JSON...")
        
        for produto in produtos:
            # Query retorna: CODIGO, DESCRICAO, NCM, QTD_VENDIDA_ANO
            codigo, descricao, ncm, qtd_vendida = produto
            
            # Obter status do arquivo JSON
            ncm_status = self._get_ncm_status(str(ncm), ncm_data)
            
            # Filtrar: mostrar apenas NCMs vencidos, a vencer ou não encontrados
            if ncm_status.get('deve_mostrar', False):
                dados_processados.append([
                    codigo,
                    descricao,
                    ncm,
                    ncm_status['fim_vigencia'],  # Data do JSON
                    ncm_status['status'],  # Status do JSON
                    qtd_vendida or 0
                ])
        
        print(f"✅ Processamento concluído: {len(dados_processados)} NCMs vencidos/a vencer encontrados")
        
        # Ordenar por prioridade de status e quantidade vendida
        def sort_key(item):
            status = item[4]  # coluna STATUS
            qtd_vendida = item[5]  # coluna QTD_VENDIDA_ANO
            
            # Prioridade por status
            if status == 'NCM NÃO ENCONTRADO':
                prioridade = 1
            elif status == 'DATA INVÁLIDA':
                prioridade = 2
            elif status == 'VENCIDO':
                prioridade = 3
            elif status == 'A VENCER (próximo)':
                prioridade = 4
            elif status == 'A VENCER':
                prioridade = 5
            else:
                prioridade = 6
                
            return (prioridade, -qtd_vendida)
        
        dados_processados.sort(key=sort_key)
        
        # Aplicar paginação
        registros_por_pagina = int(params['registros_por_pagina'])
        pagina = int(params['pagina'])
        inicio = (pagina - 1) * registros_por_pagina
        fim = inicio + registros_por_pagina
        
        dados_pagina = dados_processados[inicio:fim]
        
        return OperationResult(
            success=True,
            message=f"✅ Consulta executada com dados do arquivo JSON. {len(dados_pagina)} linhas (Total: {len(dados_processados)} NCMs vencidos/a vencer).",
            data=dados_pagina,
            columns=colunas_resultado,
            source="JSON"
        )
    
    def _execute_with_local_data(self, db_manager, **params) -> OperationResult:
        """Executa usando dados locais da tabela NCM como fallback (quando arquivo JSON não está disponível)."""
        registros_por_pagina = int(params['registros_por_pagina'])
        pagina = int(params['pagina'])
        
        offset = (pagina - 1) * registros_por_pagina + 1
        limit = offset + registros_por_pagina - 1
        
        # Query usando tabela NCM do banco como fallback
        sql_local = f"""WITH vendas_ano AS (
    SELECT 
        i.PROCOD,
        SUM(i.ITVQTDVDA) AS QTD_VENDIDA
    FROM ITEVDA i
    WHERE i.TRNDAT >= DATEADD(-365 DAY TO CURRENT_DATE)
      AND i.ITVQTDVDA > 0
    GROUP BY i.PROCOD
    HAVING SUM(i.ITVQTDVDA) > 0
)
SELECT
    p.PROCOD AS CODIGO,
    p.PRODES AS DESCRICAO,
    p.PRONCM AS NCM,
    n.NCMFIMVIG AS FIM_VIGENCIA,
    CASE
        WHEN n.NCMFIMVIG < CURRENT_DATE THEN 'VENCIDO'
        WHEN DATEDIFF(DAY, n.NCMFIMVIG, CURRENT_DATE) <= 5 THEN 'A VENCER (próximo)'
        ELSE 'A VENCER'
    END AS STATUS,
    COALESCE(v.QTD_VENDIDA, 0) AS QTD_VENDIDA_ANO
FROM PRODUTO p
INNER JOIN NCM n ON n.NCMCOD = p.PRONCM
LEFT JOIN vendas_ano v ON v.PROCOD = p.PROCOD
WHERE n.NCMFIMVIG IS NOT NULL
  AND (n.NCMFIMVIG < CURRENT_DATE
       OR n.NCMFIMVIG <= DATEADD(365 DAY TO CURRENT_DATE))
ORDER BY
    COALESCE(v.QTD_VENDIDA, 0) DESC
ROWS {offset} TO {limit};"""
        
        result = db_manager.execute_query(sql_local)
        
        # QueryResult é um objeto, não um dicionário
        if result.success:
            data = result.data or []
            columns = ['CODIGO', 'DESCRICAO', 'NCM', 'FIM_VIGENCIA', 'STATUS', 'QTD_VENDIDA_ANO']
            
            return OperationResult(
                success=True,
                message=f"⚠️ Consulta executada com dados do BANCO (arquivo JSON indisponível). {len(data)} linhas.\n\nNota: Dados podem estar desatualizados.",
                data=data,
                columns=columns,
                source="BANCO"
            )
        else:
            return OperationResult(
                success=False,
                message=f"❌ Falha ao consultar dados: {result.message}"
            )
    
    def get_sql(self, **params) -> str:
        """
        SQL para buscar produtos com NCM e vendas.
        NÃO filtra por vigência do banco - isso será feito pelo arquivo JSON.
        """
        return """WITH vendas_ano AS (
    SELECT i.PROCOD, SUM(i.ITVQTDVDA) AS QTD_VENDIDA
    FROM ITEVDA i
    WHERE i.TRNDAT >= DATEADD(-365 DAY TO CURRENT_DATE)
      AND i.ITVQTDVDA > 0
    GROUP BY i.PROCOD
    HAVING SUM(i.ITVQTDVDA) > 0
)
SELECT
    p.PROCOD AS CODIGO,
    p.PRODES AS DESCRICAO,
    p.PRONCM AS NCM,
    COALESCE(v.QTD_VENDIDA, 0) AS QTD_VENDIDA_ANO
FROM PRODUTO p
LEFT JOIN vendas_ano v ON v.PROCOD = p.PROCOD
WHERE p.PRONCM IS NOT NULL
  AND TRIM(p.PRONCM) <> ''
ORDER BY 4 DESC;"""
    
    def get_check_sql(self) -> str:
        """SQL para verificar o total de produtos com NCM."""
        return """SELECT COUNT(*) AS TOTAL_REGISTROS
FROM PRODUTO p
WHERE p.PRONCM IS NOT NULL
  AND p.PRONCM <> ''
  AND EXISTS (
      SELECT 1 FROM ITEVDA i
      WHERE i.PROCOD = p.PROCOD 
        AND i.TRNDAT >= DATEADD(-365 DAY TO CURRENT_DATE)
        AND i.ITVQTDVDA > 0
  );"""
