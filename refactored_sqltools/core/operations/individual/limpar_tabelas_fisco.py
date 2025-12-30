"""
Limpar Tabelas do Fisco Operation

Remove todos os dados das tabelas fiscais.
"""

from ..base import BaseOperation


class LimparTabelasFiscoOperation(BaseOperation):
    """Remove todos os dados das tabelas fiscais."""
    
    def __init__(self):
        super().__init__(
            name="Limpar Tabelas do Fisco",
            description="Remove todos os dados das tabelas fiscais"
        )
    
    def get_sql(self, **params) -> str:
        return """EXECUTE BLOCK AS BEGIN
  DELETE FROM FISCO_PRODUTOAUX;
  DELETE FROM FISCO_DOCUMENTOFISCAL;
  DELETE FROM FISCO_CUPOMFISCAL;
  DELETE FROM FISCO_INVENTARIO;
  DELETE FROM FISCO_REDUCAO;
  DELETE FROM FISCO_ITEMDOCUMENTOFISCAL;
  DELETE FROM FISCO_ITEMCUPOMFISCAL;
  DELETE FROM FISCO_PRODUTO;
  DELETE FROM FISCO_ITEMINVENTARIO;
END"""