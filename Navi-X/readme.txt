Welcome to Navi-X v3.7.4

-= What's New =-

NIPL updates:
-added "literal_eval" function for safely converting strings into dictionary objects
-added "data" property to lists and entries - to be used for python dictionaries
-nested "if" statements now supported in NIPL
-fixed issue with "None" type values returned by regex captures with alternation

Downloader updates:
-eliminated multiple server queries for megaupload / megavideo entries
-implemented XBMC-style custom headers - URL|header1=val1&header2=val2&...
-improved extension detection
  * accurately determines extension from processed Youtube videos
  * added a "safety net" which will fall back to an ".avi" extension if the parsed extension is too long

General:
-replaced deprecated os.getcwd() with xbmcaddon.Addon.getAddonInfo('path') for upcoming XBMC eden release
