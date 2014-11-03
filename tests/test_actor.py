import unittest

from mopidy_audioaddict.actor import format_proxy


class ActorTest(unittest.TestCase):

    def test_format_proxy(self):
        self.assertEqual(format_proxy(
            '', '', '', '', 0
            ), None)
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            'https', '', '', 'proxy.lan', 0
            ), 'https://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', 'user', '', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', 'password', 'proxy.lan', 0
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', 'user', 'password', 'proxy.lan', 0
            ), 'http://user:password@proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', -1
            ), 'http://proxy.lan:80')
        self.assertEqual(format_proxy(
            '', '', '', 'proxy.lan', 8080
            ), 'http://proxy.lan:8080')
