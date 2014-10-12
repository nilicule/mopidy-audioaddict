import mock
import unittest

from mopidy_difm import Extension, actor as backend_lib


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[difm]', config)
        self.assertIn('enabled = True', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        self.assertIn('quality', schema)
        self.assertIn('encoding', schema)

    def test_validate_environment(self):
        ext = Extension()

        self.assertEqual(ext.validate_environment(), None)

    def test_setup(self):
        registry = mock.Mock()

        ext = Extension()
        ext.setup(registry)

        registry.add.assert_called_once_with(
            'backend', backend_lib.DigitallyImportedBackend)
