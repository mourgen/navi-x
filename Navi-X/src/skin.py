#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# skin.py:
# This file loads the GUI elements on the main screen.
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
# Description: Draws all widgets on the screen during start-up
# Parameters : window: handle to the main window
# Return     : -
######################################################################
def load_skin(window):
    #background image
    window.bg = xbmcgui.ControlImage(0,0,720,576, imageDir + "background.png")
    window.addControl(window.bg)

    window.bg1 = xbmcgui.ControlImage(0,0,720,576, imageDir + "background.png")
    window.addControl(window.bg1)
    
    #Navi-X logo at top-right position
    window.logo = xbmcgui.ControlImage(620,20,80,80, imageDir + "logo.png")
    window.addControl(window.logo)

    #user logo below the buttons
    window.user_logo = xbmcgui.ControlImage(32,120,210,172, imageDir + "logo.png")
    window.addControl(window.user_logo)
    window.user_logo.setVisible(0)
            
    #user thumb below the buttons (overlaps with the user logo)
    window.user_thumb = xbmcgui.ControlImage(32,120,210,172, imageDir + "logo.png")
    window.addControl(window.user_thumb)
    window.user_thumb.setVisible(0)
    
    #URL label at top-center position
    window.urllbl = xbmcgui.ControlLabel(40,80,350,40, "", "font14")
    window.addControl(window.urllbl)

    #Navi-X Version label at top-left position
    window.version = xbmcgui.ControlLabel(40,20,155,40, 'version: '+ Version+ '.' + SubVersion, "font14")
    window.addControl(window.version)      
    
    #"Loading..." text at down-left side
    window.infotekst = xbmcgui.ControlLabel(80,500,250,30, "Loading...")
    window.addControl(window.infotekst)
    window.infotekst.setVisible(0)

    #"Please wait..." text displayed on top of the main list
    window.loading = xbmcgui.ControlLabel(280, 130, 250, 30, "Please wait...")
    window.addControl(window.loading)
    window.loading.setVisible(0)
    
    #Main lists displaying playlist entries.
    #Large list 10 entries without text box on top.
    window.list1 = xbmcgui.ControlList(260,120,450,435,'font14','0xFFDDDDDD', buttonFocusTexture=RootDir+'images\\list-focus.png', imageWidth=32, imageHeight=32, itemHeight=38)
    window.addControl(window.list1)
    window.list1.setPageControlVisible(False)

    #Small list 8 entries with text box on top.
    window.list2 = xbmcgui.ControlList(260,210,450,345,'font14','0xFFDDDDDD', buttonFocusTexture=RootDir+'images\\list-focus.png', imageWidth=32, imageHeight=32, itemHeight=38)
    window.addControl(window.list2)
    window.list2.setPageControlVisible(False)

    #the text box above main list 2
    window.list2tb = xbmcgui.ControlTextBox(270, 115, 420, 85)
    window.addControl(window.list2tb)
    window.list2tb.setVisible(0)

    #set the large list as default
    window.list = window.list1

    #list cursor position label displayed at the bottom right of the screen
    window.listpos = xbmcgui.ControlLabel(640,540,250,30, "")
    window.addControl(window.listpos)
    
    #buttons creation
    x=50
    y=303
    window.button_home = xbmcgui.ControlButton(x,y,120,32,'      Home', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
    window.addControl(window.button_home)
    window.button_favorites = xbmcgui.ControlButton(x,y+32,120,32,'      Favorites', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")            
    window.addControl(window.button_favorites)            
    window.button_downloads = xbmcgui.ControlButton(x,y+64,120,32,'      Downloads', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")            
    window.addControl(window.button_downloads)            
    window.button_url = xbmcgui.ControlButton(x,y+96,120,32,'      Browse', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
    window.addControl(window.button_url)
    window.button_about = xbmcgui.ControlButton(x,y+128,120,32,'      About', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
    window.addControl(window.button_about)

    #button behaviour
    window.list2tb.controlDown(window.list1)
    window.button_home.controlDown(window.button_favorites)
    window.button_favorites.controlDown(window.button_downloads)
    window.button_downloads.controlDown(window.button_url)
    window.button_url.controlDown(window.button_about)
    window.button_about.controlUp(window.button_url)
    window.button_url.controlUp(window.button_downloads)
    window.button_downloads.controlUp(window.button_favorites)
    window.button_favorites.controlUp(window.button_home)
    window.button_home.controlUp(window.list2tb)

    window.button_home.controlRight(window.list1)
    window.button_favorites.controlRight(window.list1)
    window.button_downloads.controlRight(window.list1)
    window.button_url.controlRight(window.list1)
    window.button_about.controlRight(window.list1)
    window.list1.controlLeft(window.button_home)
    window.list2.controlLeft(window.button_home)
    window.list2tb.controlLeft(window.button_home)
  

