Welcome to Navi-X for Boxee v1.45

Changelog:
-------------------------------------------------------------------------------
1.45
-Nested "if" statements
-Updated portal references to point to navixtreme.com

-------------------------------------------------------------------------------
1.44
-Fixed HTML-only playback

-------------------------------------------------------------------------------
1.43
-Delay method modified in "countdown" method; now checks internal hardware clock
 10x per second instead of relying on Python's "sleep" method

-------------------------------------------------------------------------------
1.42
-"countdown" method added to NIPL interpreter
-multiple conditions per if/elseif statement
-"error" method accepts a variable as an argument
-CURLLoader.urlopen and CPlayer.play_URL return an object instead of a single integer as their result. This enables the following (so far):
   processors can produce custom error messages
   processors can redirect to a playlist from a type=video/audio

-------------------------------------------------------------------------------

1.4
-Improved HTML support. Mouse and keyboard controls are now support.
-Moved the Navi-X media portal to the Navi-Xtreme website. Visit Navi-Xtreme at http://navix.turner3d.net/.

This version has been tested on:
-Boxee 0.9.23.15885 (vWindows XP)
-Boxee Box

-------------------------------------------------------------------------------
