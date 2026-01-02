"""
Cancelar Cupom Operation

Cancela todos os cupons (STACUP e STACUPVRF = 'F').
Permite filtrar por número de caixa específico.
"""

from ..base import BaseOperation


class CancelarCupomOperation(BaseOperation):
    """Cancela todos os cupons (STACUP e STACUPVRF = 'F')."""
    
    def __init__(self):
        super().__init__(
            name="Cancelar Cupom",
            description="Cancela cupons (STACUP e STACUPVRF = 'F') - pode filtrar por caixa"
        )
    
    def get_sql(self, **params) -> str:
        numero_caixa = params.get('numero_caixa', '').strip()
        todos_caixas = params.get('todos_caixas', True)
        
        if todos_caixas or not numero_caixa:
            return "UPDATE CAIXA SET STACUP='F', STACUPVRF='F'"
        else:
            return f"UPDATE CAIXA SET STACUP='F', STACUPVRF='F' WHERE CXANUM = {numero_caixa}"
    
    def get_check_sql(self) -> str:
        """SQL para verificar o estado atual antes da operação."""
        return "SELECT CXANUM, STACUP, STACUPVRF FROM CAIXA ORDER BY CXANUM"