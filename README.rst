Installation
============

Install by running the following:

  python setup.py install

You can also install the plugin from PyPI:

  pip install Mopidy-AudioAddict


Configuration
=============

Make sure you enable the extension after you've completed the installation. You will also
need the Mopidy-Stream extension enabled - it's bundled with Mopidy, so unless you disabled it
it should be available.

Example configuration::

    [audioaddict]
    # enable plugin
    enabled = true
    # username and password (optional)
    username = john@doe.net
    password = supersecret
    # you need an account if you want to set stream quality
    # valid options are:
    #   40k, 64k (free)
    #   40k, 64k, 128k, 320k (premium)
    quality = 320k
    # enable or disable individual stations
    difm = true
    radiotunes = true
    rockradio = true
    jazzradio = true
    frescaradio = true

If you choose not to provide a username and password then the plugin will default to the
lower-quality 40k public stream.

The plugin will cache channel lists for each of the stations to avoid wasting any bandwidth.

Project resources
=================

- `Source code <https://github.com/nilicule/mopidy-audioaddict>`
- `Issue tracker <https://github.com/nilicule/mopidy-audioaddict/issues>`

Bugs, feedback and patches are always welcome!