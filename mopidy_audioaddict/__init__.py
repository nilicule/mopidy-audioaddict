from __future__ import unicode_literals

import os

from mopidy import config, ext

__version__ = '0.2.7'

class Extension(ext.Extension):
    dist_name = 'Mopidy-AudioAddict'
    ext_name = 'audioaddict'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['username'] = config.String(optional=True)
        schema['password'] = config.Secret(optional=True)
        schema['quality'] = config.String(optional=True)
        schema['difm'] = config.Boolean(optional=True)
        schema['radiotunes'] = config.Boolean(optional=True)
        schema['rockradio'] = config.Boolean(optional=True)
        schema['jazzradio'] = config.Boolean(optional=True)
        schema['frescaradio'] = config.Boolean(optional=True)
        return schema

    def setup(self, registry):
        from .actor import AudioAddictBackend
        registry.add('backend', AudioAddictBackend)
