from __future__ import unicode_literals

import logging

import pykka

from mopidy import backend
from mopidy.models import Ref, Track

from . import client, translator

logger = logging.getLogger(__name__)

def format_proxy(scheme, username, password, hostname, port):
    # Format Proxy URL
    if hostname:
        # scheme must exists, so if None is give, we set default to http
        if not scheme:
            scheme = "http"
        # idem with port, default at 80
        if not port or port < 0:
            port = 80
        # with authentification
        if username and password:
            return "%s://%s:%s@%s:%i" % (
                scheme, username, password, hostname, port)
        # ... or without
        else:
            return "%s://%s:%i" % (scheme, hostname, port)
    else:
        return None

class AudioAddictBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['audioaddict']

    def __init__(self, config, audio):
        super(AudioAddictBackend, self).__init__()

        full_proxy = format_proxy(
            scheme=config['proxy']['scheme'],
            username=config['proxy']['username'],
            password=config['proxy']['password'],
            hostname=config['proxy']['hostname'],
            port=config['proxy']['port'])

        self.audioaddict = client.AudioAddict(
            config['audioaddict']['username'],
            config['audioaddict']['password'],
            config['audioaddict']['quality'],
            config['audioaddict']['difm'],
            config['audioaddict']['radiotunes'],
            config['audioaddict']['rockradio'],
            config['audioaddict']['jazzradio'],
            config['audioaddict']['frescaradio'],
            proxy=full_proxy
        )
        self.library = AudioAddictLibrary(backend=self)
        self.playback = AudioAddictPlayback(audio=audio, backend=self)


class AudioAddictLibrary(backend.LibraryProvider):
    root_directory = Ref.directory(uri='audioaddict:root', name='AudioAddict')

    def browse(self, uri):
        result = []
        variant, identifier = translator.parse_uri(uri)

        if variant == 'root':
            for radiostation in self.backend.audioaddict.radiostations():
                result.append(translator.radiostation_to_ref(radiostation))
        elif variant == 'radiostation' and identifier:
            for channel in self.backend.audioaddict.channels(radiostation=identifier):
                result.append(translator.channel_to_ref(channel))
        else:
            logger.debug('Unknown URI: %s', uri)

        result.sort(key=lambda ref: ref.name)
        return result

    def refresh(self, uri=None):
        self.backend.audioaddict.flush()

    def lookup(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'channel':
            return []
        channel = self.backend.audioaddict.channel(identifier)
        if not channel:
            return []
        ref = translator.channel_to_ref(channel)

        return [Track(uri=ref.uri, name=ref.name)]


class AudioAddictPlayback(backend.PlaybackProvider):
    def change_track(self, track):
        variant, identifier = translator.parse_uri(track.uri)
        if variant != 'channel':
            return False
        channel = self.backend.audioaddict.channel(identifier)
        track = track.copy(uri=channel['streamurl'])
        return super(AudioAddictPlayback, self).change_track(track)
