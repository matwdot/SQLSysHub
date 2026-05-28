import unittest

import _bootstrap  # noqa: F401

from refactored_sqltools.core.database.drivers.base import QueryResult
from refactored_sqltools.core.operations.base import BaseOperation
from refactored_sqltools.core.operations.individual.cancelar_cupom import CancelarCupomOperation
from refactored_sqltools.core.operations.individual.consultar_ncm_inexistente import (
    ConsultarNCMInexistenteOperation,
)
from refactored_sqltools.core.operations.registry import operation_registry


class SelectOperation(BaseOperation):
    def __init__(self):
        super().__init__("select", "select")

    def get_sql(self, **params):
        return "SELECT 1"


class FakeManager:
    def execute_query(self, query, db_type=None, params=None):
        self.query = query
        self.params = params
        return QueryResult(success=True, message="ok", columns=["A"], data=[(1,)])


class OperationTests(unittest.TestCase):
    def test_base_operation_processes_query_result_object(self):
        manager = FakeManager()
        result = SelectOperation().execute(manager)

        self.assertTrue(result.success)
        self.assertEqual(result.columns, ["A"])
        self.assertEqual(result.data, [(1,)])

    def test_cancelar_cupom_uses_bound_parameter_for_caixa(self):
        operation = CancelarCupomOperation()

        operation.validate_params(todos_caixas=False, numero_caixa="12")

        self.assertIn("CXANUM = ?", operation.get_sql(todos_caixas=False, numero_caixa="12"))
        self.assertEqual(operation.get_sql_params(todos_caixas=False, numero_caixa="12"), (12,))

    def test_cancelar_cupom_rejects_invalid_caixa(self):
        operation = CancelarCupomOperation()

        with self.assertRaises(Exception):
            operation.validate_params(todos_caixas=False, numero_caixa="1; DROP TABLE CAIXA")

    def test_consultar_ncm_uses_bound_dates(self):
        operation = ConsultarNCMInexistenteOperation()

        sql = operation.get_sql(data_inicio="2026-01-01", data_fim="2026-01-31")

        self.assertIn("BETWEEN ? AND ?", sql)
        self.assertEqual(
            operation.get_sql_params(data_inicio="2026-01-01", data_fim="2026-01-31"),
            ("2026-01-01", "2026-01-31"),
        )

    def test_registry_contains_known_operations(self):
        names = operation_registry.get_operation_names()

        self.assertIn("Cancelar Cupom", names)
        self.assertIn("Consultar NCM Inexistente", names)


if __name__ == "__main__":
    unittest.main()
