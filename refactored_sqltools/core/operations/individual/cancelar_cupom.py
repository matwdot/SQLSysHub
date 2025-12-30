"""
Cancelar Cupom Operation

Cancela todos os cupons (STACUP e STACUPVRF = 'F').
"""

from ..base import BaseOperation


class CancelarCupomOperation(BaseOperation):
    """Cancela todos os cupons (STACUP e STACUPVRF = 'F')."""
    
    def __init__(self):
        super().__init__(
            name="Cancelar Cupom",
            description="Cancela todos os cupons (STACUP e STACUPVRF = 'F')"
        )
    
    def get_sql(self, **params) -> str:
        return "UPDATE CAIXA SET STACUP='F', STACUPVRF='F'"
    
    def get_check_sql(self) -> str:
        """SQL para verificar o estado atual antes da operação."""
        return "SELECT STACUP, STACUPVRF FROM CAIXA"