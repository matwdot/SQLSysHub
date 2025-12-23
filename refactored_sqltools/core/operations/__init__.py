"""
Database operations layer.
"""

from .base import BaseOperation, OperationResult, ValidationError
from .predefined import (
    CancelarCupomOperation,
    ApagarCertificadoOperation,
    CorrigirErroEquipamentoOperation,
    LimparTabelasFiscoOperation,
    # ConsultarTransacoesOperation,  # Removida
    # ConsultarProprioOperation,     # Removida
    ConsultarNCMInexistenteOperation,
    OperationRegistry,
    operation_registry
)

__all__ = [
    'BaseOperation', 
    'OperationResult', 
    'ValidationError',
    'CancelarCupomOperation',
    'ApagarCertificadoOperation',
    'CorrigirErroEquipamentoOperation',
    'LimparTabelasFiscoOperation',
    # 'ConsultarTransacoesOperation',  # Removida
    # 'ConsultarProprioOperation',     # Removida
    'ConsultarNCMInexistenteOperation',
    'OperationRegistry',
    'operation_registry'
]