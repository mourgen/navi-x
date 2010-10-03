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
import ftplib
import os
import socket
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
#class myURLOpener(urllib.FancyURLopener):
#    """Create sub-class in order to overide error 206.  This error means a
#       partial file is being sent,
#       which is ok in this case.  Do nothing with this error.
#    """
#    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
#        pass

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

        self.setDaemon(True) #make a daemon thread   
        
        self.killed = False #not killed
        self.running = False #at startup downloader is not running
        self.shutdown = False #shutdown after all files downloaded

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
        
    def download_isrunning(self):
        return self.running
             
    def kill(self):
        self.killed = True
    
#    def notify(self):
#        self.event.set()
        
    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : entry = media item
    # Return     : self.state (0=success, -1=failure, -2=cancel) 
    #              self.dir (the new selected download dir)
    #              self.localfile (the destination path+file)
    ######################################################################
    def browse(self, entry, dir=myDownloadsDir):
        self.state = 0 #success
        self.dir = ''
       
        URL=entry.URL

        if (URL[:4] != 'http') and (URL[:3] != 'ftp'):
            self.state = -1 #URL does not point to internet file.
            return

        ext, size = self.read_file_info(entry)
        if self.state != 0:
            return
               
        #For the local file name we use the playlist item 'name' field.
        #But this string may contain invalid characters. Therefore
        #we strip these invalid characters. We also limit the file
        #name length to 42 which is the XBMC XBOX limit.

        localfile = re.sub('[^\w\s-]', '', entry.name) # remove characters which are not a letter, digit, white-space, underscore, or dash
        localfile = re.sub('\s+', ' ', localfile) # convert all instances of multiple spaces to single spaces
        localfile = localfile[:(42-len(ext))] # limit to 42 characters.
        localfile = localfile + ext
                
        size_MB = float(size) / (1024 * 1024)
        heading = "Download File: (Size = %.1f MB)" % size_MB
        
        browsewnd = CDialogBrowse("CBrowseskin.xml", os.getcwd())
        browsewnd.SetFile(dir, localfile, 3, heading)
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

        #end of function.        
        
    ######################################################################
    # Description: Retrieve the file extenstion and size of a URL 
    # Parameters : entry = mediaitem.
    # Return     : the file extension (ext) and file size (size)
    ######################################################################
    def read_file_info(self, entry):
        self.state = 0 #success    
        ext='' #no extension
    
        URL = entry.URL
    
        if URL[:3] == 'ftp':
            #FTP
            ext = getFileExtension(URL)
            if ext != '':
                ext = '.' + ext
        else:
            #HTTP
            urlopener = CURLLoader()
            result = urlopener.urlopen(URL, entry)
            if result != 0:
                self.state = -1 #URL does not point to internet file.
                return
            loc_url = urlopener.loc_url

            #Now we try to open the URL. If it does not exist an error is
            #returned.
            try:
                headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)'}
                req = urllib2.Request(loc_url, None, headers)
                f = urllib2.urlopen(req)
                loc_url=f.geturl()
                size_string = f.headers['Content-Length']
                size = int(size_string) #The remaining bytes

            except IOError:
                self.state = -1 #failed to open the HTTP URL
                return
            
            #special handing for some URL's
            pos = URL.find('http://www.youtube.com') #find last 'http' in the URL
            if pos != -1:
                ext='.mp4'
            else:
