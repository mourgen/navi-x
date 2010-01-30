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
import shutil
import zipfile
import socket
from settings import *
from libs2 import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

IMAGE_BG = 102
IMAGE_BG1 = 103
IMAGE_LOGO = 104
IMAGE_THUMB = 105
LABEL_URLLBL = 106
LABEL_VERSION = 107
LABEL_INFOTEXT = 108
LABEL_DLINFOTEXT = 109
LABEL_LOADING = 110
LABEL_LISTPOS = 111
LIST_LIST1 = 112   
BUTTON_HOME = 113
BUTTON_FAVORITES = 114
BUTTON_VIEW = 115
BUTTON_BROWSE = 116
BUTTON_ABOUT = 117
IMAGE_DLLOGO = 118
LABEL_DT = 119
LIST_LIST2 = 120
TEXT_BOX_LIST2 = 121 
LIST_LIST3 = 122
TEXT_BOX_LIST3 = 123
SCROLLBAR_LIST = 2015

######################################################################
# Description: Draws all widgets on the screen during start-up
# Parameters : window: handle to the main window
# Return     : -
######################################################################
def load_skin(window):
    return
    
    #background image
    window.bg = xbmcgui.ControlImage(0,0,720,576, imageDir + background_image)
    window.addControl(window.bg)

    window.bg1 = xbmcgui.ControlImage(0,0,720,576, imageDir + background_image1)
    window.addControl(window.bg1)
    
    #Navi-X logo at top-right position
    window.logo = xbmcgui.ControlImage(570,10,120,80, imageDir + "logo.png")
    window.addControl(window.logo)
            
    #user thumb above the buttons (overlaps with the user logo)
    window.user_thumb = xbmcgui.ControlImage(32,100,210,190, imageDir + "logo.png")
    window.addControl(window.user_thumb)
    window.user_thumb.setVisible(0)
    
    #downloading state at the bottom of screen
    window.download_logo = xbmcgui.ControlImage(40,480,30,30, imageDir + "icon_download.png")
    window.addControl(window.download_logo)
    window.download_logo.setVisible(0)
    
    #URL label at top-center position
    window.urllbl = xbmcgui.ControlLabel(40,60,350,40, "", "special13")   
    window.addControl(window.urllbl)

    #Time + Date label at top-right position
    window.dt = xbmcgui.ControlLabel(270,35,270,40, "", "font12")
    window.addControl(window.dt)      

    #Navi-X Version label at top-left position
    window.version = xbmcgui.ControlLabel(40,20,155,40, 'version: '+ Version+ '.' + SubVersion, "font10")
    window.addControl(window.version)      
    
    #"Loading..." text at down-left side
    window.infotekst = xbmcgui.ControlLabel(60,520,250,30, "Loading...")
    window.addControl(window.infotekst)
    window.infotekst.setVisible(0)
    
    #"Download progress information..." text at down-left side
    window.dlinfotekst = xbmcgui.ControlLabel(80,490,250,30, "")
    window.addControl(window.dlinfotekst)
    window.dlinfotekst.setVisible(0)

    #"Please wait..." text displayed on top of the main list
    window.loading = xbmcgui.ControlLabel(270, 100, 250, 30, "Please wait...")
    window.addControl(window.loading)
    window.loading.setVisible(0)
    
    #list cursor position label displayed at the bottom right of the screen
    window.listpos = xbmcgui.ControlLabel(640,540,250,30, "")
    window.addControl(window.listpos)    
    
    #Main lists displaying playlist entries.
    #Large list 10 entries without text box on top.
    window.list1 = xbmcgui.ControlList(260,100,450,435,'font14','0xFFDDDDDD', buttonFocusTexture=RootDir+'images\\list-focus.png', imageWidth=32, imageHeight=32, itemHeight=38)
    window.addControl(window.list1)
    window.list1.setPageControlVisible(False)

    #Small list 8 entries with text box on top.
    window.list2 = xbmcgui.ControlList(260,210,450,345,'font14','0xFFDDDDDD', buttonFocusTexture=RootDir+'images\\list-focus.png', imageWidth=32, imageHeight=32, itemHeight=38)
    window.addControl(window.list2)
    window.list2.setPageControlVisible(False)

    #Menu option at left side of the screen.
    window.list3 = xbmcgui.ControlList(0,132,200,200,'font14','0xFFDDDDDD', buttonFocusTexture=RootDir+'images\\list-focus2.png', imageWidth=32, imageHeight=32, itemHeight=38)
    window.addControl(window.list3)
    window.list2.setPageControlVisible(False)

    #the small text box above main list 2
    window.list2tb = xbmcgui.ControlTextBox(270, 100, 420, 100)
    window.addControl(window.list2tb)
    window.list2tb.setVisible(0) 

    #set the large list as default
    window.list = window.list1
    
    #buttons creation
