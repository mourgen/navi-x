#############################################################################
#
# Navi-X Playlist browser (additional library functions)
# by rodejo (rodejo16@gmail.com)
#############################################################################

ACTION_MOVE_LEFT       =  1 #Dpad Left
ACTION_MOVE_RIGHT      =  2 #Dpad Right
ACTION_MOVE_UP         =  3 #Dpad Up
ACTION_MOVE_DOWN       =  4 #Dpad Down
ACTION_PAGE_UP         =  5 #Left trigger
ACTION_PAGE_DOWN       =  6 #Right trigger
ACTION_SELECT_ITEM     =  7 #'A'
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9 #'B'
ACTION_PREVIOUS_MENU   = 10 #'Back'
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13 #'Start'
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_XBUTTON	       = 18 #'X'
ACTION_YBUTTON 	       = 34	#'Y'
ACTION_CONTEXT_MENU    = 117 # pops up the context menu
ACTION_CONTEXT_MENU2   = 229 # pops up the context menu (remote control "title" button)


#############################################################################
# auto scaling values
#############################################################################

HDTV_1080i = 0      #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p = 1       #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3 = 2   #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9 = 3  #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3 = 4        #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9 = 5       #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3 = 6         #(720x576, 4:3, pixels are 128:117)
PAL_16x9 = 7        #(720x576, 16:9, pixels are 512:351)
PAL60_4x3 = 8       #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9 = 9      #(720x480, 16:9, pixels are 5760:4739)


#############################################################################
# directory settings
#############################################################################
import os
RootDir = os.getcwd()
if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[0] == '/':
    if RootDir[-1] != '/': RootDir = RootDir+'/'
    myDownloadsDir = RootDir + "My Downloads/"
    initDir = RootDir + "init/"
    myPlaylistsDir = RootDir + "My Playlists/"
    srcDir = RootDir + "src/"
    #imageDir = RootDir + "images/"
    imageDir = RootDir + "resources/skins/Default/media/"
    cacheDir = RootDir + "cache/"
    imageViewCacheDir = RootDir + "cache/mageview/"
    imageCacheDir = RootDir + "cache/images/"
    tempCacheDir = RootDir + "cache/temp/"    
    SEPARATOR = '/'
else:
    if RootDir[-1] != '\\': RootDir = RootDir+'\\'
    myDownloadsDir = RootDir + "My Downloads\\"
    initDir = RootDir + "init\\"
    myPlaylistsDir = RootDir + "My Playlists\\"
    srcDir = RootDir + "src\\"
    #imageDir = RootDir + "images\\"
    imageDir = RootDir + "resources\\skins\\Default\\media\\"
    cacheDir = RootDir + "cache\\"
    imageViewCacheDir = RootDir + "cache\\imageview\\"
    imageCacheDir = RootDir + "cache\\images\\"
    tempCacheDir = RootDir + "cache\\temp\\"    
    SEPARATOR = '\\'

import xbmc
version = xbmc.getInfoLabel("System.BuildVersion")[:1]

if version == '9':
    scriptDir = "special://home/scripts/"
    pluginDir = "special://home/plugins/"
    skinDir = "special://home/skin/"
else: 
    scriptDir = "Q:\\scripts\\"
    pluginDir = "Q:\\plugins\\"
    skinDir = "Q:\\skin\\"


######################################################################
Version='3' #program version
SubVersion='1'

favorite_file='favorites.plx' #the favorite list is also a playlist
downloads_file='downlmenu.plx' #the downloads list is also a playlist
downloads_queue='downlqueue.plx'
downloads_complete='downloads.plx'
parent_list='blacklist.plx'
history_list='history.plx'
plxVersion = '8'
home_URL_old='http://www.navi-x.nl/playlists/home.plx'
home_URL='http://www.navi-x.org/playlists/home.plx'
home_URL_mirror='http://navi-x.googlecode.com/svn/trunk/Playlists/home.plx'
background_image1 = 'background1.jpg'
background_image2 = 'background2.png'

url_open_timeout = 10 #10 seconds
page_size = 200 #display maximum 100 entries on one page
history_size = 50 #maximum of entries in the history list

