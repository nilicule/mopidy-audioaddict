from __future__ import unicode_literals

import json
import logging
import time
import urlparse
import requests

logger = logging.getLogger(__name__)

class AudioAddict(object):

    proxies = None

    def __init__(self, username, password, quality, difm, radiotunes, rockradio, jazzradio, frescaradio, proxy=None):
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

        # Set up proxy
        if proxy is not None:
            r1 = urlparse.urlsplit(proxy)
            self.proxies = {r1.scheme: proxy}

        # Figure out our API key
        if self._username and self._password:
            self._api_key, self._has_premium = self._fetchApiKey(self._username, self._password)
        else:
            self._api_key = None
            self._has_premium = False
            logger.info('AudioAddict: premium streams not available on your account')

    def flush(self):
        self._cache = {}
        self._channels = {}

    def radiostations(self, radiostation=None):
        stationlist = []
        if self._difm:
            stationlist.append({'id': 1, 'name': 'Digitally Imported', 'shortcode': 'difm'})
        if self._radiotunes:
            stationlist.append({'id': 2, 'name': 'RadioTunes', 'shortcode': 'radiotunes'})
        if self._rockradio:
            stationlist.append({'id': 3, 'name': 'RockRadio', 'shortcode': 'rockradio'})
        if self._jazzradio:
            stationlist.append({'id': 4, 'name': 'JazzRadio', 'shortcode': 'jazzradio'})
        if self._frescaradio:
            stationlist.append({'id': 5, 'name': 'FrescaRadio', 'shortcode': 'frescaradio'})

        if not stationlist:
            # Default to at least one network
            stationlist.append({'id': 1, 'name': 'Digitally Imported', 'shortcode': 'difm'})

        return stationlist

    def channels(self, radiostation=None):
        if radiostation:
            radiostation = int(radiostation)
            if radiostation == 1:
                station_name = 'Digitally Imported'
                hostname = 'listen.di.fm'
            elif radiostation == 2:
                station_name = 'RadioTunes'
                hostname = 'listen.radiotunes.com'
            elif radiostation == 3:
                station_name = 'RockRadio'
                hostname = 'listen.rockradio.com'
            elif radiostation == 4:
                station_name = 'JazzRadio'
                hostname = 'listen.jazzradio.com'
            elif radiostation == 5:
                station_name = 'FrescaRadio'
                hostname = 'listen.frescaradio.com'
            else:
                return []

            station_uri = 'http://' + hostname + '/streamlist'
            channels = self._fetch(station_uri, [])

            channel_count = len(channels)
            logger.info('AudioAddict: loading %s channels on %s', channel_count, station_name)
        else:
            return []

        if self._api_key and self._has_premium:
            if self._quality:
                if (self._quality == '320k'):
                    streampls = 'premium_high'
                if (self._quality == '128k'):
                    streampls = 'premium'
                if (self._quality == '64k'):
                    streampls = 'premium_medium'
                if (self._quality == '40k'):
                    streampls = 'premium_low'
            else:
                streampls = 'premium_high'
        else:
            streampls = 'public3'

        for channel in channels:
            if self._api_key:
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
        logger.info('AudioAddict: authenticating with API')

        payload = {'username': username, 'password': password}
        r = requests.post("https://api.audioaddict.com/v1/di/members/authenticate", data=payload, proxies=self.proxies)
        json_object_raw = r.json()

        subscriptions = json_object_raw['subscriptions']
        listen_key = json_object_raw['listen_key']

        if not subscriptions:
            has_premium = False
            logger.info('AudioAddict: premium streams not available on your account')
        else:
            has_premium = True
            logger.info('AudioAddict: premium streams enabled on your account')

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
            r = requests.get(uri, proxies=self.proxies)
            logger.debug("Get %s : %i", uri, r.status_code)

            if r.status_code is not 200:
                logger.error("AudioAddict: %s is not reachable [http code:%i]", uri, r.status_code)
                return None

        except requests.exceptions.RequestException, e:
            logger.error("AudioAddict RequestException: %s", e)
        except requests.exceptions.ConnectionError, e:
            logger.error("AudioAddict ConnectionError: %s", e)
        except requests.exceptions.URLRequired, e:
            logger.error("AudioAddict URLRequired: %s", e)
        except requests.exceptions.TooManyRedirects, e:
            logger.error("AudioAddict TooManyRedirects: %s", e)
        except Exception, e:
            logger.error("AudioAddict exception: %s", e)
        else:
            # Parse JSON object
            data = r.json()
            self._cache[uri] = data
            self._backoff = 1
            return data

        self._backoff = min(self._backoff_max, self._backoff*2)
        self._backoff_until = time.time() + self._backoff
        logger.debug('Entering back off mode for %d seconds.', self._backoff)
        return default