#    x=50
#    y=303
#    window.button_home = xbmcgui.ControlButton(x,y,120,32,'      Home', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
#    window.addControl(window.button_home)
#    window.button_favorites = xbmcgui.ControlButton(x,y+32,120,32,'      Favorites', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")            
#    window.addControl(window.button_favorites)            
#    window.button_downloads = xbmcgui.ControlButton(x,y+64,120,32,'      View', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")            
#    window.addControl(window.button_downloads)            
#    window.button_url = xbmcgui.ControlButton(x,y+96,120,32,'      Browse', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
#    window.addControl(window.button_url)
#    window.button_about = xbmcgui.ControlButton(x,y+128,120,32,'      Exit', RootDir + "images\\button-focus1.png", RootDir + "images\\button-nofocus1.png")
#    window.addControl(window.button_about)

    #button behaviour
#    window.list2tb.controlDown(window.list)
#    window.button_home.controlDown(window.button_favorites)
#    window.button_favorites.controlDown(window.button_downloads)
#    window.button_downloads.controlDown(window.button_url)
#    window.button_url.controlDown(window.button_about)
#    window.button_about.controlUp(window.button_url)
#    window.button_url.controlUp(window.button_downloads)
#    window.button_downloads.controlUp(window.button_favorites)
#    window.button_favorites.controlUp(window.button_home)
#    #window.button_home.controlUp(window.list2tb)
#    window.list2tb.controlUp(window.list)

#    window.button_home.controlLeft(window.button_about)
#    window.button_favorites.controlLeft(window.button_about)
#    window.button_downloads.controlLeft(window.button_about)
#    window.button_url.controlLeft(window.button_about)
#    window.list1.controlLeft(window.button_home)
#    window.list2.controlLeft(window.button_home)
#    window.list2tb.controlLeft(window.button_home)


def load_skin1(window):   
    #images
    window.bg = window.getControl(IMAGE_BG)
    window.bg1 = window.getControl(IMAGE_BG1)
    window.logo = window.getControl(IMAGE_LOGO)
    window.user_thumb = window.getControl(IMAGE_THUMB)
    window.download_logo = window.getControl(IMAGE_DLLOGO)
    window.download_logo.setVisible(0)
                 
    #labels
    window.urllbl = window.getControl(LABEL_URLLBL)
    window.dt = window.getControl(LABEL_DT)
    
    window.version = window.getControl(LABEL_VERSION)
    window.version.setLabel('version: '+ Version + '.' + SubVersion)#, "font10")
    
    window.infotekst = window.getControl(LABEL_INFOTEXT)
    window.infotekst.setVisible(False)
    window.dlinfotekst = window.getControl(LABEL_DLINFOTEXT)
    window.dlinfotekst.setVisible(False)
    window.loading = window.getControl(LABEL_LOADING)
    window.loading.setVisible(False)
    window.listpos = window.getControl(LABEL_LISTPOS)
    
    #lists
    window.list1 = window.getControl(LIST_LIST1)
    window.list2 = window.getControl(LIST_LIST2)
    window.list2.setVisible(False)
    window.list3 = window.getControl(LIST_LIST3)
    
    item = xbmcgui.ListItem("Home")   
    window.list3.addItem(item)
    item = xbmcgui.ListItem("Favorites")   
    window.list3.addItem(item)
    item = xbmcgui.ListItem("View")   
    window.list3.addItem(item)
    item = xbmcgui.ListItem("Browse")   
    window.list3.addItem(item)
    item = xbmcgui.ListItem("Exit")   
    window.list3.addItem(item)
    
    #textbox
    window.list2tb = window.getControl(TEXT_BOX_LIST2)
    #window.list2tb.setVisible(False)
 
    #textbox
    window.list3tb = window.getControl(TEXT_BOX_LIST3)
    window.list3tb.setVisible(False) 
 
    #buttons
    #window.button_home = window.getControl(BUTTON_HOME)
    #window.button_favorites = window.getControl(BUTTON_FAVORITES)
    #window.button_downloads = window.getControl(BUTTON_VIEW)
    #window.button_url = window.getControl(BUTTON_BROWSE)
    #window.button_about = window.getControl(BUTTON_ABOUT)
    
    #set the large list as default
    window.list = window.list1
    

