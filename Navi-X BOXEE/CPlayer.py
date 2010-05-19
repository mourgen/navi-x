#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CPlayer:
# Video and audio player class which extends the funcionality of the default
# xbmc player class.
#############################################################################

import mc
from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
##import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from libs2 import *
from settings import *
from CURLLoader import *
from CFileLoader import *

##try: Emulating = xbmcgui.Emulating
##except: Emulating = False

#####################################################################
# Description: My player class, overrides the XBMC Player
######################################################################
class CPlayer(mc.Player):
##    def  __init__(self, core, function):
    def  __init__(self, core='', function=''):
##        self.function=function
##        self.core=core
##        self.stopped=False
##        self.pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
#        self.pls.clear()

##        xbmc.Player.__init__(self)
        mc.Player.__init__(self)


    ######################################################################
    ######################################################################            
    def play_URL(self, URL, mediaitem=0):

        ##mc.ShowDialogOk("play_URL", str(URL))
        #URL=mediaitem.URL
        #check if the URL is empty or not
        if URL == '':
            return -1
                
        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, mediaitem)
        ##mc.ShowDialogOk("result from urlopen", str(result))
        if result != 0:
            return -1    
        URL = urlopener.loc_url
        ##mc.ShowDialogOk("loc_url", str(URL))
        
#        SetInfoText("Loading... ")

#        self.pls.clear() #clear the playlist
    
#        ext = getFileExtension(URL)
#        if ext == 'pls' or ext == 'm3u':
#            loader = CFileLoader2() #file loader
#            loader.load(URL, tempCacheDir + "playlist." + ext, retries=2)
#            if loader.state == 0: #success
#                result = self.pls.load(loader.localfile)
#                if result == False:
#                    return -1
#                xbmc.Player.play(self, self.pls) #play the playlist
#        else:
            #self.pls.add(urlopener.loc_url)

        if mediaitem.type == 'video':
            listitem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
        elif mediaitem.type == 'audio':
            listitem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_MUSIC)
        else:                      #Player can only play audio or video
            return -1
          
        listitem.SetLabel(mediaitem.name)
        listitem.SetPath(URL)
        listitem.SetContentType("url")

        if mediaitem.playpath != '':
            self.play_RTMP(mediaitem.URL, mediaitem.playpath, mediaitem.swfplayer, mediaitem.pageurl);
        else:  
#            xbmc.Player.play(self, urlopener.loc_url)
             mc.Player().Play(listitem)
            
        return 0

    ######################################################################
    ###################################################################### 
    def play_RTMP(self, URL, playpath, swfplayer, pageurl):
        #check if the URL is empty or not
        if URL == '':
            return -1
    
##        self.pls.clear() #clear the playlist
    
        listitem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
        listitem.SetLabel('')
        listitem.SetPath(URL)
        listitem.SetContentType("video/x-flv")

        if swfplayer != '':
            listitem.SetProperty("SWFPlayer", swfplayer)      ## not sure if Boxee uses this
        if playpath != '':
            listitem.SetProperty("PlayPath", playpath)
        if pageurl != '':
            listitem.SetProperty("PageURL", pageurl)

        ##mc.ShowDialogOk("Ok", "trying to play rtmp" )
        mc.Player().Play(listitem)
        
        return 0
        
