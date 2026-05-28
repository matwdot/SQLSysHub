"""
NCM JSON manager.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from .paths import get_base_path, get_user_data_path


logger = logging.getLogger(__name__)


class NCMManager:
    """Manage Siscomex NCM JSON files."""

    NCM_URL = "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json"

    def __init__(self):
        self._ncm_data: Optional[Dict] = None
        self._last_update: Optional[str] = None
        self._json_source: Optional[str] = None

    @property
    def bundled_json_dir(self) -> Path:
        """Directory containing bundled JSON files."""
        return get_base_path() / "json"

    @property
    def user_json_dir(self) -> Path:
        """Writable user JSON directory."""
        json_dir = get_user_data_path() / "json"
        json_dir.mkdir(parents=True, exist_ok=True)
        return json_dir

    def get_json_path(self) -> Optional[Path]:
        """Return the newest available JSON file."""
        all_files = []

        if self.user_json_dir.exists():
            all_files.extend(self.user_json_dir.glob("Tabela_NCM_*.json"))

        if self.bundled_json_dir.exists():
            all_files.extend(self.bundled_json_dir.glob("Tabela_NCM_*.json"))

        return max(all_files, key=lambda file: file.name) if all_files else None

    def is_json_available(self) -> Tuple[bool, str]:
        json_path = self.get_json_path()
        if json_path and json_path.exists():
            location = self._get_file_location(json_path)
            return True, f"Arquivo encontrado ({location}): {json_path.name}"
        return False, "Arquivo JSON nao encontrado. Use 'Baixar NCMs' para obter."

    def load_json(self) -> Tuple[bool, str]:
        """Load and validate an NCM JSON file into memory."""
        if self._ncm_data is not None:
            return True, f"JSON ja carregado ({len(self._ncm_data)} NCMs)"

        json_path = self.get_json_path()
        if not json_path or not json_path.exists():
            return False, "Arquivo JSON nao encontrado. Use 'Baixar NCMs' para obter."

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            valid, message = self._validate_json_payload(data)
            if not valid:
                return False, message

            self._ncm_data = self._index_ncm_data(data)
            self._last_update = data.get("Data_Ultima_Atualizacao_NCM", "N/A")
            self._json_source = str(json_path)

            return True, f"Carregado: {len(self._ncm_data)} NCMs (Atualizacao: {self._last_update})"
        except json.JSONDecodeError as exc:
            return False, f"Erro ao decodificar JSON: {exc}"
        except Exception as exc:
            return False, f"Erro ao carregar JSON: {exc}"

    @staticmethod
    def _parse_update_date_str(date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        date_str = date_str.replace("Vigente em ", "").strip()
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def get_json_update_date(self) -> Optional[str]:
        json_path = self.get_json_path()
        if not json_path or not json_path.exists():
            return None
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("Data_Ultima_Atualizacao_NCM")
        except Exception:
            return None

    def download_json(self, progress_callback=None) -> Tuple[bool, str]:
        """Download, validate and store the Siscomex JSON file."""
        try:
            import ssl
            import urllib.request

            if progress_callback:
                progress_callback("Conectando ao Siscomex...")

            request = urllib.request.Request(
                self.NCM_URL,
                headers={"User-Agent": "SQLSysHub/2.0.1"},
            )

            if progress_callback:
                progress_callback("Baixando arquivo JSON...")

            context = ssl.create_default_context()
            with urllib.request.urlopen(request, context=context, timeout=120) as response:
                raw_data = response.read()

            if progress_callback:
                progress_callback("Validando dados...")

            json_data = json.loads(raw_data.decode("utf-8"))
            valid, message = self._validate_json_payload(json_data)
            if not valid:
                return False, message

            nova_data_str = json_data.get("Data_Ultima_Atualizacao_NCM", "")
            nova_data = self._parse_update_date_str(nova_data_str)

            existing_path = self.get_json_path()
            if existing_path and existing_path.exists():
                try:
                    with open(existing_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                    existing_data_str = existing_data.get("Data_Ultima_Atualizacao_NCM", "")
                    existing_date = self._parse_update_date_str(existing_data_str)

                    if nova_data and existing_date and nova_data <= existing_date:
                        ncm_count = len(json_data.get("Nomenclaturas", []))
                        msg = f"JSON ja atualizado ({existing_data_str}). Download possui {nova_data_str}."
                        logger.info(msg)
                        return True, msg
                except Exception:
                    pass

            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"Tabela_NCM_Vigente_{date_str}.json"
            filepath = self.user_json_dir / filename
            temp_path = filepath.with_suffix(filepath.suffix + ".tmp")

            if progress_callback:
                progress_callback("Salvando arquivo...")

            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(json_data, file, ensure_ascii=False, indent=2)
            temp_path.replace(filepath)

            self._ncm_data = None
            self._last_update = None
            self._json_source = None

            ncm_count = len(json_data.get("Nomenclaturas", []))
            logger.info("JSON NCM salvo em: %s", filepath)
            return True, f"Download concluido: {ncm_count} NCMs ({nova_data_str})"
        except urllib.error.URLError as exc:
            return False, f"Erro de conexao: {exc.reason}"
        except json.JSONDecodeError as exc:
            return False, f"Erro ao processar JSON: {exc}"
        except PermissionError:
            return False, f"Sem permissao para salvar em: {self.user_json_dir}"
        except Exception as exc:
            logger.exception("Erro no download do JSON")
            return False, f"Erro no download: {exc}"

    def get_ncm_data(self) -> Optional[Dict]:
        return self._ncm_data

    def get_last_update(self) -> Optional[str]:
        return self._last_update

    def get_json_info(self) -> Dict:
        json_path = self.get_json_path()
        if not json_path:
            return {
                "available": False,
                "path": None,
                "location": None,
                "filename": None,
                "source": self._json_source,
            }

        return {
            "available": True,
            "path": str(json_path),
            "location": self._get_file_location(json_path),
            "filename": json_path.name,
            "source": self._json_source,
        }

    def is_json_outdated(self) -> bool:
        local_date_str = self.get_json_update_date()
        if local_date_str is None:
            return True
        return self._parse_update_date_str(local_date_str) is None

    def _validate_json_payload(self, data: Dict) -> Tuple[bool, str]:
        if not isinstance(data, dict):
            return False, "Arquivo JSON invalido: raiz deve ser objeto"

        ncm_list = data.get("Nomenclaturas")
        if not isinstance(ncm_list, list) or not ncm_list:
            return False, "Arquivo JSON vazio ou invalido"

        required_fields = ("Codigo", "Descricao", "Data_Fim")
        for index, item in enumerate(ncm_list[:100]):
            if not isinstance(item, dict):
                return False, f"NCM invalido na posicao {index}"
            missing = [field for field in required_fields if not item.get(field)]
            if missing:
                return False, f"NCM sem campos obrigatorios na posicao {index}: {', '.join(missing)}"

        return True, "JSON valido"

    def _index_ncm_data(self, data: Dict) -> Dict:
        indexed = {}
        for item in data.get("Nomenclaturas", []):
            codigo = str(item.get("Codigo", "")).replace(".", "").strip()
            if codigo:
                indexed[codigo] = item
        return indexed

    def _get_file_location(self, path: Path) -> str:
        return "usuario" if self.user_json_dir in path.parents or path.parent == self.user_json_dir else "aplicacao"


_ncm_manager: Optional[NCMManager] = None


def get_ncm_manager() -> NCMManager:
    """Return the global NCMManager instance."""
    global _ncm_manager
    if _ncm_manager is None:
        _ncm_manager = NCMManager()
    return _ncm_manager
