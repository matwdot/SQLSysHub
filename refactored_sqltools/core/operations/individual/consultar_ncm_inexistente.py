"""
Consultar NCM Inexistente Operation

Consulta transações com NCM inexistente no período.
"""

from ..base import BaseOperation, ValidationError


class ConsultarNCMInexistenteOperation(BaseOperation):
    """Consulta transações com NCM inexistente no período."""
    
    def __init__(self):
        super().__init__(
            name="Consultar NCM Inexistente",
            description="Consulta transações com NCM inexistente no período"
        )
    
    def validate_params(self, **params) -> bool:
        """Validate date range parameters for NCM query."""
        required_params = ['data_inicio', 'data_fim']
        self._validate_required_params(required_params, **params)
        self._validate_date_range(params['data_inicio'], params['data_fim'])
        return True
    
    def get_sql(self, **params) -> str:
        data_inicio = params['data_inicio']
        data_fim = params['data_fim']
        
        return f"""SELECT 
    TRNNFCENUM AS NOTA,
    T.TRNDAT AS DATA, 
    PROCOD AS PRODUTO,
    T.CXANUM AS CAIXA,
    ITVSEQ AS SEQ_ITEM,
    ITVNCM AS NCM,
    TRNMENSNFE AS ERRO
FROM TRANSACAO_XMLNOTA tx 
INNER JOIN TRANSACAO t  ON TX.TRNSEQ = T.TRNSEQ AND TX.TRNDAT = T.TRNDAT AND TX.CXANUM = T.CXANUM  
INNER JOIN ITEVDA i ON TX.TRNSEQ = I.TRNSEQ AND TX.TRNDAT = I.TRNDAT AND TX.CXANUM = i.CXANUM  
WHERE 
TX.TRNDAT BETWEEN '{data_inicio}' AND '{data_fim}'
AND TRNMENSNFE LIKE '%Rejeicao: Informado NCM inexistente%'
AND CAST(ITVSEQ AS INTEGER) =
CAST( SUBSTRING(TRNMENSNFE FROM POSITION('nItem:' IN TRNMENSNFE) + 6 FOR POSITION(']' IN TRNMENSNFE)- (POSITION('nItem:' IN TRNMENSNFE) + 6))AS INTEGER);"""