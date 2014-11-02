Installation
============

Install by running the following:

  python setup.py install


Configuration
=============

Make sure you enable the extension after you've completed the installation. You will also
need the Mopidy-Stream extension enabled - it's bundled with Mopidy, so unless you disabled it
it should be available.

You may change prefered quality in your Mopidy configuration file. An example configuration is
included in the ext.conf file, all fields apart from username and password are required.

Optionally you can add a username and password from any of the AudioAddict sites to enable selecting
stream quality. Valid stream quality options are 40k, 64k, 128k and 320k.

If you have a valid account but premium is not enabled the plugin will default to the lower quality
public streams.


Project resources
=================

Bugs, feedback and patches are always welcome at https://github.com/nilicule/mopidy-audioaddict
