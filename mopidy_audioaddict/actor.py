from __future__ import unicode_literals

import logging

import pykka

from mopidy import backend, exceptions, stream
from mopidy.models import Ref, Track

from . import client, translator

from mopidy.internal import http, playlists
from mopidy.audio import scan

import time

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

        self._config = config

        self._scanner = scan.Scanner(
            timeout=config['stream']['timeout'],
            proxy_config=config['proxy'])

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
    def __init__(self, audio, backend):
        super(AudioAddictPlayback, self).__init__(audio, backend)
        self._config = backend._config
        self._scanner = backend._scanner
        self._session = http.get_requests_session(
            proxy_config=backend._config['proxy'],
            user_agent='%s/%s' % (
                stream.Extension.dist_name, stream.Extension.version))

    def translate_uri(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'channel':
            return None
        channel = self.backend.audioaddict.channel(identifier)
        logger.info("Stream URL: %s", channel['streamurl'])

        return _unwrap_stream(channel['streamurl'], timeout=self._config['stream']['timeout'], scanner=self._scanner, requests_session=self._session)


def _unwrap_stream(uri, timeout, scanner, requests_session):
    """
    Get a stream URI from a playlist URI, ``uri``.
    Unwraps nested playlists until something that's not a playlist is found or
    the ``timeout`` is reached.
    """

    original_uri = uri
    seen_uris = set()
    deadline = time.time() + timeout

    while time.time() < deadline:
        if uri in seen_uris:
            logger.info(
                'Unwrapping stream from URI (%s) failed: '
                'playlist referenced itself', uri)
            return None
        else:
            seen_uris.add(uri)

        logger.debug('Unwrapping stream from URI: %s', uri)

        try:
            scan_timeout = deadline - time.time()
            if scan_timeout < 0:
                logger.info(
                    'Unwrapping stream from URI (%s) failed: '
                    'timed out in %sms', uri, timeout)
                return None
            scan_result = scanner.scan(uri, timeout=scan_timeout)
        except exceptions.ScannerError as exc:
            logger.debug('GStreamer failed scanning URI (%s): %s', uri, exc)
            scan_result = None

        if scan_result is not None and not (
                scan_result.mime.startswith('text/') or
                scan_result.mime.startswith('application/')):
            logger.debug(
                'Unwrapped potential %s stream: %s', scan_result.mime, uri)
            return uri

        download_timeout = deadline - time.time()
        if download_timeout < 0:
            logger.info(
                'Unwrapping stream from URI (%s) failed: timed out in %sms',
                uri, timeout)
            return None
        content = http.download(
            requests_session, uri, timeout=download_timeout)

        if content is None:
            logger.info(
                'Unwrapping stream from URI (%s) failed: '
                'error downloading URI %s', original_uri, uri)
            return None

        uris = playlists.parse(content)
        if not uris:
            logger.debug(
                'Failed parsing URI (%s) as playlist; found potential stream.',
                uri)
            return uri

        # TODO Test streams and return first that seems to be playable
        logger.debug(
            'Parsed playlist (%s) and found new URI: %s', uri, uris[0])
        uri = uris[0]