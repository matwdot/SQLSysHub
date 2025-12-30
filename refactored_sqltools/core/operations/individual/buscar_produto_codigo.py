"""
Buscar Produto por Código Operation

Busca um produto específico pelo código.
"""

from ..base import BaseOperation, ValidationError


class BuscarProdutoCodigoOperation(BaseOperation):
    """Busca um produto específico pelo código."""
    
    def __init__(self):
        super().__init__(
            name="Buscar Produto por Código",
            description="Busca um produto específico pelo código (execução automática)"
        )
    
    def validate_params(self, **params) -> bool:
        """Validate product code parameter."""
        required_params = ['codigo_produto']
        self._validate_required_params(required_params, **params)
        
        codigo_produto = params['codigo_produto'].strip()
        if not codigo_produto:
            raise ValidationError("Código do produto não pode estar vazio")
            
        return True
    
    def get_sql(self, **params) -> str:
        codigo_produto = params['codigo_produto'].strip()
        
        return f"""SELECT PROCOD AS CODIGO, PRODES AS DESCRICAO, PRONCM AS NCM
FROM PRODUTO
WHERE PROCOD = '{codigo_produto}'
ORDER BY PRONCM;"""