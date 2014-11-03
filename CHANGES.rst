Changelog
=========
v0.2.6 (2014-11-03)
-------------------
- Added proxy support
- Cleaning up tests folder in preparation of new unit tests

v0.2.5 (2014-11-02)
-------------------
- Be slightly more verbose on API authentication, premium status, number of channels found
- Fixed bug where stations were shown in channel list

v0.2.4 (2014-11-02)
-------------------
- Fixed bug where disabled stations were still shown in Mopidy
- Most configuration settings are now optional
- Cleaned up README.rst

v0.2.3 (2014-11-02)
-------------------
- Username and password are now completely optional

v0.2.2 (2014-11-02)
-------------------
- Fix bug for users without premium, but with a valid AudioAddict API key

v0.2.1 (2014-11-02)
-------------------
- Fixed bug for users without premium, now picks correct stream URL
- Only attempt to get API key when authentication details are available
- Bumped version number to avoid confusion with earlier retracted 0.2 release

v0.1.1 (2014-10-13)
-------------------
- Renamed project to Mopidy-AudioAddict
- Added support for the entire AudioAddict network. The extension
  now plays DI.FM, RadioTunes, RockRadio, JazzRadio and FrescaRadio
- No need to figure out your API key anymore, just enter your username
  and password in the Mopidy configuration

v0.1.0 (2014-08-12)
-------------------
- Initial release