#todo: deprecated            
                pos = URL.find("flyupload.com")
                if pos != -1:
                    ext='.avi'
                else:
                    #extract the file extension
                    url_stripped = re.sub('\?.*$', '', loc_url) # strip GET-method args
                    re_ext = re.compile('(\.\w+)$') # find extension
                    match = re_ext.search(url_stripped)
                    if match is None:
                        ext = ""
                    else:
                        ext = match.group(1)

        return ext, size
        
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
        tmp.processor = entry.processor
        tmp.background = entry.background
        self.playlist_src.add(tmp)
        self.playlist_src.save(RootDir + downloads_queue)

    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : shutdown = true if auto shutdown after download.
    # Return     : -
    ######################################################################
    def download_queue(self, shutdown = False):
        self.state = 0 #success
        
        counter = 0
        
        self.MainWindow.download_logo.setVisible(1)
        self.MainWindow.dlinfotekst.setVisible(1)
        
        while (self.state != -2) and (self.playlist_src.size() > 0) and (self.killed == False) and (self.running == True):
            header = str(counter+1) + " of " + str(self.playlist_src.size()+counter)
            self.download_file(self.playlist_src.list[0], header) #download single file

            if self.state == 0:
                #Download file completed successfully
                self.playlist_src.remove(0)
                self.playlist_src.save(RootDir + downloads_queue)
                counter = counter + 1
            elif self.state == -1:     
                #Downlaod failed
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Error", "Download failed. Retry?") == False:
                    self.playlist_src.remove(0)
                    self.playlist_src.save(RootDir + downloads_queue)
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
            xbmc.shutdown() #shutdown XBMC
        
        self.running = False #disable downloading
        
        self.MainWindow.dlinfotekst.setVisible(0)        
        self.MainWindow.download_logo.setVisible(0)

    ######################################################################
    # Description: Downloads a URL to local disk
    # Parameters : entry =  mediaitem to download
    #              header = header to display (1 of x)
    # Return     : -
    ######################################################################
    def download_file(self, entry, header=""):
        self.state = 0 #success
        
        URL = entry.URL
        localfile = entry.DLloc     
        
        #download of FTP file is handled in a separte function
        if URL[:3] == 'ftp':
            self.download_fileFTP(entry, header)
            return
        
        if URL[:4] != 'http':
            self.state = -1 #URL does not point to internet file.
            return

        #Continue with HTTP download
        self.MainWindow.dlinfotekst.setLabel('(' + header + ')' + " Retrieving file info...") 

        #Get the direct URL to the mediaitem given URL      
        urlopener = CURLLoader()
        result = urlopener.urlopen(URL, entry)
        if result != 0:
            self.state = -1 #failed to download the file
            return        

        URL = urlopener.loc_url
              
        try:
#            oldtimeout=socket_getdefaulttimeout()
#            socket_setdefaulttimeout(url_open_timeout)

            existSize=0 #existing size = 0 Bytes

            if os.path.exists(localfile):
                #Append to the existing file. Because opening a file for append no longer works,
                #we need to copy the existing file in a new file.
                self.MainWindow.dlinfotekst.setLabel("Preparing append to file...")            
                existSize = os.path.getsize(localfile)
                
                #Message("Exist size: " + str(existSize))
                
                backupfile = localfile[0:-1] + '~'
                os.rename(localfile, backupfile)
                
                file2 = open(backupfile, "rb")
                file = open(localfile, "wb")
                bytes= 0
                while (bytes < existSize):
                    chunk = 100 * 1024
                    if (bytes + chunk) > existSize:
                        chunk = existSize-bytes #remainder
                    file.write(file2.read(chunk))
                    bytes = bytes + chunk

                    percent = 100 * bytes / existSize
                    line2 = '(%s) - %d ' % (header, percent) + '%' + ' Append...' 
                    self.MainWindow.dlinfotekst.setLabel(line2)
            
                file2.close()                
                os.remove(backupfile)
               
                #If the file exists, then only download the remainder 
                headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)',
                            'Range' : 'bytes=%s-' % existSize}                          

            else: 
                #file does not exist 
                file = open(localfile, "wb")           
                headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)'}
            
            #destination is already open            

            self.MainWindow.dlinfotekst.setLabel('(' + header + ')' + " Downloading file...")  
            
            req = urllib2.Request(URL, None, headers)
            f = urllib2.urlopen(req)            
                        
            #If the file exists, but we already have the whole thing, don't download again
            size_string = f.headers['Content-Length']
            size = int(size_string) #The remaining bytes
            
            #Message("Remaining: " + str(size))
                        
#todo: size may be existsize if file is downloaded exactly 50%            
            if (size > 0) and (size != existSize):
                bytes = existSize #bytes downloaded already
                size = size + existSize #total size
                #Message("Total: " + str(size))
                
                size_MB = float(size) / (1024 * 1024) #total size MB

                #download in chunks of 100kBytes
                while (bytes < size) and (self.killed == False) and (self.running == True):
                    chunk = 100 * 1024 #100kBytes chunks
                    if (bytes + chunk) > size:
                        chunk = size-bytes #remainder
                    #data = f.read(chunk)
                    file.write(f.read(chunk))
                    bytes = bytes + chunk
                            
                    percent = 100 * bytes / size
                    done = float(bytes) / (1024 * 1024)
                    line2 = '(%s) %.1f MB - %d ' % (header, size_MB, percent) + '%'           
                    self.MainWindow.dlinfotekst.setLabel(line2)
                
                f.close() #close the URL

                if (self.killed == True) or (self.running == False):
                    self.state = -2 #failed to download the file
                        
        except IOError:  
