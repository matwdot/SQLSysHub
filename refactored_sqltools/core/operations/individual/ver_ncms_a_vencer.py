"""
Ver NCMs a Vencer Operation

Consulta NCMs que já venceram ou vencerão em até 90 dias (com paginação).
"""

from ..base import BaseOperation, ValidationError


class VerNCMsAVencerOperation(BaseOperation):
    """Consulta NCMs que já venceram ou vencerão em até 90 dias (com paginação)."""
    
    def __init__(self):
        super().__init__(
            name="Ver NCMs a Vencer",
            description="Consulta NCMs que já venceram ou vencerão em até 90 dias (com paginação)"
        )
    
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
    
    def get_sql(self, **params) -> str:
        registros_por_pagina = int(params['registros_por_pagina'])
        pagina = int(params['pagina'])
        
        # Calculate offset and limit for pagination
        offset = (pagina - 1) * registros_por_pagina + 1
        limit = offset + registros_por_pagina - 1
        
        return f"""SELECT 
    p.PROCOD AS CODIGO,
    p.PRODES AS DESCRICAO,
    p.PRONCM AS NCM,
    n.NCMDES AS DESCRICAO_NCM,
    n.NCMFIMVIG AS FIM_VIGENCIA,
    CURRENT_DATE AS DATA_ATUAL,
    DATEDIFF(DAY FROM CURRENT_DATE TO n.NCMFIMVIG) AS DIAS_PARA_VENCER
FROM PRODUTO p
LEFT JOIN NCM n ON n.NCMCOD = p.PRONCM
WHERE n.NCMFIMVIG IS NOT NULL
    AND (n.NCMFIMVIG < CURRENT_DATE
         OR n.NCMFIMVIG <= DATEADD(90 DAY TO CURRENT_DATE))
ORDER BY n.NCMFIMVIG, p.PRONCM
ROWS {offset} TO {limit}"""
    
    def get_check_sql(self) -> str:
        """SQL para verificar o total de registros."""
        return """SELECT COUNT(*) AS TOTAL_REGISTROS
FROM PRODUTO p
LEFT JOIN NCM n ON n.NCMCOD = p.PRONCM
WHERE n.NCMFIMVIG IS NOT NULL
    AND (n.NCMFIMVIG < CURRENT_DATE
         OR n.NCMFIMVIG <= DATEADD(90 DAY TO CURRENT_DATE))"""