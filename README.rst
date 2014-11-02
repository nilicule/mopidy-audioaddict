Installation
============

Install by running the following:

  python setup.py install


Configuration
=============

Make sure you enable the extension after you've completed the installation. You will also
need the Mopidy-Stream extension enabled - it's bundled with Mopidy, so unless you disabled it
it should be available.

An example configuration is included in the ext.conf file. Make sure to enable the plugin and
at least one of the AudioAddict stations.

Optionally you can set a username and password from any of the AudioAddict sites to have the plugin
check if premium is enabled for you. With a premium-enabled account the valid stream options
are 40k, 64k, 128k and 320k, without a premium-enabled account the plugin will default to the
lower-quality public stream.

If you don't want all AudioAddict stations to show up in Mopidy you can disable individual stations
in the Mopidy configuration.


Project resources
=================

Bugs, feedback and patches are always welcome at https://github.com/nilicule/mopidy-audioaddict
