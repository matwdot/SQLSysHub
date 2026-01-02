"""
Configuration Manager

Gerencia as configurações do sistema usando arquivo INI.
"""

import os
import sys
import configparser
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_user_config_path() -> Path:
    """
    Retorna o caminho para o arquivo de configuração do usuário.
    Funciona tanto em desenvolvimento quanto no executável PyInstaller.
    O arquivo settings.ini fica na mesma pasta do executável.
    """
    if getattr(sys, 'frozen', False):
        # Executando como executável PyInstaller
        # Salvar na mesma pasta do executável
        config_dir = Path(sys.executable).parent
    else:
        # Executando em desenvolvimento - usar pasta do projeto
        config_dir = Path(__file__).parent
    
    return config_dir / 'settings.ini'


class ConfigManager:
    """Gerenciador de configurações do sistema."""
    
    DEFAULT_CONFIG = {
        'Connection': {
            'db_type': 'Firebird',
            'host': 'localhost',
            'port': '3050',
            'username': 'SYSDBA',
            'password': 'masterkey',
            'database_option': 'SRV',
            'custom_database': ''
        },
        'Application': {
            'last_operation': '',
            'theme': 'Fusion',
            'remember_connection': 'true',
            'auto_connect': 'false'
        },
        'Window': {
            'width': '1200',
            'height': '800',
            'x': '100',
            'y': '100',
            'maximized': 'false'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_path: Caminho para o arquivo de configuração.
                        Se None, usa o caminho padrão.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = get_user_config_path()
        
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """Carrega as configurações do arquivo INI."""
        # Primeiro, definir valores padrão
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        
        # Depois, carregar do arquivo se existir
        if self.config_path.exists():
            try:
                self.config.read(self.config_path, encoding='utf-8')
                logger.info(f"Configurações carregadas de: {self.config_path}")
            except Exception as e:
                logger.warning(f"Erro ao carregar configurações: {e}")
        else:
            # Criar arquivo com valores padrão
            self._save_config()
            logger.info(f"Arquivo de configuração criado: {self.config_path}")
    
    def _save_config(self):
        """Salva as configurações no arquivo INI."""
        try:
            # Garantir que o diretório existe
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            logger.debug(f"Configurações salvas em: {self.config_path}")
        except PermissionError:
            logger.error(f"Sem permissão para salvar em: {self.config_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
    
    def get_config_path(self) -> str:
        """Retorna o caminho do arquivo de configuração."""
        return str(self.config_path)
    
    # ==================== Connection ====================
    
    def get_connection_config(self) -> Dict[str, str]:
        """Retorna as configurações de conexão."""
        return {
            'db_type': self.config.get('Connection', 'db_type'),
            'host': self.config.get('Connection', 'host'),
            'port': self.config.get('Connection', 'port'),
            'username': self.config.get('Connection', 'username'),
            'password': self.config.get('Connection', 'password'),
            'database_option': self.config.get('Connection', 'database_option'),
            'custom_database': self.config.get('Connection', 'custom_database')
        }
    
    def save_connection_config(self, db_type: str, host: str, port: str,
                               username: str, password: str,
                               database_option: str, custom_database: str = ''):
        """
        Salva as configurações de conexão.
        
        Args:
            db_type: Tipo de banco (Firebird ou SQL Server)
            host: Endereço do servidor
            port: Porta de conexão
            username: Nome de usuário
            password: Senha
            database_option: Opção de banco (SRV, CAD, MOV, Custom, etc.)
            custom_database: Caminho customizado do banco
        """
        self.config.set('Connection', 'db_type', db_type)
        self.config.set('Connection', 'host', host)
        self.config.set('Connection', 'port', port)
        self.config.set('Connection', 'username', username)
        self.config.set('Connection', 'password', password)
        self.config.set('Connection', 'database_option', database_option)
        self.config.set('Connection', 'custom_database', custom_database)
        self._save_config()
        logger.info("Configurações de conexão salvas")
    
    # ==================== Application ====================
    
    def get_last_operation(self) -> str:
        """Retorna a última operação selecionada."""
        return self.config.get('Application', 'last_operation')
    
    def set_last_operation(self, operation: str):
        """Define a última operação selecionada."""
        self.config.set('Application', 'last_operation', operation)
        self._save_config()
    
    def get_theme(self) -> str:
        """Retorna o tema da aplicação."""
        return self.config.get('Application', 'theme')
    
    def set_theme(self, theme: str):
        """Define o tema da aplicação."""
        self.config.set('Application', 'theme', theme)
        self._save_config()
    
    def should_remember_connection(self) -> bool:
        """Retorna se deve lembrar a última conexão."""
        return self.config.getboolean('Application', 'remember_connection')
    
    def set_remember_connection(self, remember: bool):
        """Define se deve lembrar a última conexão."""
        self.config.set('Application', 'remember_connection', str(remember).lower())
        self._save_config()
    
    def should_auto_connect(self) -> bool:
        """Retorna se deve conectar automaticamente ao iniciar."""
        return self.config.getboolean('Application', 'auto_connect')
    
    def set_auto_connect(self, auto_connect: bool):
        """Define se deve conectar automaticamente ao iniciar."""
        self.config.set('Application', 'auto_connect', str(auto_connect).lower())
        self._save_config()
    
    # ==================== Window ====================
    
    def get_window_geometry(self) -> Dict[str, Any]:
        """Retorna a geometria da janela."""
        return {
            'width': self.config.getint('Window', 'width'),
            'height': self.config.getint('Window', 'height'),
            'x': self.config.getint('Window', 'x'),
            'y': self.config.getint('Window', 'y'),
            'maximized': self.config.getboolean('Window', 'maximized')
        }
    
    def save_window_geometry(self, width: int, height: int, x: int, y: int, maximized: bool):
        """Salva a geometria da janela."""
        self.config.set('Window', 'width', str(width))
        self.config.set('Window', 'height', str(height))
        self.config.set('Window', 'x', str(x))
        self.config.set('Window', 'y', str(y))
        self.config.set('Window', 'maximized', str(maximized).lower())
        self._save_config()
    
    # ==================== Generic ====================
    
    def get(self, section: str, key: str, fallback: str = '') -> str:
        """Obtém um valor de configuração."""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """Define um valor de configuração."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self._save_config()


# Instância global
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Retorna a instância global do ConfigManager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
