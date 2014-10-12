from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Album, Track, Artist, Ref
from .difm import DigitallyImportedClient

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


class DigitallyImportedBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(DigitallyImportedBackend, self).__init__()

        full_proxy = format_proxy(
            scheme=config['proxy']['scheme'],
            username=config['proxy']['username'],
            password=config['proxy']['password'],
            hostname=config['proxy']['hostname'],
            port=config['proxy']['port'])

        self.difm = DigitallyImportedClient(proxy=full_proxy)
        self.library = DigitallyImportedLibraryProvider(backend=self)

        self.uri_schemes = ['difm']
        self.quality = config['difm']['quality']
        self.api_key = config['difm']['api_key']

    def on_start(self):
        self.difm.refresh(self.quality, self.api_key)


class DigitallyImportedLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri='difm:library', name='DI.FM')

    def lookup(self, uri):
        # Whatever the uri, it will always contains one track
        # which is a url to a pls

        if not uri.startswith('difm:'):
            return None

        channel_name = uri[uri.index('/') + 1:]
        channel_name = channel_name.strip()
        channel_name = float(channel_name)

        channel_data = self.backend.difm.channels[channel_name]

        # Artists
        # artist = Artist(name=channel_data['name'])
        print("ARTIST")
        artist = Artist(name="DI.FM")
        print(artist)

        # Build album (idem as playlist, but with more metada)
        print("ALBUM")
        print(channel_data)
        album = Album(
            artists=[artist],
            #date=channel_data['updated'],
            #images=[channel_data['image']],
            name=channel_data['name'],
            uri='difm:channel:/%s' % (channel_name))
        print(album)

        print("TRACK")
        track = Track(
            artists=[artist],
            album=album,
            genre=channel_data['genre'],
            name=channel_data['name'],
            uri=channel_data['pls'])
        print(track)

        return [track]

    def browse(self, uri):
        if uri != 'difm:library':
            return []

        result = []
        for channel in self.backend.difm.channels:
            result.append(Ref.track(
                uri='difm:channel:/%s' % (channel),
                name=self.backend.difm.channels[channel]['name']
                ))
        result.sort(key=lambda ref: ref.name)
        return result
