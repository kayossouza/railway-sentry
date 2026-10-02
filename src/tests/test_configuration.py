import os
import pathlib
import runpy
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ConfigurationTest(unittest.TestCase):
    def execute(self, required_options_ready):
        values = {}
        options = types.SimpleNamespace(get=values.get,
                                        set=lambda key, value: values.__setitem__(key, value))
        sentry = types.ModuleType('sentry')
        sentry.options = options
        sentry.get_version = lambda: '26.9.0'
        manager = MagicMock()
        manager.filter.return_value.exists.return_value = True
        modules = {
            'sentry': sentry,
            'sentry.runner': types.SimpleNamespace(configure=lambda: None),
            'sentry.users.models.user': types.SimpleNamespace(User=types.SimpleNamespace(objects=manager)),
            'sentry.web.client_config': types.SimpleNamespace(
                _needs_upgrade=lambda: not required_options_ready or
                values.get('sentry:version-configured') != '26.9.0'),
        }
        with patch.dict(sys.modules, modules), patch.dict(os.environ, {'ADMIN_EMAIL': 'admin@sentry.local'}):
            runpy.run_path(str(ROOT / 'sentry-config/admin.py'))
        manager.create_user.assert_not_called()
        return values

    def test_preconfigured_installation_skips_redundant_wizard(self):
        self.assertEqual(self.execute(True).get('sentry:version-configured'), '26.9.0')

    def test_missing_required_option_aborts_bootstrap(self):
        with self.assertRaises(RuntimeError):
            self.execute(False)


if __name__ == '__main__':
    unittest.main()
