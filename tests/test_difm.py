import unittest

from mopidy_audioaddict.client import AudioAddict


class AudioAddictClientTest(unittest.TestCase):
    def test_refresh(self):
        sfmc = AudioAddict()
        sfmc.refresh('mp3', 'fast')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_refresh_firewall(self):
        sfmc = AudioAddict()
        sfmc.refresh('mp3', 'firewall')

        self.assertIsNotNone(sfmc.channels)
        self.assertNotEqual(len(sfmc.channels), 0)

    def test_refresh_no_channels(self):
        sfmc = AudioAddict()
        sfmc.CHANNELS_URI = ''
        sfmc.refresh('mp3', 'fast')

        self.assertDictEqual(sfmc.channels, {})
        self.assertEqual(len(sfmc.channels), 0)

    def test_downloadContent_ok(self):
        url = "http://listen.di.fm/streamlist"
        sfmc = AudioAddict()
        data = sfmc._downloadContent(url)
        self.assertNotEqual(len(data), 0)

    def test_downloadContent_ko(self):
        url = "http://listen.di.fm/streamlist"
        sfmc = AudioAddict()
        data = sfmc._downloadContent(url)
        self.assertIsNone(data)

