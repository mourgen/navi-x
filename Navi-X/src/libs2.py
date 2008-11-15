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

RootDir = os.getcwd()
if RootDir[-1]==';': RootDir=RootDir[0:-1]
if RootDir[-1]!='\\': RootDir=RootDir+'\\'
imageDir = RootDir + "\\images\\"
cacheDir = RootDir + "\\cache\\"
imageCacheDir = RootDir + "\\cache\\imageview\\"
scriptDir = "Q:\\scripts\\"
myDownloadsDir = RootDir + "My Downloads\\"
initDir = RootDir + "\\init\\"

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
    def __init__(self, type='unknown', version=plxVersion, name='', thumb='default', URL='', DLloc='', player='default', background='default'):
        self.type = type    #(required) type (playlist, image, video, audio, text)
        self.version = version #(optional) playlist version
        self.name = name    #(required) name as displayed in list view
        self.thumb = thumb  #(optional) URL to thumb image or 'default'
        self.URL = URL      #(required) URL to playlist entry
        self.DLloc = DLloc  #(optional) Download location
        self.player = player #(optional) player core to use for playback
        self.background = background #(optional) background image
        
######################################################################
# Description: Playlist item class. 
######################################################################
class CHistorytem:
    def __init__(self, index=0, mediaitem=CMediaItem()):
        self.index = index
        self.mediaitem = mediaitem

#class CHistorytem2:
#    def __init__(self, URL='', index=0, type='unknown'):
#        self.URL = URL        
#        self.index = index
#        self.type = type
 

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
        
 