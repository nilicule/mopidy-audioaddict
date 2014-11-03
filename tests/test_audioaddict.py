import unittest

from mopidy_audioaddict.actor import


class DigitallyImportedClientTest(unittest.TestCase):
    self._difm = 'True'

    def test_refresh(self):
        audioaddict = AudioAddict()
        audioaddict.refresh('mp3', 'fast')

        self.assertIsNotNone(audioaddict.channels)
        self.assertNotEqual(len(audioaddict.channels), 0)

    def test_refresh_firewall(self):
        audioaddict = AudioAddict()
        audioaddict.refresh('mp3', 'firewall')

        self.assertIsNotNone(audioaddict.channels)
        self.assertNotEqual(len(audioaddict.channels), 0)

    def test_refresh_no_channels(self):
        audioaddict = AudioAddict()
        audioaddict.CHANNELS_URI = ''
        audioaddict.refresh('mp3', 'fast')

        self.assertDictEqual(audioaddict.channels, {})
        self.assertEqual(len(audioaddict.channels), 0)

    def test_downloadContent_ok(self):
        url = "http://listen.di.fm/streamlist"
        audioaddict = AudioAddict()
        data = audioaddict._downloadContent(url)
        self.assertNotEqual(len(data), 0)

    def test_downloadContent_ko(self):
        url = "http://listen.di.fm/streamlist"
        audioaddict = AudioAddict()
        data = audioaddict._downloadContent(url)
        self.assertIsNone(data)

