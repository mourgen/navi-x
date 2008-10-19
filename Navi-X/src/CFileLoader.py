#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CFileloader:
# This class is a generic file loader and handles downloading a file to disk.
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
#import Image, ImageFile
import shutil
import zipfile
#import socket
from settings import *
from libs2 import *

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
# Description: Downloads a URL to local disk. 
######################################################################
#class CFileLoader:
#    ######################################################################
#    # Description: Downloads a file in case of URL and returns absolute
#    #              path to the local file.
#    # Parameters : URL=source, localfile=destination
#    # Return     : -
#    ######################################################################
#    def load(self, URL, localfile):
#        if URL[:4] == 'http':
#            try:
#                loc = urllib.URLopener()
#                loc.retrieve(URL, localfile)
#            except IOError:
#                self.state = -1 #failed
#                return
#            self.state = 0 #success
#            self.localfile = localfile
#        elif URL[1] == ':': #absolute path
#            self.localfile = URL
#            self.state = 0 #success
#        else: #assuming relative path
#            self.localfile = RootDir + '\\' + URL
#            self.state = 0 #success 

#class CFileLoader3:
#    ######################################################################
#    # Description: Downloads a file in case of URL and returns absolute
#    #              path to the local file.
#    # Parameters : URL=source
#    #              localfile=destination
#    #              timeout(optional)=Funtion time out time.
#    # Return     : -
#    ######################################################################
#    def load(self, URL, localfile, timout=url_open_timeout):
#        if URL[:4] == 'http':
#            try:
#                oldtimeout=socket.getdefaulttimeout()
#                socket.setdefaulttimeout(timout)
#            
#                f = urllib.urlopen(URL)
#                #get the size of the file in bytes
##                size_string=f.info().getheader("Content-Length")
#
#                #open the destination file
#                file = open(localfile, "wb")
#                #file.write(f.read(int(size_string)))
#                file.write(f.read())
#                file.close()          
#                  
#            except IOError:
#                socket.setdefaulttimeout(oldtimeout)            
#                self.state = -1 #failed
#                return
#
#            socket.setdefaulttimeout(oldtimeout)
#                
#            self.localfile = localfile
#            self.state = 0 #success
#            
#        elif URL[1] == ':': #absolute path
#            self.localfile = URL
#            self.state = 0 #success
#        else: #assuming relative path
#            self.localfile = RootDir + '\\' + URL
#            self.state = 0 #success 

#class CFileLoader2:
#    ######################################################################
#    # Description: Downloads a file in case of URL and returns absolute
#    #              path to the local file.
#    # Parameters : URL=source, localfile=destination
#    # Return     : -
#    ######################################################################
#    def load(self, URL, localfile):
#        if URL[:4] == 'http':
#            try:
#                values = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
#                req = urllib2.Request(URL, None, values)
#                f = urllib2.urlopen(req)
#                
#                #open the destination file
#                file = open(localfile, "wb")
#                #file.write(f.read(int(size_string)))
#                file.write(f.read())
#                file.close()          
#                  
#            except IOError:
#                self.state = -1 #failed
#                return
#                
#            self.localfile = localfile
#            self.state = 0 #success
#            
#        elif URL[1] == ':': #absolute path
#            self.localfile = URL
#            self.state = 0 #success
#        else: #assuming relative path
#            self.localfile = RootDir + '\\' + URL
#            self.state = 0 #success 

class CFileLoader:
    ######################################################################
    # Description: Downloads a file in case of URL and returns absolute
    #              path to the local file.
    # Parameters : URL=source
    #              localfile=destination
    #              timeout(optional)=Funtion time out time.
    # Return     : -
    ######################################################################
    def load(self, URL, localfile, timeout=url_open_timeout, proxy="CACHING", content_type= ''):
        if (URL == '') or (localfile == ''):
            self.state = -1 #failed
            return
        
        if URL[:4] == 'http':
            sum_str = ''
            if proxy != "DISABLED":
                sum = 0
                #calculate hash of URL
                for i in range(len(URL)):
                    sum = sum + (ord(URL[i]) * i)
                sum_str = str(sum)

            ext_pos = localfile.rfind('.') #find last '.' in the string
            if ext_pos != -1:
                localfile = localfile[:ext_pos] + sum_str + localfile[ext_pos:]
            else:
                localfile = localfile + sum_str

            if (not((proxy == "ENABLED") and (os.path.exists(localfile) == True))): 
                try:
                    oldtimeout=socket_getdefaulttimeout()
                    socket_setdefaulttimeout(timeout)
            
                    f = urllib.urlopen(URL)

                    headers = f.info()
                    type = headers['Content-Type']
                    
#                    Trace(type)
                    
                    if (content_type != '') and (type.find(content_type)  == -1):
                        #unexpected type
                        socket_setdefaulttimeout(oldtimeout)            
                        self.state = -1 #failed
                        return

                    #open the destination file
                    file = open(localfile, "wb")
                    #file.write(f.read(int(size_string)))
                    file.write(f.read())
                    file.close()          
                  
                except IOError:
                    socket_setdefaulttimeout(oldtimeout)            
                    self.state = -1 #failed
                    return

                socket_setdefaulttimeout(oldtimeout)
                
            self.localfile = localfile
            self.state = 0 #success
            
        elif URL[1] == ':': #absolute (local) path
            self.localfile = URL
            self.state = 0 #success
        else: #assuming relative (local) path
            self.localfile = RootDir + '\\' + URL
            self.state = 0 #success


class CFileLoader2:
    ######################################################################
    # Description: Downloads a file in case of URL and returns absolute
    #              path to the local file.
    # Parameters : URL=source, localfile=destination
    # Return     : -
    ######################################################################
    def load(self, URL, localfile, timout=url_open_timeout, proxy="CACHING"):
        if (URL == '') or (localfile == ''):
            self.state = -1 #failed
            return
        
        if URL[:4] == 'http':
            sum_str = ''
            if proxy != "DISABLED":
                sum = 0
                #calculate hash of URL
                for i in range(len(URL)):
                    sum = sum + (ord(URL[i]) * i)
                sum_str = str(sum)

            ext_pos = localfile.rfind('.') #find last '.' in the string
            if ext_pos != -1:
                localfile = localfile[:ext_pos] + sum_str + localfile[ext_pos:]
            else:
                localfile = localfile + sum_str

            if (not((proxy == "ENABLED") and (os.path.exists(localfile) == True))): 
                try:
                    oldtimeout=socket_getdefaulttimeout()
                    socket_setdefaulttimeout(timout)
            
                    values = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
                    req = urllib2.Request(URL, None, values)
                    f = urllib2.urlopen(req)
                
                    #open the destination file
                    file = open(localfile, "wb")
                    #file.write(f.read(int(size_string)))
                    file.write(f.read())
                    file.close()          
                  
                except IOError:
                    socket_setdefaulttimeout(oldtimeout)            
                    self.state = -1 #failed
                    return

                socket_setdefaulttimeout(oldtimeout)
                
            self.localfile = localfile
            self.state = 0 #success
            
        elif URL[1] == ':': #absolute (local) path
            self.localfile = URL
            self.state = 0 #success
        else: #assuming relative (local) path
            self.localfile = RootDir + '\\' + URL
            self.state = 0 #success
           

        
