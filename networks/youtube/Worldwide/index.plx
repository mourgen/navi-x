version=5
#playlist properties:
background=default
logo=http://www.navi-x.org/playlists/youtube/logo.png
title=Youtube videos (Worldwide)
#
type=search_youtube
name=Youtube Search
processor=http://www.navixtreme.com/proc/youtube
#
#type=search:rss:video
#name=Youtube Search
#processor=http://www.navixtreme.com/proc/youtube
#URL=http://gdata.youtube.com/feeds/base/videos?max-results=50&alt=rss&q=
#
type=rss:video
name=Most Recent
processor=http://www.navixtreme.com/proc/youtube
URL=http://gdata.youtube.com/feeds/base/standardfeeds/most_recent?max-results=50&alt=rss&format=6
#
type=playlist
name=Most Viewed
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/MV.plx
#
type=playlist
name=Top Rated
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/TR.plx
#
type=playlist
name=Top Favorites
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/TF.plx
#
type=playlist
name=Most Discussed
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/MD.plx
#
type=playlist
name=Most Linked
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/ML.plx
#
type=playlist
name=Most Responded
URL=http://navi-x.googlecode.com/svn/trunk/networks/youtube/Worldwide/MR.plx
#
type=rss:video
name=Recently Featured
processor=http://www.navixtreme.com/proc/youtube
URL=http://gdata.youtube.com/feeds/mobile/standardfeeds/recently_featured?max-results=50&alt=rss
#