"""
Operation Registry

Centralized registry for all database operations.
Imports operations from individual modules for better maintainability.
"""

from typing import Dict, Any
from .base import BaseOperation

# Import individual operations
from .individual.cancelar_cupom import CancelarCupomOperation
from .individual.apagar_certificado import ApagarCertificadoOperation
from .individual.corrigir_erro_equipamento import CorrigirErroEquipamentoOperation
from .individual.limpar_tabelas_fisco import LimparTabelasFiscoOperation
from .individual.consultar_ncm_inexistente import ConsultarNCMInexistenteOperation
from .individual.ver_ncms_a_vencer import VerNCMsAVencerOperation
from .individual.buscar_produto_codigo import BuscarProdutoCodigoOperation


class OperationRegistry:
    """Registry for all predefined operations."""
    
    def __init__(self):
        self._operations = {}
        self._operation_types = {
            "PDV": [
                "Cancelar Cupom",
                "Corrigir Erro de Equipamento"
            ],
            "Server": [
                "Limpar Tabelas do Fisco",
                "Consultar NCM Inexistente",
                "Ver NCMs a Vencer",
                "Buscar Produto por Código"
            ],
            "Ambos": [
                "Apagar Certificado"
            ]
        }
        self._sessions = {
            "SysPDV PDV": [
                "Cancelar Cupom",
                "Corrigir Erro de Equipamento"
            ],
            "SysPDV Server": [
                "Limpar Tabelas do Fisco",
                "Consultar NCM Inexistente",
                "Ver NCMs a Vencer",
                "Buscar Produto por Código"
            ],
            "Outros": [
                "Apagar Certificado"
            ]
        }
        self._register_operations()
    
    def _register_operations(self):
        """Register all predefined operations."""
        operations = [
            CancelarCupomOperation(),
            ApagarCertificadoOperation(),
            CorrigirErroEquipamentoOperation(),
            LimparTabelasFiscoOperation(),
            ConsultarNCMInexistenteOperation(),
            VerNCMsAVencerOperation(),
            BuscarProdutoCodigoOperation(),
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
    
    def get_operations_by_session(self) -> Dict[str, Dict[str, BaseOperation]]:
        """
        Get operations organized by sessions (compatibility method).
        
        Returns:
            Dict[str, Dict[str, BaseOperation]]: Operations grouped by session
        """
        return self.get_operations_by_type()
    
    def get_operations_by_type(self, operation_types: list = None) -> Dict[str, Dict[str, BaseOperation]]:
        """
        Get operations organized by sessions, filtered by operation types.
        
        Args:
            operation_types: List of types to include ('PDV', 'Server', 'Ambos'). 
                           If None, returns all operations.
        
        Returns:
            Dict[str, Dict[str, BaseOperation]]: Operations grouped by session
        """
        if operation_types is None:
            operation_types = ['PDV', 'Server', 'Ambos']
        
        # Get all operations that match the selected types
        allowed_operations = set()
        for op_type in operation_types:
            if op_type in self._operation_types:
                allowed_operations.update(self._operation_types[op_type])
        
        result = {}
        for session_name, operation_names in self._sessions.items():
            session_operations = {}
            for operation_name in operation_names:
                if operation_name in allowed_operations and operation_name in self._operations:
                    session_operations[operation_name] = self._operations[operation_name]
            
            # Only add session if it has operations
            if session_operations:
                result[session_name] = session_operations
        
        return result
    
    def get_operation_type(self, operation_name: str) -> str:
        """
        Get the type of an operation (PDV, Server, or Ambos).
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            str: Type of the operation ('PDV', 'Server', 'Ambos', or 'Unknown')
        """
        for op_type, operations in self._operation_types.items():
            if operation_name in operations:
                return op_type
        return 'Unknown'
    
    def get_operation_parameters(self, name: str) -> Dict[str, Any]:
        """
        Get parameter configuration for an operation.
        
        Args:
            name: Operation name
            
        Returns:
            Dict[str, Any]: Parameter configuration
        """
        operation = self.get_operation(name)
        
        # Define parameter configurations for operations that need them
        parameter_configs = {
            "Consultar NCM Inexistente": {
                "data_inicio": {
                    "type": "date",
                    "label": "Data Início",
                    "default": "month_ago"
                },
                "data_fim": {
                    "type": "date", 
                    "label": "Data Fim",
                    "default": "today"
                }
            },
            "Ver NCMs a Vencer": {
                "registros_por_pagina": {
                    "type": "text",
                    "label": "Registros por Página",
                    "default": "100",
                    "placeholder": "Ex: 100, 500, 1000"
                },
                "pagina": {
                    "type": "text",
                    "label": "Página",
                    "default": "1",
                    "placeholder": "Número da página (1, 2, 3...)"
                }
            },
            "Buscar Produto por Código": {
                "codigo_produto": {
                    "type": "text",
                    "label": "Código do Produto",
                    "placeholder": "Digite o código do produto"
                }
            }
        }
        
        return parameter_configs.get(name, {})
    
    def has_parameters(self, name: str) -> bool:
        """
        Check if operation requires parameters.
        
        Args:
            name: Operation name
            
        Returns:
            bool: True if operation requires parameters
        """
        return bool(self.get_operation_parameters(name))
    
    def add_operation(self, operation: BaseOperation):
        """
        Add a new operation to the registry.
        
        Args:
            operation: Operation instance to add
        """
        self._operations[operation.name] = operation
    
    def remove_operation(self, name: str):
        """
        Remove an operation from the registry.
        
        Args:
            name: Operation name to remove
            
        Raises:
            KeyError: If operation not found
        """
        if name not in self._operations:
            raise KeyError(f"Operação '{name}' não encontrada")
        del self._operations[name]


# Global registry instance
operation_registry = OperationRegistry()