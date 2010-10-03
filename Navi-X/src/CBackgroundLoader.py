#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CBackgroundLoader:
# This class loads playlists properties in a separate background task.
# At this moment loading of the thumbnail images are handled by this task.
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
from CFileLoader import *
from libs2 import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

######################################################################
# Description: Background loader thread
######################################################################
class CBackgroundLoader(threading.Thread):
    def __init__(self, *args, **kwargs):
        if (kwargs.has_key('window')): 
            self.MainWindow = kwargs['window']
        else:
            self.MainWindow = 0
       
        threading.Thread.__init__(self)    

        self.setDaemon(True) #make a deamon thread   
       
        self.killed = False
          
        self.counter=0
        
    def run(self):
        while self.killed == False:
            time.sleep(0.3) #delay 0,3 second
            self.UpdateThumb()
            self.UpdateTime()            
    def kill(self):
        self.killed = True
    
#    def notify(self):
#        self.event.set()
               
    ######################################################################
    # Description: Displays the logo or media item thumb on left side of
    #              the screen.
    # Parameters : -
    # Return     : -
    ######################################################################
    def UpdateThumb(self):  
        #playlist = self.MainWindow.pl_focus
        index = self.MainWindow.getPlaylistPosition()
        index2 = -1 #this value never will be reached
        thumb_update = False
                              
        while (self.MainWindow.state_busy == 0) and (index != index2):
            index = self.MainWindow.getPlaylistPosition()
            if index != -1:
                if self.MainWindow.pl_focus.size() > 0:
              
                    self.UpdateRateingImage(index)
                    self.DisplayMediaSource(index) 
                
                    #now update the thumb
                    m = self.MainWindow.pl_focus.list[index].thumb
                      
                    if (m == 'default') or (m == ""): #no thumb image
                        m = self.MainWindow.pl_focus.logo #use the logo instead
                        if m != self.MainWindow.userthumb:
                            self.MainWindow.user_thumb.setVisible(0)
            
                    if m != self.MainWindow.userthumb:
                        #diffent thumb image
                        if (m == 'default') or (m == ""): #no image
                            self.MainWindow.thumb_visible = False
                        elif m != 'previous': #URL to image located elsewhere
#todo:use the HTTP header image content type to determine the file extension
                            ext = getFileExtension(m)
                            loader = CFileLoader2() #file loader
                            #loader.load(m, imageCacheDir + "thumb." + ext, timeout=2, proxy="ENABLED", content_type='image')
                            loader.load(m, imageCacheDir + "thumb." + ext, proxy="ENABLED", content_type='image')
                            if loader.state == 0: #success
                                #next line is fix, makes sure thumb is update.
                                self.MainWindow.thumb_visible = True
                                thumb_update = True
                            else:
                                self.MainWindow.thumb_visible = False
                        self.MainWindow.userthumb = m
                else: #the list is empty
                    self.MainWindow.thumb_visible = False
                
            index2 = self.MainWindow.getPlaylistPosition()

        if self.MainWindow.thumb_visible == True:
            if thumb_update == True:
                self.MainWindow.user_thumb.setVisible(0)
                self.MainWindow.user_thumb.setImage("")
                self.MainWindow.user_thumb.setImage(loader.localfile)

            self.MainWindow.user_thumb.setVisible(1)
        else:
            self.MainWindow.user_thumb.setVisible(0)
            
    ######################################################################
    # Description: Update the time
    # Parameters : -
    # Return     : -
    ######################################################################
    def UpdateTime(self):
        today=datetime.date.today()
        self.MainWindow.dt.setLabel(time.strftime("%A, %d %B | %I:%M %p"))
        
        
    ######################################################################
    # Description: Sets the rating image.
    # Parameters : -
    # Return     : -
    ######################################################################        
    def UpdateRateingImage(self, pos):        
        rating = self.MainWindow.pl_focus.list[pos].rating
        if rating != '':
            self.MainWindow.rating.setImage('rating' + rating + '.png')
            self.MainWindow.rating.setVisible(1)
        else:
            self.MainWindow.rating.setVisible(0)
    
    ######################################################################
    # Description: Display the media source for processor based entries.
    # Parameters : -
    # Return     : -
    ######################################################################        
    def DisplayMediaSource(self, pos):
        str_url=self.MainWindow.pl_focus.list[pos].URL
        str_server_report=""
        if str_url != "" and self.MainWindow.pl_focus.list[pos].type != "playlist":
            match=re_server.search(str_url)
            if match:
                str_server_report= match.group(1)
                if self.MainWindow.pl_focus.list[pos].processor != "":
                    str_server_report = str_server_report + "+"
        SetInfoText(str_server_report)     
