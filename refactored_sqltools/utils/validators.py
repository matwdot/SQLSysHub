"""
Input validation utilities for the SQL SysHub refactored system.

This module provides validation functions for database connections,
date ranges, file paths, and other input parameters used throughout
the application.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from .exceptions import ValidationError


def validate_connection_params(db_type: str, **params) -> bool:
    """
    Validate database connection parameters.
    
    Args:
        db_type (str): Database type ('firebird' or 'sqlserver')
        **params: Connection parameters to validate
        
    Returns:
        bool: True if parameters are valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not db_type:
        raise ValidationError("Tipo de banco de dados é obrigatório")
    
    db_type = db_type.lower()
    
    if db_type == 'firebird':
        return _validate_firebird_params(**params)
    elif db_type in ('sqlserver', 'sql server'):
        return _validate_sqlserver_params(**params)
    else:
        raise ValidationError(f"Tipo de banco não suportado: {db_type}")


def _validate_firebird_params(**params) -> bool:
    """
    Validate Firebird connection parameters.
    
    Args:
        **params: Firebird connection parameters
        
    Returns:
        bool: True if parameters are valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    # Required parameters
    required_params = ['database']
    _validate_required_params(required_params, **params)
    
    # Validate database path
    database = params.get('database', '')
    if not validate_firebird_database_path(database, params.get('host', 'localhost')):
        raise ValidationError(f"Caminho do banco Firebird inválido: {database}")
    
    # Validate optional parameters
    host = params.get('host', 'localhost')
    port = params.get('port', '3050')
    username = params.get('username', 'SYSDBA')
    password = params.get('password', '')
    
    # Validate host format
    if not _validate_host_format(host):
        raise ValidationError(f"Formato de host inválido: {host}")
    
    # Validate port
    if not _validate_port(port):
        raise ValidationError(f"Número de porta inválido: {port}")
    
    # Validate username (basic check)
    if not username or len(username.strip()) == 0:
        raise ValidationError("Nome de usuário não pode estar vazio")
    
    return True


def _validate_sqlserver_params(**params) -> bool:
    """
    Validate SQL Server connection parameters.
    
    Args:
        **params: SQL Server connection parameters
        
    Returns:
        bool: True if parameters are valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    # Required parameters
    required_params = ['database']
    _validate_required_params(required_params, **params)
    
    # Validate optional parameters
    host = params.get('host', 'localhost')
    port = params.get('port', '1433')
    username = params.get('username', 'sa')
    password = params.get('password', '')
    database = params.get('database', 'master')
    
    # Validate host format
    if not _validate_host_format(host):
        raise ValidationError(f"Formato de host inválido: {host}")
    
    # Validate port
    if not _validate_port(port):
        raise ValidationError(f"Número de porta inválido: {port}")
    
    # Validate username (basic check)
    if not username or len(username.strip()) == 0:
        raise ValidationError("Nome de usuário não pode estar vazio")
    
    # Validate database name format
    if not _validate_database_name(database):
        raise ValidationError(f"Nome de banco inválido: {database}")
    
    return True


def validate_firebird_database_path(database_path: str, host: str = 'localhost') -> bool:
    """
    Validate Firebird database file path.
    
    Args:
        database_path (str): Path to Firebird database file
        host (str): Database host (default: localhost)
        
    Returns:
        bool: True if path is valid
        
    Raises:
        ValidationError: If path is invalid
    """
    if not database_path or len(database_path.strip()) == 0:
        raise ValidationError("Caminho do banco não pode estar vazio")
    
    database_path = database_path.strip()
    
    # For local connections, validate file existence
    if host.lower() in ['localhost', '127.0.0.1', '']:
        if not os.path.exists(database_path):
            raise ValidationError(f"Arquivo de banco não encontrado: {database_path}")
        
        if not os.path.isfile(database_path):
            raise ValidationError(f"Caminho do banco não é um arquivo: {database_path}")
        
        # Check file extension (common Firebird extensions)
        valid_extensions = ['.fdb', '.gdb', '.db']
        file_ext = os.path.splitext(database_path)[1].lower()
        if file_ext not in valid_extensions:
            # Warning but not error - Firebird can use any extension
            pass
    
    # For remote connections, basic path format validation
    else:
        # Check for invalid characters in path
        invalid_chars = ['<', '>', '|', '"', '*', '?']
        if any(char in database_path for char in invalid_chars):
            raise ValidationError(f"Caminho do banco contém caracteres inválidos: {database_path}")
    
    return True


