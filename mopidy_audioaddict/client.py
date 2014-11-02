from __future__ import unicode_literals

import json
import logging
import time
import urllib2
import requests

logger = logging.getLogger(__name__)

class AudioAddict(object):
    def __init__(self, username, password, quality, difm, radiotunes, rockradio, jazzradio, frescaradio):
        self._cache = {}
        self._channels = {}
        self._backoff_until = time.time()
        self._backoff_max = 60
        self._backoff = 1
        self._username = username
        self._password = password
        self._quality = quality
        self._difm = difm
        self._radiotunes = radiotunes
        self._rockradio = rockradio
        self._jazzradio = jazzradio
        self._frescaradio = frescaradio

        # Figure out our API key
        if self._username and self._password:
            self._api_key, self._has_premium = self._fetchApiKey(self._username, self._password)
        else:
            self._api_key = ""
            self._has_premium = False

    def flush(self):
        self._cache = {}
        self._channels = {}

    def radiostations(self, radiostation=None):
        stationlist = [
            {'id': 1, 'name': 'Digitally Imported', 'shortcode': 'difm',},
            {'id': 2, 'name': 'RadioTunes', 'shortcode': 'radiotunes',},
            {'id': 3, 'name': 'RockRadio', 'shortcode': 'rockradio',},
            {'id': 4, 'name': 'JazzRadio', 'shortcode': 'jazzradio',},
            {'id': 5, 'name': 'FrescaRadio', 'shortcode': 'frescaradio',}
        ]

        return stationlist

    def channels(self, radiostation=None):
        if radiostation:
            radiostation = int(radiostation)
            if radiostation == 1:
                hostname = 'listen.di.fm'
            elif radiostation == 2:
                hostname = 'listen.radiotunes.com'
            elif radiostation == 3:
                hostname = 'listen.rockradio.com'
            elif radiostation == 4:
                hostname = 'listen.jazzradio.com'
            elif radiostation == 5:
                hostname = 'listen.frescaradio.com'
            else:
                return []

            station_uri = 'http://' + hostname + '/streamlist'
            channels = self._fetch(station_uri, [])
        else:
            return []

        if (len(self._api_key)) and self._has_premium:
            if (self._quality == '320k'):
                streampls = 'premium_high'
            if (self._quality == '128k'):
                streampls = 'premium'
            if (self._quality == '64k'):
                streampls = 'premium_medium'
            if (self._quality == '40k'):
                streampls = 'premium_low'
        else:
            streampls = 'public3'

        for channel in channels:
            if (len(self._api_key)):
                channel['streamurl'] = 'http://' + hostname + '/' + streampls + '/' + channel['key'] + '.pls?' + self._api_key
            else:
                channel['streamurl'] = 'http://' + hostname + '/' + streampls + '/' + channel['key'] + '.pls'

            self._channels.setdefault(channel['id'], channel)
        return channels

    def channel(self, identifier):
        identifier = int(identifier)
        if identifier in self._channels:
            return self._channels[identifier]
        path = '/id/%s' % identifier
        channel = self._fetch('channel', path, {})
        if channel:
            self._channels.setdefault(channel['id'], channel)
        return channel

    def _fetchApiKey(self, username, password):
        payload = {'username': username, 'password': password}
        r = requests.post("https://api.audioaddict.com/v1/di/members/authenticate", data=payload)
        json_object_raw = r.json()

        subscriptions = json_object_raw['subscriptions']
        listen_key = json_object_raw['listen_key']

        if not subscriptions:
            has_premium = False
        else:
            has_premium = True

        return (listen_key, has_premium)

    def _fetch(self, uri, default):
        if uri in self._cache:
            logger.debug('Cache hit: %s', uri)
            return self._cache[uri]

        if time.time() < self._backoff_until:
            logger.debug('Back off fallback used: %s', uri)
            return default

        logger.debug('Fetching: %s', uri)
        try:
            fp = urllib2.urlopen(uri)
            data = json.load(fp)
            self._cache[uri] = data
            self._backoff = 1
            return data
        except urllib2.HTTPError as e:
            logger.debug('Fetch failed, HTTP %s: %s', e.code, e.reason)
            if e.code == 404:
                self._cache[uri] = default
                return default
        except IOError as e:
            logger.debug('Fetch failed: %s', e)
        except ValueError as e:
            logger.warning('Fetch failed: %s', e)

        self._backoff = min(self._backoff_max, self._backoff*2)
        self._backoff_until = time.time() + self._backoff
        logger.debug('Entering back off mode for %d seconds.', self._backoff)
        return default
