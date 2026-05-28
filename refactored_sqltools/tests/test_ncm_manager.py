import json
import unittest

import _bootstrap  # noqa: F401

from refactored_sqltools.utils.ncm_manager import NCMManager


class TempNCMManager(NCMManager):
    def __init__(self, json_dir):
        super().__init__()
        self._json_dir = json_dir

    @property
    def user_json_dir(self):
        return self._json_dir

    @property
    def bundled_json_dir(self):
        return self._json_dir / "missing"


class NCMManagerTests(unittest.TestCase):
    def test_ncm_manager_rejects_invalid_payload(self):
        manager = NCMManager()

        valid, message = manager._validate_json_payload({"Nomenclaturas": []})

        self.assertFalse(valid)
        self.assertTrue("vazio" in message.lower() or "invalido" in message.lower())


    def test_ncm_manager_loads_valid_json(self):
        import tempfile
        from pathlib import Path

        payload = {
            "Data_Ultima_Atualizacao_NCM": "01/01/2026",
            "Nomenclaturas": [
                {
                    "Codigo": "0101.21.00",
                    "Descricao": "Teste",
                    "Data_Fim": "31/12/9999",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            json_dir = Path(tmp) / "json"
            json_dir.mkdir()
            json_path = json_dir / "Tabela_NCM_Vigente_20260101.json"
            json_path.write_text(json.dumps(payload), encoding="utf-8")

            manager = TempNCMManager(json_dir)
            success, message = manager.load_json()

            self.assertTrue(success, message)
            self.assertEqual(manager.get_ncm_data()["01012100"]["Descricao"], "Teste")
