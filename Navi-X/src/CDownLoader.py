#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CDownloader:
# This class handles file downloads in a background task.
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
import threading
from settings import *
from CPlayList import *
from CDialogBrowse import *
from CURLLoader import *
from libs2 import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

######################################################################
# Description: See comments in class body
######################################################################
class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

######################################################################
# Description: File downloader including progress bar. 
######################################################################
class CDownLoader(threading.Thread):
    def __init__(self, *args, **kwargs):
        if (kwargs.has_key('window')): 
            self.MainWindow = kwargs['window']
        if (kwargs.has_key('playlist_src')): 
            self.playlist_src = kwargs['playlist_src']  
        if (kwargs.has_key('playlist_dst')): 
            self.playlist_dst = kwargs['playlist_dst']       
       
        threading.Thread.__init__(self)    

        self.setDaemon(True) #make a deamon thread   
        
        self.killed = False #not killed
        self.running = False #at startup downloader is not running
        self.shutdown = False #shutdown after download

    def run(self):
        while self.killed == False:
            time.sleep(1.0) #delay 1 second
            #check if there are files in the download queue.
            while (self.killed == False) and (self.running == True) and (self.playlist_src.size() > 0):
                #there are files to be downloaded.
                self.download_queue()
    
    def download_start(self, shutdown = False):
        self.shutdown = shutdown
        self.running = True
    
    def download_stop(self):
        self.running = False
             
    def kill(self):
        self.killed = True
    
#    def notify(self):
#        self.event.set()
        
    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : URL=source
    # Return     : -
    ######################################################################
    def browse(self, entry, dir=myDownloadsDir):
        self.state = 0 #success
        self.dir = ''
       
        URL=entry.URL

        if URL[:4] != 'http':
            self.state = -1 #URL does not point to internet file.
            return

        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, entry)
        if result != 0:
            self.state = -1 #URL does not point to internet file.
            return
        loc_url = urlopener.loc_url
##########################
        #Now we try to open the URL. If it does not exist an error is
        #returned.
        try:
            oldtimeout=socket.getdefaulttimeout()
            socket.setdefaulttimeout(url_open_timeout)

            values = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)'}
            req = urllib2.Request(loc_url, None, values)
            f = urllib2.urlopen(req)
            loc_url=f.geturl()
            socket.setdefaulttimeout(oldtimeout)

        except IOError:
            socket.setdefaulttimeout(oldtimeout)
            self.state = -1 #failed to open URL
            return
########################
            
        #special handing for some URL's
        pos = URL.find('http://youtube.com/v') #find last 'http' in the URL
        if pos != -1:
            ext='.mp4'
        else:
            pos = URL.find("flyupload.com")
            if pos != -1:
                ext='.avi'
            else:
                #strip the file extension
                pos = loc_url.rfind('.') #find last '.' in the string
                if pos != -1:
                    ext = loc_url[pos:] #the file extension
                else:
                    ext = ""
               
        #For the local file name we use the playlist item 'name' field.
        #But this string may contain invalid characters. Therefore
        #we strip these invalid characters. We also limit the file
        #name length to 42 which is the XBMC limit.
        localfile = entry.name.replace('<',"")
        localfile = localfile.replace('>',"")
        localfile = localfile.replace('=',"")
        localfile = localfile.replace('?',"")
        localfile = localfile.replace(':',"")
        localfile = localfile.replace(';',"")
        localfile = localfile.replace('"',"")
        localfile = localfile.replace('*',"")
        localfile = localfile.replace('+',"")
        localfile = localfile.replace(',',"")
        localfile = localfile.replace('/',"")
        localfile = localfile.replace('|',"")
        localfile = localfile[:(42-len(ext))] #limit to 42 characters.
        localfile = localfile + ext
                
        browsewnd = CDialogBrowse(parent=self.MainWindow)
        browsewnd.SetFile(dir, localfile, 3)
        browsewnd.doModal()

        if browsewnd.state != 0:
            self.state = -2 #cancel download
            return
        
        self.localfile = browsewnd.dir + browsewnd.filename
        self.dir = browsewnd.dir
        
        #Check if the file already exists
        if os.path.exists(self.localfile):
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Message", "The destination file already exists, continue?") == False:
                self.state = -2 #cancel download

    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : URL=source
    # Return     : -
    ######################################################################
    def add_queue(self, entry):
        self.state = 0 #success

        tmp = CMediaItem() #create new item
        tmp.type = entry.type
        tmp.name = entry.name
        tmp.thumb = entry.thumb
        tmp.URL = entry.URL
        tmp.DLloc = entry.DLloc
        tmp.player = entry.player
        tmp.background = entry.background
        self.playlist_src.add(tmp)
        self.playlist_src.save(RootDir + downloads_queue)

    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : URL=source
    # Return     : -
    ######################################################################
    def download_queue(self, shutdown = False):
        self.state = 0 #success
        
        index = 0
        counter = 0
        size = self.playlist_src.size()
        
        self.MainWindow.download_logo.setVisible(1)
        self.MainWindow.dlinfotekst.setVisible(1)
        
        while (self.state != -2) and (index < self.playlist_src.size()) and (self.killed == False) and (self.running == True):
            header = str(counter+1) + " of " + str(size)
            self.download_file(self.playlist_src.list[0], shutdown, header) #download single file

            if self.state == -1:
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Download failed.")