def validate_date_range(data_inicio: str, data_fim: str) -> bool:
    """
    Validate date range parameters for NCM queries.
    
    Args:
        data_inicio (str): Start date in YYYY-MM-DD format
        data_fim (str): End date in YYYY-MM-DD format
        
    Returns:
        bool: True if date range is valid
        
    Raises:
        ValidationError: If date format or range is invalid
    """
    if not data_inicio or not data_fim:
        raise ValidationError("Datas de início e fim são obrigatórias")
    
    try:
        start_date = datetime.strptime(data_inicio, '%Y-%m-%d')
        end_date = datetime.strptime(data_fim, '%Y-%m-%d')
        
        if start_date > end_date:
            raise ValidationError("Data de início deve ser anterior ou igual à data de fim")
        
        # Check for reasonable date range (not too far in the past or future)
        current_date = datetime.now()
        min_date = datetime(2000, 1, 1)  # Reasonable minimum date
        max_date = datetime(current_date.year + 1, 12, 31)  # One year in the future
        
        if start_date < min_date or end_date < min_date:
            raise ValidationError(f"Datas não podem ser anteriores a {min_date.strftime('%Y-%m-%d')}")
        
        if start_date > max_date or end_date > max_date:
            raise ValidationError(f"Datas não podem ser posteriores a {max_date.strftime('%Y-%m-%d')}")
        
        return True
        
    except ValueError as e:
        raise ValidationError(f"Formato de data inválido. Use o formato AAAA-MM-DD: {str(e)}")


def _validate_required_params(required_params: List[str], **params) -> bool:
    """
    Validate that all required parameters are present and not empty.
    
    Args:
        required_params (List[str]): List of required parameter names
        **params: Provided parameters
        
    Returns:
        bool: True if all required parameters are present
        
    Raises:
        ValidationError: If any required parameter is missing or empty
    """
    missing_params = []
    empty_params = []
    
    for param in required_params:
        if param not in params:
            missing_params.append(param)
        elif params[param] is None or (isinstance(params[param], str) and len(params[param].strip()) == 0):
            empty_params.append(param)
    
    if missing_params:
        raise ValidationError(f"Parâmetros obrigatórios ausentes: {', '.join(missing_params)}")
    
    if empty_params:
        raise ValidationError(f"Parâmetros obrigatórios vazios: {', '.join(empty_params)}")
    
    return True


def _validate_host_format(host: str) -> bool:
    """
    Validate host format (IP address or hostname).
    
    Args:
        host (str): Host to validate
        
    Returns:
        bool: True if host format is valid
    """
    if not host or len(host.strip()) == 0:
        return False
    
    host = host.strip()
    
    # Check for localhost variations
    if host.lower() in ['localhost', '127.0.0.1', '::1']:
        return True
    
    # Basic IP address validation (IPv4)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, host):
        # Validate IP octets
        octets = host.split('.')
        for octet in octets:
            if int(octet) > 255:
                return False
        return True
    
    # Basic hostname validation
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(hostname_pattern, host))


def _validate_port(port: str) -> bool:
    """
    Validate port number.
    
    Args:
        port (str): Port number to validate
        
    Returns:
        bool: True if port is valid
    """
    if not port:
        return False
    
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False


def _validate_database_name(database_name: str) -> bool:
    """
    Validate database name format.
    
    Args:
        database_name (str): Database name to validate
        
    Returns:
        bool: True if database name is valid
    """
    if not database_name or len(database_name.strip()) == 0:
        return False
    
    database_name = database_name.strip()
    
    # Basic database name validation
    # Allow alphanumeric, underscore, hyphen, and dot
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    if not re.match(pattern, database_name):
        return False
    
    # Check length (reasonable limits)
    if len(database_name) > 128:
        return False
    
    return True


def validate_sql_query(query: str) -> bool:
    """
    Basic SQL query validation.
    
    Args:
        query (str): SQL query to validate
        
    Returns:
        bool: True if query appears valid
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or len(query.strip()) == 0:
        raise ValidationError("Query SQL não pode estar vazia")
    
    query = query.strip()
    
    # Check for basic SQL injection patterns (basic protection)
    dangerous_patterns = [
        r';\s*drop\s+',
        r';\s*delete\s+',
        r';\s*truncate\s+',
        r';\s*alter\s+',
        r';\s*create\s+',
        r'--\s*',
        r'/\*.*\*/',
    ]
    
    query_lower = query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            raise ValidationError(f"Query contém padrão potencialmente perigoso: {pattern}")
    
    return True
