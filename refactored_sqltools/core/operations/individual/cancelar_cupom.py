"""
Cancelar Cupom Operation

Cancela todos os cupons (STACUP e STACUPVRF = 'F').
Permite filtrar por número de caixa específico.
"""

from ..base import BaseOperation
from ....utils.exceptions import ValidationError


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
            return "UPDATE CAIXA SET STACUP='F', STACUPVRF='F' WHERE CXANUM = ?"

    def get_sql_params(self, **params):
        numero_caixa = params.get('numero_caixa', '').strip()
        todos_caixas = params.get('todos_caixas', True)
        if todos_caixas or not numero_caixa:
            return None
        return (int(numero_caixa),)

    def validate_params(self, **params) -> bool:
        todos_caixas = params.get('todos_caixas', True)
        numero_caixa = params.get('numero_caixa', '')

        if isinstance(todos_caixas, str):
            todos_caixas = todos_caixas.lower() in ('true', '1', 'sim', 'yes')

        if todos_caixas:
            return True

        try:
            numero = int(str(numero_caixa).strip())
        except (TypeError, ValueError):
            raise ValidationError("Numero do caixa deve ser um inteiro")

        if numero < 1 or numero > 999:
            raise ValidationError("Numero do caixa deve estar entre 1 e 999")

        return True
    
    def get_check_sql(self) -> str:
        """SQL para verificar o estado atual antes da operação."""
        return "SELECT CXANUM, STACUP, STACUPVRF FROM CAIXA ORDER BY CXANUM"
