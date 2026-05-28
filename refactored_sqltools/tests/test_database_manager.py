import unittest

import _bootstrap  # noqa: F401

from refactored_sqltools.core.database.drivers.base import DatabaseDriver, QueryResult
from refactored_sqltools.core.database.manager import DatabaseManager


class FakeDriver(DatabaseDriver):
    def connect(self, **kwargs):
        self._is_connected = True
        self._connection_params = kwargs
        return True

    def disconnect(self):
        self._is_connected = False

    def execute_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        return QueryResult(success=True, message="ok", rows_affected=1)


class DatabaseManagerTests(unittest.TestCase):
    def test_database_manager_supports_registered_fake_driver_with_params(self):
        DatabaseManager.register_driver("Fake", FakeDriver)
        manager = DatabaseManager()

        manager.connect("Fake", database="x")
        result = manager.execute_query("UPDATE T SET A = ?", params=(1,))
        driver = manager.get_driver("Fake")

        self.assertTrue(result.success)
        self.assertEqual(driver.last_params, (1,))
