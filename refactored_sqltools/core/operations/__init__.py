"""
Database operations layer.
"""

from .base import BaseOperation, OperationResult
from .registry import OperationRegistry, operation_registry
from ...utils.exceptions import ValidationError

# Import individual operations for direct access if needed
from .individual.cancelar_cupom import CancelarCupomOperation
from .individual.apagar_certificado import ApagarCertificadoOperation
from .individual.corrigir_erro_equipamento import CorrigirErroEquipamentoOperation
from .individual.limpar_tabelas_fisco import LimparTabelasFiscoOperation
from .individual.consultar_ncm_inexistente import ConsultarNCMInexistenteOperation
from .individual.ver_ncms_a_vencer import VerNCMsAVencerOperation

__all__ = [
    'BaseOperation', 
    'OperationResult', 
    'ValidationError',
    'OperationRegistry',
    'operation_registry',
    # Individual operations
    'CancelarCupomOperation',
    'ApagarCertificadoOperation',
    'CorrigirErroEquipamentoOperation',
    'LimparTabelasFiscoOperation',
    'ConsultarNCMInexistenteOperation',
    'VerNCMsAVencerOperation'
]