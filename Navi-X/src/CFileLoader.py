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
import shutil
import zipfile
from settings import *
from libs2 import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

class CFileLoader:
    ######################################################################
    # Description: Downloads a file in case of URL and returns absolute
    #              path to the local file.
    # Parameters : URL=source
    #              file=destination
    #              timeout(optional)=Funtion time out time.
    # Return     : -
    ######################################################################
    def load(self, URL, localfile='', timeout=url_open_timeout, proxy="CACHING", content_type= '', retries=0):
        if (URL == ''):# or (localfile == ''):
            self.state = -1 #failed
            return
        
        self.data=''        
        
        if URL[:4] == 'http':
            sum_str = ''
            if proxy != "DISABLED":
                sum = 0
                #calculate hash of URL
                for i in range(len(URL)):
                    sum = sum + (ord(URL[i]) * i)
                sum_str = str(sum)

            if localfile != '':
                ext_pos = localfile.rfind('.') #find last '.' in the string
                if ext_pos != -1:
                    localfile = localfile[:ext_pos] + sum_str + localfile[ext_pos:]
                else:
                    localfile = localfile + sum_str

            if (not((proxy == "ENABLED") and (os.path.exists(localfile) == True))):
                oldtimeout=socket_getdefaulttimeout()
                socket_setdefaulttimeout(timeout)
                self.state = -1 #failure
                counter = 0
                while (counter <= retries) and (self.state != 0):
                    counter = counter + 1
                    try:
                        f = urllib.urlopen(URL)

                        headers = f.info()
                        type = headers['Content-Type']
                        type = type.lower()
                    
#                    Trace(str(headers))
                    
                        if (content_type != '') and (type.find(content_type)  == -1):
                            #unexpected type, do not retry again
                            #socket_setdefaulttimeout(oldtimeout)            
                            self.state = -2 #failed
                            #return
                            break #do not try again

                        #open the destination file
                        self.data = f.read()
                        if localfile != '':
                            file = open(localfile, "wb")   
                            file.write(self.data)
                            file.close()
                        f.close()   

                        self.localfile = localfile
                        self.state = 0 #success                          
                  
                    except IOError:
                        #socket_setdefaulttimeout(oldtimeout)            
                        self.state = -1 #failed

                socket_setdefaulttimeout(oldtimeout)
            else: #file is inside the cache
                self.localfile = localfile
                self.state = 0 #success          
#@todo
        elif (URL[1] == ':') or (URL[0] == '/'): #absolute (local) path
            self.localfile = URL
            self.state = 0 #success
        else: #assuming relative (local) path
            self.localfile = RootDir + URL        
            self.state = 0 #success


class CFileLoader2:
    ######################################################################
    # Description: Downloads a file in case of URL and returns absolute
    #              path to the local file.
    # Parameters : URL=source, localfile=destination
    # Return     : -
    ######################################################################
    def load(self, URL, localfile='', timeout=url_open_timeout, proxy="CACHING", content_type= '', retries=0):
        if (URL == ''):# or (localfile == ''):
            self.state = -1 #failed
            return
        
        destfile = localfile       
        self.data=''
        
        if URL[:4] == 'http':
            sum_str = ''
            if proxy != "DISABLED":
                sum = 0
                #calculate hash of URL
                for i in range(len(URL)):
                    sum = sum + (ord(URL[i]) * i)
                sum_str = str(sum)
            
            if localfile != '':
                ext_pos = localfile.rfind('.') #find last '.' in the string
                if ext_pos != -1:
                    destfile = localfile[:ext_pos] + sum_str + localfile[ext_pos:]
                else:
                    destfile = localfile + sum_str
            else:
                destfile = cacheDir + sum_str  

            if (not((proxy == "ENABLED") and (os.path.exists(destfile) == True))):
                oldtimeout=socket_getdefaulttimeout()
                socket_setdefaulttimeout(timeout)
                self.state = -1 #failure
                counter = 0
                
                while (counter <= retries) and (self.state != 0):
                    counter = counter + 1 
                    try:
                        oldtimeout=socket_getdefaulttimeout()
                        socket_setdefaulttimeout(timeout)
            
                        values = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)'}
                        req = urllib2.Request(URL, None, values)
                        #req = urllib2.Request(URL)
                        f = urllib2.urlopen(req)
                
                        headers = f.info()
                        
                        #Trace(str(headers))
                        
                        type = headers['Content-Type']
                    
                        if (content_type != '') and (type.find(content_type)  == -1):
                            #unexpected type
                            socket_setdefaulttimeout(oldtimeout)            
                            self.state = -1 #failed
                            #return
                            break #do not try again                            
                        
                        #open the destination file
                        self.data = f.read()
                        #if localfile != '':
                        file = open(destfile, "wb")   
                        file.write(self.data)
                        file.close()
                        f.close()                          
                       
                        self.localfile = destfile
                        self.state = 0 #success       
                  
                    except IOError:
                        #socket_setdefaulttimeout(oldtimeout)            
                        self.state = -1 #failed

#                   except urllib2.HTTPError:
#                       socket_setdefaulttimeout(oldtimeout)
#
#                       Trace("There was an http error: ")
#                       self.state = -1 #failed

#                   except urllib2.URLError, e:
#                       socket_setdefaulttimeout(oldtimeout)
#
#                       Trace("There is a problem with the URL: " + str(e.reason))
#                       self.state = -1 #failed

                socket_setdefaulttimeout(oldtimeout)                  
            else: #file is inside the cache
                self.localfile = destfile
                self.state = 0 #success
                
                if localfile == '':
                    try:
                        f = open(self.localfile, 'r')
                        self.data = f.read()
                        f.close()
                    except IOError:
                        self.state =  -1 #failed                              
                
        else: #localfile    
            if (URL[1] == ':') or (URL[0] == '/'): #absolute (local) path
                self.localfile = URL
                self.state = 0 #success
            else: #assuming relative (local) path
                self.localfile = RootDir + SEPARATOR + URL
                self.state = 0 #success
            
#            Trace(self.localfile)
            
            if localfile == '':
                try:
                    f = open(self.localfile, 'r')
                    self.data = f.read()
                    f.close()
                except IOError:
                    self.state =  -1 #failed
            
           

        
