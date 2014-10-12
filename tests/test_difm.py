import unittest

from mopidy_difm.difm import DigitallyImportedClient


class DigitallyImportedClientTest(unittest.TestCase):

    def test_init_proxy(self):
        proxy = "http://user:pass@proxy.lan:8080"
        sfmc = DigitallyImportedClient(proxy=proxy)
        self.assertIn('http', sfmc.proxies)
        self.assertEqual(sfmc.proxies['http'], proxy)

    def test_refresh(self):
        sfmc = DigitallyImportedClient()
        sfmc.refresh('mp3', 'fast')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_refresh_firewall(self):
        sfmc = DigitallyImportedClient()
        sfmc.refresh('mp3', 'firewall')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_refresh_no_channels(self):
        sfmc = DigitallyImportedClient()
        sfmc.CHANNELS_URI = ''
        sfmc.refresh('mp3', 'fast')

        self.assertDictEqual(sfmc.channels, {})
        self.assertEqual(len(sfmc.channels), 0)

    def test_downloadContent_ok(self):
        url = "http://listen.di.fm/streamlist"
        sfmc = DigitallyImportedClient()
        data = sfmc._downloadContent(url)
        self.assertNotEqual(len(data), 0)

    def test_downloadContent_ko(self):
        url = "http://listen.di.fm/streamlist"
        sfmc = DigitallyImportedClient()
        data = sfmc._downloadContent(url)
        self.assertIsNone(data)

