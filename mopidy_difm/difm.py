#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
import logging
import requests
import urlparse
import re
import json
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

#
#  Channels are playlist and Album
#  PLS are tracks
#  PLS contents for internal use
#


class DigitallyImportedClient(object):

    CHANNELS_URI = "http://listen.di.fm/streamlist"
    channels = {}
    proxies = None

    def __init__(self, proxy=None):
        super(DigitallyImportedClient, self).__init__()

        if proxy is not None:
            r1 = urlparse.urlsplit(proxy)
            self.proxies = {r1.scheme: proxy}

    def refresh(self, quality, api_key):
        # clean previous data
        self.channels = {}

        # adjust quality real name
        plsquality = quality

        # download channels xml file
        channels_content = self._downloadContent(self.CHANNELS_URI)
        if channels_content is None:
            logger.error('Cannot fetch %s' % (self.CHANNELS_URI))
            return

        # parse XML
        root = json.loads(channels_content)

        idcount = 0

        for child_channel in root:
            idcount += 1

            pls_id = idcount
            channel_data = {}

            channel_data['name'] = child_channel['name']
            channel_data['playlist'] = child_channel['playlist']
            channel_data['genre'] = child_channel['key']

            channel_data['updated'] = datetime.fromtimestamp(time.time())
            channel_data['image'] = ""

            channel_data['channelid'] = child_channel['key']

            if (len(api_key)):
                if (plsquality == '320k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium_high/' + channel_data['channelid'] + '.pls?' + api_key;
                    channel_data['pls'] = plsurl;
                if (plsquality == '128k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium/' + channel_data['channelid'] +'.pls?' + api_key;
                    channel_data['pls'] = plsurl;
                if (plsquality == '64k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium_medium/' + channel_data['channelid'] +'.pls?' + api_key;
                    channel_data['pls'] = plsurl;
                if (plsquality == '40k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium_low/' + channel_data['channelid'] +'.pls?' + api_key;
                    channel_data['pls'] = plsurl;
            else:
                if (plsquality == '64k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium_medium/' + channel_data['channelid'] +'.pls';
                    channel_data['pls'] = plsurl;
                if (plsquality == '40k'):
                    channelurl = "";
                    plsurl = 'http://listen.di.fm/premium_low/' + channel_data['channelid'] +'.pls';
                    channel_data['pls'] = plsurl;

            self.channels[pls_id] = channel_data

        logger.info('Loaded %i DI.FM channels' % (len(self.channels)))

    def extractStreamUrlFromPls(self, pls_uri):
        pls_content = self._downloadContent(pls_uri)
        if pls_content is None:
            logger.error('Cannot fetch %s' % (pls_uri))
            return pls_uri

        # try to find FileX=<stream url>
        try:
            m = re.search(
                r"^(File\d)=(?P<stream_url>\S+)",
                pls_content, re.M)
            if m:
                return m.group("stream_url")
            else:
                return pls_uri
        except:
            return pls_uri

    def _downloadContent(self, url):
        try:
            r = requests.get(url, proxies=self.proxies)
            logger.debug("Get %s : %i", url, r.status_code)

            if r.status_code is not 200:
                logger.error(
                    "DIFM: %s is not reachable [http code:%i]",
                    url, r.status_code)
                return None

        except requests.exceptions.RequestException, e:
            logger.error("DigitallyImported RequestException: %s", e)
        except requests.exceptions.ConnectionError, e:
            logger.error("DigitallyImported ConnectionError: %s", e)
        except requests.exceptions.URLRequired, e:
            logger.error("DigitallyImported URLRequired: %s", e)
        except requests.exceptions.TooManyRedirects, e:
            logger.error("DigitallyImported TooManyRedirects: %s", e)
        except Exception, e:
            logger.error("DigitallyImported exception: %s", e)
        else:
            return r.text

        return None