#            socket_setdefaulttimeout(oldtimeout)       
            file.close() #close the destination file 
            self.state = -1 #failed to download the file
            return

        file.close() #close the destination file  
#        socket_setdefaulttimeout(oldtimeout)
  
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
        
        #end of function
            

    ######################################################################
    # Description: Downloads a FTP URL to local disk
    # Parameters : entry =  mediaitem to download
    #              shutdown = true is shutdown after download
    #              header = header to display (1 of x)
    # Return     : -
    ######################################################################            
    def download_fileFTP(self, entry, header=""):
        self.state = 0 #success

        URL = entry.URL
        localfile = entry.DLloc

        self.header = header
        self.MainWindow.dlinfotekst.setLabel('(' + header + ')')
#@todo: move URLparse to another function.
########################
        #Parse URL according RFC 1738: ftp://user:password@host:port/path 
        #There is no standard Python funcion to split these URL's.
        username=''
        password=''        
        port=21
        
        #check for username, password
        index = URL.find('@')
        if index != -1:
            index2 = URL.find(':',6,index)
            if index2 != -1:
                username = URL[6:index2]
                print 'user: ' + username
                password = URL[index2+1:index]
                print 'password: ' + password            
            URL = URL[index+1:]
        else:
            URL = URL[6:]
        
        #check for host
        index = URL.find('/')
        if index != -1:
            host = URL[:index]
            path = URL[index:]
        else:
            host = URL
            path = ''
            
        #retrieve the port
        index = host.find(':')
        if index != -1:
            port = int(host[index+1:])
            host = host[:index]
            
        print 'host: ' + host    
        print 'port: ' + str(port)
            
        #split path and file
        index = path.rfind('/')
        if index != -1:
            file = path[index+1:]
            path = path[:index]
        else:
            file = ''        
        
        print 'path: ' + path
        print 'file: ' + file
########################        
        try:
            self.f = ftplib.FTP()
            self.f.connect(host,port)
        except (socket.error, socket.gaierror), e:
            print 'ERROR: cannot reach "%s"' % host
            self.state = -1 #failed to download the file
            return

        print '*** Connected to host "%s"' % host

        try:
            if username != '':
                self.f.login(username, password)
            else:
                self.f.login()
        except ftplib.error_perm:
            print 'ERROR: cannot login anonymously'
            self.f.quit()
            self.state = -1 #failed to download the file
            return

        print '*** Logged in as "anonymous"'

        try:
            self.f.cwd(path)
        except ftplib.error_perm:
            print 'ERROR: cannot CD to "%s"' % path
            self.f.quit()
            self.state = -1 #failed to download the file
            return

        print '*** Changed to "%s" folder' % path

        #retrieve the file
        self.bytes = 0
        self.file = open(entry.DLloc, 'wb')

        try:
            #f.retrbinary('RETR %s' % file, open(entry.DLloc, 'wb').write)
            self.size = self.f.size(file)
            self.size_MB = float(self.size) / (1024 * 1024)
            self.percent2 = 0
            self.f.retrbinary('RETR %s' % file, self.download_fileFTP_callback)
        except ftplib.error_perm:
            print 'ERROR: cannot read file "%s"' % file
            os.unlink(self.file)
        else:
            print '*** Downloaded "%s" to CWD' % file
        
        self.f.quit()
       
        self.file.close()
       
        if self.state == 0:
            tmp = CMediaItem() #create new item
            tmp.type = entry.type
            tmp.name = entry.name
            tmp.thumb = entry.thumb
            tmp.URL = entry.DLloc
            tmp.player = entry.player
            self.playlist_dst.add(tmp)
            self.playlist_dst.save(RootDir + downloads_complete)    
    
        #end of function

    ######################################################################
    # Description: Downloads a FTP URL to local disk (callback)
    # Parameters : entry =  mediaitem to download
    #              shutdown = true is shutdown after download
    #              header = header to display (1 of x)
    # Return     : -
    ######################################################################       
    def download_fileFTP_callback(self, string):
                
        self.file.write(string)
        
        self.bytes = self.bytes + len(string)
        percent = 100 * self.bytes / self.size
        
        if percent != self.percent2:
            self.percent2 = percent
        
            done = float(self.bytes) / (1024 * 1024)
        
            line2 = '(%s) %.1f MB - %d ' % (self.header, self.size_MB, percent) + '%'
                
            self.MainWindow.dlinfotekst.setLabel(line2)      
        
        if (self.killed == True) or (self.running == False):
            self.state = -2 #failed to download the file
            self.f.abort()
        
        #end of function
        
        

                