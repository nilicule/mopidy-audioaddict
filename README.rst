Installation
============

Install by running the following:

    python setup.py install


Configuration
=============

Make sure you enable the extension after you've completed the installation. You will also
need the Mopidy-Stream extension enabled - it's bundled with Mopidy, so unless you disabled it
it should be available.

You may change prefered quality in your Mopidy configuration file:

    [difm]
    enabled = true
    quality = 320k
    api_key = 2398479237492374829384

If you have a DI.FM premium account, fill in your API key. This will allow you to use the higher
quality streams as usual.

For quality you can pick between 40k, 64k, 128k and 320k


Project resources
=================

Bugs, feedback and patches are always welcome at http://github.com/nilicule/mopidy
