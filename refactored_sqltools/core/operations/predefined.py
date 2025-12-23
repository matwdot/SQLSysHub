"""
Predefined database operations migrated from original SQL SysHub.py.

This module contains all the predefined operations that were originally
defined in the operations dictionary of the monolithic SQL SysHub.py file.
"""

from typing import Dict, Any
from .base import BaseOperation, ValidationError


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


class ApagarCertificadoOperation(BaseOperation):
    """Remove certificado digital do sistema."""
    
    def __init__(self):
        super().__init__(
            name="Apagar Certificado",
            description="Remove certificado digital do sistema"
        )
    
    def get_sql(self, **params) -> str:
        return """UPDATE PROPRIO
SET PRPCERELE = NULL,
    PRPPWDCER = NULL,
    PRPNUMSERA3 = NULL"""


class CorrigirErroEquipamentoOperation(BaseOperation):
    """Remove número de série do caixa."""
    
    def __init__(self):
        super().__init__(
            name="Corrigir Erro de Equipamento",
            description="Remove número de série do caixa"
        )
    
    def get_sql(self, **params) -> str:
        return "UPDATE CAIXA SET CXASERNUM = NULL"


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


# class ConsultarTransacoesOperation(BaseOperation):
#     """Consulta as transações na tabela TRANSACAO."""
    
#     def __init__(self):
#         super().__init__(
#             name="Consultar Transações",
#             description="Consulta as transações na tabela TRANSACAO"
#         )
    
#     def get_sql(self, **params) -> str:
#         return "SELECT * FROM TRANSACAO"


# class ConsultarProprioOperation(BaseOperation):
#     """Consulta os dados da tabela PROPRIO."""
    
#     def __init__(self):
#         super().__init__(
#             name="Consultar Proprio",
#             description="Consulta os dados da tabela PROPRIO"
#         )
    
#     def get_sql(self, **params) -> str:
#         return "SELECT * FROM PROPRIO"


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


class OperationRegistry:
    """Registry for all predefined operations."""
    
    def __init__(self):
        self._operations = {}
        self._register_operations()
    
    def _register_operations(self):
        """Register all predefined operations."""
        operations = [
            CancelarCupomOperation(),
            ApagarCertificadoOperation(),
            CorrigirErroEquipamentoOperation(),
            LimparTabelasFiscoOperation(),
            # ConsultarTransacoesOperation(),
            # ConsultarProprioOperation(),
            ConsultarNCMInexistenteOperation(),
        ]
        
        for operation in operations:
            self._operations[operation.name] = operation
    
    def get_operation(self, name: str) -> BaseOperation:
        """
        Get operation by name.
        
        Args:
            name: Operation name
            
        Returns:
            BaseOperation: The requested operation
            
        Raises:
            KeyError: If operation not found
        """
        if name not in self._operations:
            raise KeyError(f"Operação '{name}' não encontrada")
        return self._operations[name]
    
    def list_operations(self) -> Dict[str, BaseOperation]:
        """
        Get all registered operations.
        
        Returns:
            Dict[str, BaseOperation]: Dictionary of operation name to operation instance
        """
        return self._operations.copy()
    
    def get_operation_names(self) -> list:
        """
        Get list of all operation names.
        
        Returns:
            list: List of operation names
        """
        return list(self._operations.keys())


# Global registry instance
operation_registry = OperationRegistry()