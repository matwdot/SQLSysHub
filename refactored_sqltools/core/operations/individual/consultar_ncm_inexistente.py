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
            description='Consulta transações com NCM inexistente no período.<br><br>📎 <a href="https://portalunico.siscomex.gov.br/classif/#/sumario?perfil=publico">Link para consulta de NCMs</a>'
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
    T.TRNNFCENUM AS NOTA,
    T.TRNDAT AS DATA_EMISSAO,
    i.PROCOD AS PRODUTO,
    p.PRODES AS DESCRICAO_PRODUTO,
    T.CXANUM AS CAIXA,
    i.ITVSEQ AS SEQ,
    i.ITVNCM AS NCM,
    TX.TRNMENSNFE AS ERRO
FROM TRANSACAO_XMLNOTA TX
INNER JOIN TRANSACAO T
    ON TX.TRNSEQ = T.TRNSEQ
    AND TX.TRNDAT = T.TRNDAT
    AND TX.CXANUM = T.CXANUM
INNER JOIN ITEVDA i
    ON TX.TRNSEQ = i.TRNSEQ
    AND TX.TRNDAT = i.TRNDAT
    AND TX.CXANUM = i.CXANUM
INNER JOIN PRODUTO p
    ON p.PROCOD = i.PROCOD
WHERE
    TX.TRNDAT BETWEEN '{data_inicio}' AND '{data_fim}'
    AND TX.TRNMENSNFE CONTAINING 'Rejeicao: Informado NCM inexistente'
    AND CAST(i.ITVSEQ AS INTEGER) = CAST(
        SUBSTRING(TX.TRNMENSNFE 
            FROM POSITION('nItem:' IN TX.TRNMENSNFE) + 6 
            FOR (POSITION(']' IN TX.TRNMENSNFE) - POSITION('nItem:' IN TX.TRNMENSNFE) - 6)
        ) AS INTEGER
    )
ORDER BY
    T.TRNDAT DESC,
    T.TRNNFCENUM,
    i.ITVSEQ;"""