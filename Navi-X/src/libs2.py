#############################################################################
#
# Navi-X Playlist browser (additional library functions)
# by rodejo (rodejo16@gmail.com)
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
import socket
from settings import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

######################################################################
# Description: Playlist item class. 
######################################################################
#class CMediaItem:
#    def __init__(self, id='0', type='unknown', version=plxVersion, name='', thumb='default', URL=''):
#        self.id = id        #identifier
#        self.type = type    #type (playlist, image, video, audio, text)
#        self.version = version #playlist version
#        self.name = name    #name as displayed in list view
#        self.thumb = thumb  #URL to thumb image or 'default'
#        self.URL = URL      #URL to playlist entry
######################################################################
class CMediaItem:
    def __init__(self, \
                  type='unknown', \
                  version=plxVersion, \
                  name='', \
                  description='', \
                  date='', \
                  thumb='default', \
                  icon='default', \
                  URL='', \
                  DLloc='', \
                  player='default', \
                  processor='', \
                  playpath='', \
                  swfplayer='', \
                  pageurl='', \
                  background='default'):
        self.type = type    #(required) type (playlist, image, video, audio, text)
        self.version = version #(optional) playlist version
        self.name = name    #(required) name as displayed in list view
        self.description = description    #(optional) description of this item
        self.date = date    #(optional) release date of this item (yyyy-mm-dd)
        self.thumb = thumb  #(optional) URL to thumb image or 'default'
        self.icon = icon  #(optional) URL to icon image or 'default'
        self.URL = URL      #(required) URL to playlist entry
        self.DLloc = DLloc  #(optional) Download location
        self.player = player #(optional) player core to use for playback
        self.processor = processor #(optional) URL to mediaitem processing server 
        self.playpath = playpath #(optional) 
        self.swfplayer = swfplayer #(optional)
        self.pageurl = pageurl #(optional)
        self.background = background #(optional) background image
               
    ######################################################################
    # Description: Get mediaitem type.
    # Parameters : field: field to retrieve (type or attributes)
    # Return     : -
    ######################################################################
    def GetType(self, field=0):
        index = self.type.find(':')
        if index != -1:
            if field == 0:
                value = self.type[:index]
            elif field == 1:
                value = self.type[index+1:]
            else: #invalid field
                value == ''
        else:
            if field == 0:
                value = self.type
            elif field == 1:
                value = ''
            else: #invalid field
                value == ''

        return value
        
######################################################################
# Description: Playlist item class. 
######################################################################
class CHistorytem:
    def __init__(self, index=0, mediaitem=CMediaItem()):
        self.index = index
        self.mediaitem = mediaitem

######################################################################
# Description: Get the file extension of a URL
# Parameters : filename=local path + file name
# Return     : -
######################################################################
def getFileExtension(filename):
    ext_pos = filename.rfind('.') #find last '.' in the string
    if ext_pos != -1:
        ext_pos2 = filename.rfind('?', ext_pos) #find last '.' in the string
        if ext_pos2 != -1:
            return filename[ext_pos+1:ext_pos2]
        else:
            return filename[ext_pos+1:]
    else:
        return ''

######################################################################
# Description: Get the socket timeout time
# Parameters : -
# Return     : -
######################################################################
def socket_getdefaulttimeout():
    return socket.getdefaulttimeout()

######################################################################
# Description: Set the socket timeout time
# Parameters : time in seconds
# Return     : -
######################################################################
def socket_setdefaulttimeout(url_open_timeout):
    if platform == "xbox":
        socket.setdefaulttimeout(url_open_timeout)
        
######################################################################
# Description: Trace function for debugging
# Parameters : string: text string to trace
# Return     : -
######################################################################
def Trace(string):
    f = open(RootDir + "trace.txt", "a")
    f.write(string + '\n')
    f.close()


######################################################################
# Description: Display popup error message
# Parameters : string: text string to trace
# Return     : -
######################################################################
def Message(string):
    dialog = xbmcgui.Dialog()
    dialog.ok("Error", string)  
    
######################################################################
# Description: Retrieve the platform Navi-X is running on.
# Parameters : -
# Return     : string containing the platform.
######################################################################  
def get_system_platform():
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
#    Trace("Platform: %s"%platform)
    return platform

######################################################################
# Description: Retrieve remote HTML.
# Parameters : URL
# Return     : string containing the page contents.
######################################################################  
def get_HTML(url,referer='',cookie=''):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': referer,
                'Cookie': cookie}
    try:
        oldtimeout=socket_getdefaulttimeout()
        socket_setdefaulttimeout(url_open_timeout)
        req = urllib2.Request(url=url, headers=headers)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except IOError:         
        link = ""
    
    socket_setdefaulttimeout(oldtimeout)
    
    return link
     

######################################################################
# Description: Controls the info text label on the left bottom side
#              of the screen.
# Parameters : folder=path to local folder
# Return     : -
######################################################################
def SetInfoText(text='', window=0):
    global win
    
    if window != 0:
        win=window
        
    if text != '':
        win.setLabel(text)
        win.setVisible(1)
    else:
        win.setVisible(0)

        
#retrieve the platform.
platform = get_system_platform()

        


