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
import urllib, urlparse
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
        self.function=function
        self.core=core
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
            return {"code":1, "data":"URL is empty"}
        
        orig_processor = mediaitem.processor   #remember to decide if we show a webpage or play the result of html processing      
        ##mc.ShowDialogOk("Debug in play_URL start", "type = " + mediaitem.type + '\n' + "processor = " + mediaitem.processor) 

        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, mediaitem)
        ##mc.ShowDialogOk("result from urlopen", str(result))
        if result["code"] != 0:
            return result   
        URL = urlopener.loc_url
        ##mc.ShowDialogOk("loc_url", str(URL))
        
#        SetInfoText("Loading... ")

#        self.pls.clear() #clear the playlist
#################################  
        ext = getFileExtension(URL)
        
        #todo ashx  
        if ext == 'ashx':
            ext = 'm3u'
        
        if ext == 'pls' or ext == 'm3u':
            loader = CFileLoader2() #file loader
            loader.load(URL, tempCacheDir + "playlist." + ext, retries=2)
            if loader.state == 0: #success
                URL = loader.localfile
################################# 
        ##mc.ShowDialogOk("Debug in play_URL before play", "type = " + mediaitem.type + '\n' + "processor = " + orig_processor)

        if mediaitem.type == 'html':   #assume html processing returns video?
            if orig_processor == '':  #no actual html processing, just display the webpage using boxee browser
                listitemObj = CreateHTMLListItem(URL)
                if listitemObj["code"]==0:
                    listitem=listitemObj["data"]
                    mc.Player().Play(listitem)
                    return {"code":0}
                else:
                    return listitemObj
            else:  
                listitem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)

        elif mediaitem.type == 'video': 
            listitem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
        elif mediaitem.type == 'audio':
            listitem = mc.ListItem(mc.ListItem.MEDIA_AUDIO_MUSIC)
        else:                      #Player can only play audio or video or html
            return {"code":1,"data":"Item type not supported"}

        listitem.SetLabel(mediaitem.name)
        listitem.SetPath(URL)
        listitem.SetContentType("url")

        if mediaitem.playpath != '':
            self.play_RTMP(mediaitem.URL, mediaitem.playpath, mediaitem.swfplayer, mediaitem.pageurl);
        else:  
#            xbmc.Player.play(self, urlopener.loc_url)
             mc.Player().Play(listitem)
            
        return {"code":0}

    ######################################################################
    ###################################################################### 
    def play_RTMP(self, URL, playpath, swfplayer, pageurl):
        #check if the URL is empty or not
        if URL == '':
            return {"code":1,"data":"URL is empty"}
    
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
        
        return {"code":0}


######################################################################

## CreateHTMLListItem makes a ListItem from url to be used by Boxee integrated browser. The code comes from
## Boxee Browser App, browser.navigate(url) when s_video = False
## that is the display function when the browser is not in "video mode"
## Returns ListItem

def CreateHTMLListItem(url):
	#mc.ShowDialogOk("Debug", "Creating HTMLListItem")
	uri = urlparse.urlparse(url)
	
	if not uri[0]:
		url = "http://" + urlparse.urlunparse(uri)
		uri = urlparse.urlparse(url)
	
	domain = uri[1]
	domain = domain.split('.')
	
	if len(domain) > 2:
		domain = domain[-2:]
	
	domain = ".".join(domain)
	
	badUrl = False

	http = mc.Http()
	if not http.Get(url):
		badUrl = True
	
	if not badUrl:
		
		item = mc.ListItem()
		item.SetLabel("Navi-X Browser")
		item.SetAddToHistory(False)
		item.SetReportToServer(False)
		item.SetContentType("text/html")
		item.SetPath(url)
		#return item
		return {"code":0,"data":item}
	else:
		#mc.ShowDialogOk("Error: html", "The address does not exist or cannot be displayed through the browser.")
		return {"code":1,"data":"The address does not exist or cannot be displayed through the browser."}
        
