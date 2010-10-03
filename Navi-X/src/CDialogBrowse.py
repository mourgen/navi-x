#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CDialogBrowse:
# This class is a non-standard dialog window which is used for downloading 
# and file selection.
#@todo: Use WindowXMLDialog instead of the WindowDialog for better customization
#@todo: fix layout issues for non-XBOX platforms.
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

try: Emulating = xbmcgui.Emulating
except: Emulating = False

LABEL_TITLE = 141
BUTTON_PATH = 142
BUTTON_BROWSE = 143
BUTTON_OK = 144
BUTTON_CANCEL = 145

######################################################################
# Description: Browse dialog class
######################################################################
class CDialogBrowse(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath):
        self.setCoordinateResolution(PAL_4x3)
        self.filename=''
        self.dir=''
    
    def onInit( self ):           
        control=self.getControl(LABEL_TITLE)
        control.setLabel(self.label)
      
        self.SetLabel(self.dir + self.filename)
      
        control=self.getControl(BUTTON_OK)
        self.setFocus(control) 
             
    def onAction(self, action):
        #select item is handled via other onClick().
        if not action.getId() == ACTION_SELECT_ITEM:
            self.onAction1(action)        
        
    def onAction1(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_PARENT_DIR:
            self.state = -1 #success
            self.close() #exit
                       
        if action == ACTION_SELECT_ITEM:
            if self.getFocus() == self.getControl(BUTTON_OK):
                if os.path.exists(self.dir) == False:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Destination directory does not exist")
                else:
                    self.state = 0 #success
                    self.close() #exit
            if self.getFocus() == self.getControl(BUTTON_CANCEL):
                self.state = -1 #success
                self.close() #exit
            if self.getFocus() == self.getControl(BUTTON_PATH):
                keyboard = xbmc.Keyboard(self.dir + self.filename)
                keyboard.doModal()
                
                if (keyboard.isConfirmed() == True):
                    fn = keyboard.getText()
                    pos = fn.rfind(SEPARATOR) #find last '\' in the string
                    if pos != -1:
                        self.dir = fn[:pos+1]
                        filename = fn[pos+1:]
                        if len(filename) > 42:
                            dialog = xbmcgui.Dialog()
                            dialog.ok("Error", "Filename exceeds 42 characters.")
                        else:
                            self.filename = filename
                            
                    self.SetLabel(self.dir + self.filename)

            if self.getFocus() == self.getControl(BUTTON_BROWSE):             
                dialog = xbmcgui.Dialog()
                fn = dialog.browse(self.type,'Xbox Media Center', 'files', '', False, False)
                if fn:
                    if self.type == 3:
                        if fn[-1] != SEPARATOR:
                            fn = fn + SEPARATOR
                            
                        self.dir = fn
                    else:
                        pos = fn.rfind(SEPARATOR) #find last '\' in the string
                        if pos != -1:
                            self.dir = fn[:pos+1]
                            filename = fn[pos+1:]
                            self.filename = filename
                    
                    self.SetLabel(self.dir + self.filename)

    def onFocus( self, controlId ):
        pass
            
    def onClick( self, controlId ):
        if controlId == BUTTON_CANCEL:          
            self.onAction1(ACTION_PREVIOUS_MENU)
        else:
            self.onAction1(ACTION_SELECT_ITEM)   
       
    def onControl(self, control):
        pass
    
    def SetFile(self, dir, filename, type, heading=""):
        self.dir = dir
        self.filename = filename
        self.type = type
        self.label = heading
        
    def SetLabel(self, filename):
        control = self.getControl(BUTTON_PATH)
        control.setLabel(filename[-60:])
        