from __future__ import unicode_literals

import re

from mopidy.models import Ref

def unparse_uri(variant, identifier):
    return b'audioaddict:%s:%s' % (variant, identifier)


def parse_uri(uri):
    result = re.findall(r'^audioaddict:([a-z]+)(?::(\d+|[a-z]{2}))?$', uri)
    if result:
        return result[0]
    return None, None


def channel_to_ref(channel):
    name = channel.get('name', channel['streamurl']).strip()
    uri = unparse_uri('channel', channel['id'])
    return Ref.track(uri=uri, name='%s' % (name))


def radiostation_to_ref(radiostation):
    uri = unparse_uri('radiostation', radiostation['id'])
    return Ref.directory(uri=uri, name=radiostation.get('name', uri))

