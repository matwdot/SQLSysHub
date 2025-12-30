"""
Corrigir Erro de Equipamento Operation

Remove número de série do caixa.
"""

from ..base import BaseOperation


class CorrigirErroEquipamentoOperation(BaseOperation):
    """Remove número de série do caixa."""
    
    def __init__(self):
        super().__init__(
            name="Corrigir Erro de Equipamento",
            description="Remove número de série do caixa"
        )
    
    def get_sql(self, **params) -> str:
        return "UPDATE CAIXA SET CXASERNUM = NULL"