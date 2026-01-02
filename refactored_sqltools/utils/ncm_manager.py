"""
NCM JSON Manager

Gerencia o download e carregamento do arquivo JSON de NCMs do Siscomex.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def get_base_path() -> Path:
    """
    Retorna o caminho base da aplicação.
    Funciona tanto em desenvolvimento quanto no executável PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Executando como executável PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Executando em desenvolvimento
        return Path(__file__).parent.parent


def get_user_data_path() -> Path:
    """
    Retorna o caminho para dados do usuário (gravável).
    Usado para salvar arquivos JSON baixados.
    """
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
    else:
        base = Path(os.path.expanduser('~/.local/share'))
    
    app_data = base / 'SQLSysHub'
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data


class NCMManager:
    """Gerenciador do arquivo JSON de NCMs do Siscomex."""
    
    NCM_URL = "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json"
    
    def __init__(self):
        self._ncm_data: Optional[Dict] = None
        self._last_update: Optional[str] = None
        
    @property
    def bundled_json_dir(self) -> Path:
        """Diretório do JSON empacotado no executável (somente leitura)."""
        return get_base_path() / "refactored_sqltools" / "json"
    
    @property
    def user_json_dir(self) -> Path:
        """Diretório do JSON do usuário (leitura/escrita)."""
        json_dir = get_user_data_path() / "json"
        json_dir.mkdir(parents=True, exist_ok=True)
        return json_dir
        
    def get_json_path(self) -> Optional[Path]:
        """
        Retorna o caminho do arquivo JSON de NCM existente.
        Prioriza o arquivo do usuário (mais recente) sobre o empacotado.
        """
        all_files = []
        
        # Procura no diretório do usuário primeiro
        if self.user_json_dir.exists():
            user_files = list(self.user_json_dir.glob("Tabela_NCM_*.json"))
            all_files.extend(user_files)
        
        # Procura no diretório empacotado
        if self.bundled_json_dir.exists():
            bundled_files = list(self.bundled_json_dir.glob("Tabela_NCM_*.json"))
            all_files.extend(bundled_files)
        
        if all_files:
            # Retorna o mais recente baseado no nome do arquivo (data)
            return max(all_files, key=lambda f: f.name)
        
        return None
    
    def is_json_available(self) -> Tuple[bool, str]:
        """
        Verifica se o arquivo JSON está disponível.
        
        Returns:
            Tuple[bool, str]: (disponível, mensagem)
        """
        json_path = self.get_json_path()
        if json_path and json_path.exists():
            location = "usuário" if self.user_json_dir in json_path.parents or json_path.parent == self.user_json_dir else "aplicação"
            return True, f"Arquivo encontrado ({location}): {json_path.name}"
        return False, "Arquivo JSON não encontrado. Use 'Baixar NCMs' para obter."
    
    def load_json(self) -> Tuple[bool, str]:
        """
        Carrega o arquivo JSON em memória.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        if self._ncm_data is not None:
            return True, f"JSON já carregado ({len(self._ncm_data)} NCMs)"
            
        json_path = self.get_json_path()
        if not json_path or not json_path.exists():
            return False, "Arquivo JSON não encontrado. Use 'Baixar NCMs' para obter."
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            ncm_list = data.get('Nomenclaturas', [])
            if not ncm_list:
                return False, "Arquivo JSON vazio ou inválido"
                
            # Indexar por código NCM
            self._ncm_data = {}
            for item in ncm_list:
                codigo = item.get('Codigo', '').replace('.', '')
                self._ncm_data[codigo] = item
                
            self._last_update = data.get('Data_Ultima_Atualizacao_NCM', 'N/A')
            
            return True, f"Carregado: {len(self._ncm_data)} NCMs (Atualização: {self._last_update})"
            
        except json.JSONDecodeError as e:
            return False, f"Erro ao decodificar JSON: {e}"
        except Exception as e:
            return False, f"Erro ao carregar JSON: {e}"
    
    def download_json(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Faz download do arquivo JSON do Siscomex.
        
        Args:
            progress_callback: Função callback para reportar progresso
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            import urllib.request
            import ssl
            
            if progress_callback:
                progress_callback("Conectando ao Siscomex...")
            
            # Criar contexto SSL
            context = ssl.create_default_context()
            
            # Fazer requisição
            req = urllib.request.Request(
                self.NCM_URL,
                headers={'User-Agent': 'SQLSysHub/2.0.1'}
            )
            
            if progress_callback:
                progress_callback("Baixando arquivo JSON...")
            
            with urllib.request.urlopen(req, context=context, timeout=120) as response:
                data = response.read()
                
            if progress_callback:
                progress_callback("Validando dados...")
            
            # Validar JSON
            json_data = json.loads(data.decode('utf-8'))
            ncm_list = json_data.get('Nomenclaturas', [])
            
            if not ncm_list:
                return False, "Arquivo baixado está vazio ou inválido"
            
            # Salvar no diretório do usuário (gravável)
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"Tabela_NCM_Vigente_{date_str}.json"
            filepath = self.user_json_dir / filename
            
            if progress_callback:
                progress_callback("Salvando arquivo...")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            # Limpar cache para forçar recarregamento
            self._ncm_data = None
            self._last_update = None
            
            logger.info(f"JSON salvo em: {filepath}")
            
            return True, f"Download concluído: {len(ncm_list)} NCMs salvos em {filepath.name}"
            
        except urllib.error.URLError as e:
            return False, f"Erro de conexão: {e.reason}"
        except json.JSONDecodeError as e:
            return False, f"Erro ao processar JSON: {e}"
        except PermissionError:
            return False, f"Sem permissão para salvar em: {self.user_json_dir}"
        except Exception as e:
            logger.exception("Erro no download do JSON")
            return False, f"Erro no download: {e}"
    
    def get_ncm_data(self) -> Optional[Dict]:
        """Retorna os dados de NCM carregados."""
        return self._ncm_data
    
    def get_last_update(self) -> Optional[str]:
        """Retorna a data da última atualização."""
        return self._last_update
    
    def get_json_info(self) -> Dict:
        """Retorna informações sobre o arquivo JSON atual."""
        json_path = self.get_json_path()
        if not json_path:
            return {
                'available': False,
                'path': None,
                'location': None,
                'filename': None
            }
        
        is_user = self.user_json_dir in json_path.parents or json_path.parent == self.user_json_dir
        
        return {
            'available': True,
            'path': str(json_path),
            'location': 'usuário' if is_user else 'aplicação',
            'filename': json_path.name
        }


# Instância global para cache
_ncm_manager: Optional[NCMManager] = None


def get_ncm_manager() -> NCMManager:
    """Retorna a instância global do NCMManager."""
    global _ncm_manager
    if _ncm_manager is None:
        _ncm_manager = NCMManager()
    return _ncm_manager