#@todo: index can be removed            
            if self.state != -2:
                #When not Navi-X shutdown and not downloading stopped by user.
                self.playlist_src.remove(0)
                self.playlist_src.save(RootDir + downloads_queue)
            #else:
            #    index = index + 1
            
            counter = counter + 1
            
            #Display the updated Queue playlist
            if (self.MainWindow.pl_focus == self.MainWindow.downloadqueue) or \
               (self.MainWindow.pl_focus == self.MainWindow.downloadslist):
                self.MainWindow.ParsePlaylist(reload=False) #display download list
               
        if (self.shutdown == True) and (self.killed == False) and (self.running == True):
            self.MainWindow.onSaveSettings()
            self.MainWindow.delFiles(cacheDir) #clear the cache first        
            self.MainWindow.bkgndloadertask.kill()
            self.MainWindow.bkgndloadertask.join(10) #timeout after 10 seconds        
            xbmc.shutdown() #shutdown the X-box
        
        self.running = False #disable downloading
        
        self.MainWindow.dlinfotekst.setVisible(0)        
        self.MainWindow.download_logo.setVisible(0)

    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : URL=source
    # Return     : -
    ######################################################################
    def download_file(self, entry, shutdown = False, header=""):
        self.state = 0 #success
        
        URL = entry.URL
        localfile = entry.DLloc     
        
        if URL[:4] != 'http':
            self.state = -1 #URL does not point to internet file.
            return

        #Get the direct URL to the mediaitem given URL      
        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, entry)
        if result != 0:
            self.state = -1 #failed to download the file
            return        

        URL = urlopener.loc_url
  
        #open the URL and get the direct URL
    
        self.MainWindow.dlinfotekst.setLabel("Getting file from server.")

        try:
            oldtimeout=socket_getdefaulttimeout()
            socket_setdefaulttimeout(url_open_timeout)

            existSize=0
            #myUrlclass = myURLOpener()
            if os.path.exists(localfile):
                file = open(localfile,"ab")
                existSize = os.path.getsize(localfile)
                               
                #If the file exists, then only download the remainder
                #myUrlclass.addheader("User-Agent","Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)")                            
                #myUrlclass.addheader("Range","bytes=%s-" % existSize)   
                headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)',
                            'Range' : 'bytes=%s-' % existSize}                          

            else: #file does not exist
                #open the destination file
                file = open(localfile, "wb")
                headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)'}

            #f = myUrlclass.open(URL)
                      
            req = urllib2.Request(URL, None, headers)
            f = urllib2.urlopen(req)            
            
            #If the file exists, but we already have the whole thing, don't download again
            size_string = f.headers['Content-Length']
            size = int(size_string) #The remaining bytes
            
#todo: size may be existsize if file is downloaded exactly 50%            
            if (size > 0) and (size != existSize):
                if shutdown == True:
                    string = "Downloading + Shutdown " + header
                else:
                    string = "Downloading " + header

#                dialog = xbmcgui.DialogProgress()
#                dialog.create(string, entry.name)
                
                bytes = existSize #bytes downloaded already
                size = size + existSize
                size_MB = float(size) / (1024 * 1024)

                #download in chunks of 100kBytes
                while (bytes < size) and (self.killed == False) and (self.running == True):
                    chunk = 100 * 1024
                    if (bytes + chunk) > size:
                        chunk = size-bytes #remainder
                    file.write(f.read(chunk))
                    bytes = bytes + chunk
            
#                    if(dialog.iscanceled()):
#                        self.state = -2 #cancel download
#                        break
                
                    percent = 100 * bytes / size
                    done = float(bytes) / (1024 * 1024)
                    #line2 = '%.1f MB of %.1f MB copied.' % (done, size_MB)
                    line2 = '%.1f MB - %d ' % (size_MB, percent) + '%'
#                    dialog.update(percent, entry.name, line2)
                
                    self.MainWindow.dlinfotekst.setLabel(line2)
                
#                dialog.close()
                f.close()

                if (self.killed == True) or (self.running == False):
                    self.state = -2 #failed to download the file
                
            
        except IOError:
            #f.close()     
            socket_setdefaulttimeout(oldtimeout)       
            self.state = -1 #failed to download the file
            return

        file.close()      
        socket_setdefaulttimeout(oldtimeout)
  
        #add the downloaded file to the download list
        if self.state == 0:
            tmp = CMediaItem() #create new item
            tmp.type = entry.type
            tmp.name = entry.name
            tmp.thumb = entry.thumb
            tmp.URL = entry.DLloc
            tmp.player = entry.player
            self.playlist_dst.add(tmp)
            self.playlist_dst.save(RootDir + downloads_complete)
    
