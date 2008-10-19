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
from libs2 import *
from settings import *
from CURLLoader import *
from CFileLoader import *

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

#####################################################################
# Description: My player class, overrides the XBMC Player
######################################################################
class CPlayer(xbmc.Player):
    def  __init__(self, core, function):
        self.function=function
        self.core=core
        self.stopped=False
        self.pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
#        self.pls.clear()

        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        self.function(1)
    
    def onPlayBackEnded(self):
        self.stopped=True
        self.function(2)
        
    def onPlayBackStopped(self):
        self.stopped=True
        self.function(3)

    ######################################################################
    # Description: Play the video, audio in the playlist
    # Parameters : playlist = the input playlist containing all items
    #              first = index of first item
    #              lasts = index of last item
    # Return     : 0 if succesful, -1 if no audio, video files in list
    ######################################################################    
    def play(self, playlist, first, last):
        self.pls.clear()

        if first == last:
            URL = playlist.list[first].URL
            xbmc.Player.play(self, URL)
        else:
#            self.pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        
            index = first
            urlopener = CURLLoader()
            self.stopped=False
            while index <= last and self.stopped == False and self.pls.size() < 100:                
                type = playlist.list[index].type
                if type == 'video' or type == 'audio':
                    URL = playlist.list[index].URL

                    result = urlopener.urlopen(URL)
                    if result == 0:
                        loc_url = urlopener.loc_url

                        name = playlist.list[index].name
                        self.pls.add(loc_url, name)
                        
                        if self.pls.size() == 1:
                            #start playing                        
                            xbmc.Player.play(self, self.pls)
                index = index + 1
            
            if self.pls.size() == 0:
                #no valid items found
                return -1
                
            #start playing
#            xbmc.Player.play(self, self.pls)
            
        return 0
        
    def play_URL(self, URL):
        #check if the URL is empty or not
        if URL == '':
            return -1
    
        self.pls.clear() #clear the playlist
    
        ext = getFileExtension(URL)
        if ext == 'pls' or ext == 'm3u':
            loader = CFileLoader() #file loader
            loader.load(URL, cacheDir + "playlist." + ext)
            if loader.state == 0: #success
#                playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
#                playlist.clear()
#                result = playlist.load(loader.localfile)
                result = self.pls.load(loader.localfile)
                if result == False:
                    return -1
#                loc_url = playlist
        else:
            urlopener = CURLLoader()
            result = urlopener.urlopen(URL)
            if result != 0:
                return -1
#            loc_url = urlopener.loc_url
            self.pls.add(urlopener.loc_url)

#        xbmc.Player.play(self, loc_url)
        xbmc.Player.play(self, self.pls)
        return 0
        
