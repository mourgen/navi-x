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
                  background='default', \
                  rating=''):
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
        self.rating = rating #(optional) rating value
               
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
# Description: parse FTP URL.
# Parameters : URL, retrieval parameters
# Return     : username, password, host, port, path, file
######################################################################  
class CURLParseFTP:
    def __init__(self, URL):
        #Parse URL according RFC 1738: ftp://user:password@host:port/path 
        #There is no standard Python 2.4 funcion to split these URL's.
        self.username=''
        self.password=''        
        self.port=21
                
        #check for username, password
        index = URL.find('@')
        if index != -1:
            index2 = URL.find(':',6,index)
            if index2 != -1:
                self.username = URL[6:index2]
                print 'user: ' + self.username
                self.password = URL[index2+1:index]
                print 'password: ' + self.password            
            URL = URL[index+1:]
        else:
            URL = URL[6:]
                
        #check for host
        index = URL.find('/')
        if index != -1:
            self.host = URL[:index]
            self.path = URL[index:]
        else:
            self.host = URL
            self.path = ''
                
        #retrieve the port
        index = self.host.find(':')
        if index != -1:
            self.port = int(self.host[index+1:])
            self.host = self.host[:index]
            
        print 'host: ' + self.host    
        print 'port: ' + str(self.port)        
    
        #split path and file
        index = self.path.rfind('/')
        if index != -1:
            self.file = self.path[index+1:]
            self.path = self.path[:index]
        else:
            self.file = ''        
        
        print 'path: ' + self.path
        print 'file: ' + self.file

######################################################################
# Description: Get the file extension of a URL
# Parameters : filename=local path + file name
# Return     : the file extension Excluding the dot
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
    f = open(RootDir + "trace.txt", "w")
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
# Description: Retrieve remote information.
# Parameters : URL, retrieval parameters
# Return     : string containing the page contents.
######################################################################  
def getRemote(url,args={}):
    rdefaults={
        'agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
        'referer': '',
        'cookie': '',
        'method': 'get',
        'action': 'read',
        'postdata': ''
    }
    for ke in rdefaults:
        try:
            args[ke]
        except KeyError:
            args[ke]=rdefaults[ke]
    try:
        hdr={'User-Agent':args['agent'], 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Referer':args['referer'], 'Cookie':args['cookie']}
    except:
        print "Unexpected error:", sys.exc_info()[0]
    try:
#        oldtimeout=socket_getdefaulttimeout()
#        socket_setdefaulttimeout(url_open_timeout)

        if args['method'] == 'get':
            req=urllib2.Request(url=url, headers=hdr)
        else:
            req=urllib2.Request(url,args['postdata'],hdr)
        response = urllib2.urlopen(req)

        if args['action']=='read':
            oret=response.read()
        elif args['action']=='geturl':
            oret=response.geturl()
        elif args['action']=='headers':
            oret=response.info()
        response.close()
    except IOError:         
        oret = ""
    
#    socket_setdefaulttimeout(oldtimeout)
    
    return oret

 
######################################################################
# Description: Creates an addon.xml file (needed for Dharma)
# Parameters : name: shortcut name
#            : path: short pathname in the scripts folder
# Return     : -
######################################################################
def CreateAddonXML(name, path):
    sum = 0
    #calculate hash of name
    for i in range(len(name)):
        sum = sum + (ord(name[i]) * i)
    sum_str = str(sum)

    try:
        f=open(initDir + 'addon.xml', 'r')
        data = f.read()
        data = data.splitlines()
        f.close()
        
        f=open(path + 'addon.xml', 'w')
        for m in data:
            line = m
            if m.find("name=") != -1:
                line = line + '"' + name + '"'
            elif m.find("id=") != -1:
                line = line + '"scrip.navi-x' + sum_str + '"' 
            f.write(line + '\n')
        f.close()     
    except IOError:
        pass

 
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

        


