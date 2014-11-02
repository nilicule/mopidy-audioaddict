from __future__ import unicode_literals

import os

from mopidy import config, ext

__version__ = '0.2.2'


class Extension(ext.Extension):

    dist_name = 'Mopidy-AudioAddict'
    ext_name = 'audioaddict'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['username'] = config.String()
        schema['password'] = config.Secret()
        schema['quality'] = config.String()
        schema['difm'] = config.Boolean()
        schema['radiotunes'] = config.Boolean()
        schema['rockradio'] = config.Boolean()
        schema['jazzradio'] = config.Boolean()
        schema['frescaradio'] = config.Boolean()
        return schema

    def setup(self, registry):
        from .actor import AudioAddictBackend
        registry.add('backend', AudioAddictBackend)
