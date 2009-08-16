#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CURLLoader:
# This class Retrieves the URL to a media item which the XBMC player 
# understands.
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from libs2 import *
from settings import *
from CFileLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

class CURLLoader:
    def __init__(self, parent=0):
        self.parent=parent
        
    ######################################################################
    # Description: This class is used to retrieve the direct URL of given
    #              URL which the XBMC player understands.
    #              
    # Parameters : URL=source URL, mediaitem = mediaitem to open
    # Return     : 0=successful, -1=fail
    ######################################################################
    def urlopen(self, URL, mediaitem=0):
        result = 0 #successful
          
        if URL[:4] == 'http':
            if mediaitem.processor != '':
                result = self.geturl_processor(mediaitem)
            else:
                pos = URL.rfind('http://') #find last 'http://' in the URL
                loc_url = URL[pos:]
                    
                try:
                    oldtimeout=socket_getdefaulttimeout()
                    socket_setdefaulttimeout(url_open_timeout)

                    self.f = urllib.urlopen(loc_url)
                    self.loc_url=self.f.geturl()             
                
                except IOError:
                    self.loc_url = "" #could not open URL
                    socket_setdefaulttimeout(oldtimeout)            
                    return -1 #fail

                socket_setdefaulttimeout(oldtimeout)
                
                #post processing for youtube files
                pos = URL.find('http://youtube.com') #find last 'http' in the URL
                if pos != -1:
                    result = self.geturl_youtube(self.loc_url)
        else:
            self.loc_url = URL
        
        return result

    ######################################################################
    # Description: This class is used to retrieve the URL of a FlyUpload
    #              webpage
    #              
    # Parameters : URL=source URL
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_youtube(self, URL):
        #retrieve the flv file URL
        #URL parameter is not used.
        #Trace("voor "+self.loc_url)

        id=''
        #pos = self.loc_url.find('&video_id=') #find last 'http' in the URL
        #if pos != -1:
        #    pos2 = self.loc_url.find('&',pos+1) #find last 'http' in the URL
        #    id = self.loc_url[pos+10:pos2] #only the video ID
        pos = self.loc_url.rfind('/')
        pos2 = self.loc_url.rfind('.swf')
        id = self.loc_url[pos+1:pos2] #only the video ID

        #Trace(id)
               
        try:
            oldtimeout=socket_getdefaulttimeout()
            socket_setdefaulttimeout(url_open_timeout)

            #retrieve the timestamp based on the video ID
            #self.f = urllib.urlopen("http://www.youtube.com/api2_rest?method=youtube.videos.get_video_token&video_id=" + id)
            self.f = urllib.urlopen("http://youtube.com/get_video_info?video_id=" + id)
            data=self.f.read()
            

            
            #index1 = data.find('<t>')
            #index2 = data.find('</t>')
            index1 = data.find('&token=')
            index2 = data.find('&thumbnail_url')
            if (index1 != -1) and (index2 != -1):
                #t = data[index1+3:index2]
                t = data[index1+7:index2]
                #t contains the timestamp now. Create the URL of the video file (high quality).
                self.loc_url = "http://www.youtube.com/get_video.php?video_id=" + id + "&amp;t=" + t + "&amp;fmt=18"
            else:
                self.loc_url = ""
        
        except IOError:
            self.loc_url = "" #could not open URL
            return -1 #fail
        
        socket_setdefaulttimeout(oldtimeout)
       
        #Trace(self.loc_url)        
        
        if self.loc_url != "":
            return 0 #success
        else:
            return -1 #failure
    

    ######################################################################
    # Description: This class is used to retrieve the URL using a 
    #              processor server
    #              
    # Parameters : mediaitem = mediaitem to open
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_processor(self, mediaitem):
        SetInfoText("Processor: getting filter...")
        arr=get_HTML(mediaitem.processor+'?url='+urllib.quote_plus(mediaitem.URL)).splitlines()
        if len(arr) < 1:
            return -1 # nothing retrieved from processor
        URL=arr[0]
        if len(arr) < 2:
            self.loc_url = URL
            SetInfoText("")
            return 0 # success - final URL output by processor stage 1 - no further processing needed
        filt=arr[1]
        if len(arr) > 2:
            ref=arr[2]
        else:
            ref=''
        if len(arr) > 3:
            cookie=arr[3]
        else:
            cookie=''
            
        SetInfoText("Processor: scraping...")
        htm=get_HTML(URL,ref,cookie)
        if htm == '':
            return -1 #nothing scraped
        p=re.compile(filt)
        match=p.search(htm)
        if match:
            tgt=mediaitem.processor
            sep='?'
            for i in range(1,len(match.groups())+1):
                val=urllib.quote_plus(match.group(i))
                tgt=tgt+sep+'v'+str(i)+'='+val
                sep='&'
            SetInfoText("Processor: processing...")
            arr=get_HTML(tgt).splitlines()
            mediaitem.URL=arr[0]
            if len(arr) > 1:
                mediaitem.swfplayer=arr[1]
                mediaitem.playpath=arr[2]
            if len(arr) > 3:
                mediaitem.pageurl=arr[3]
            mediaitem.processor=''
            
        self.loc_url = mediaitem.URL

        SetInfoText("")
            
        return 0 #success
        

