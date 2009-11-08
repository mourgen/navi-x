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

######################################################################
# Description: Browse dialog class
######################################################################
class CDialogBrowse(xbmcgui.WindowDialog):
    def __init__(self, parent=None):
        if Emulating: xbmcgui.WindowDialog.__init__(self)
        
        self.filename=''
        self.dir=''
      
        width=parent.getWidth()
      
        #background image
        self.bg = xbmcgui.ControlImage(100,200,width-200,160, imageDir + "dialog-panel.png")
        self.addControl(self.bg)

        self.title = xbmcgui.ControlLabel(130,210,155,40, 'Download location', "font14")
        self.addControl(self.title)

        self.button_dest = xbmcgui.ControlButton(130,240,width-245,32, '' , RootDir + "images\\button-focus.png", RootDir + "images\\button-nofocus.png")
        self.addControl(self.button_dest)

        self.button_browse = xbmcgui.ControlButton(130,290,145,32,'Browse', RootDir + "images\\button-focus.png", RootDir + "images\\button-nofocus.png")
        self.addControl(self.button_browse)
          
        self.button_ok = xbmcgui.ControlButton(300,290,140,32,'OK', RootDir + "images\\button-focus.png", RootDir + "images\\button-nofocus.png")
        self.addControl(self.button_ok)
        
        self.button_cancel = xbmcgui.ControlButton(475,290,140,32,'Cancel', RootDir + "images\\button-focus.png", RootDir + "images\\button-nofocus.png")
        self.addControl(self.button_cancel)
        
        #button key behaviour
        self.button_ok.controlUp(self.button_dest)       
        self.button_ok.controlRight(self.button_cancel) 
        self.button_ok.controlLeft(self.button_browse) 
        self.button_dest.controlDown(self.button_ok)       
        self.button_browse.controlRight(self.button_ok)
        self.button_browse.controlUp(self.button_dest)
        self.button_cancel.controlLeft(self.button_ok)
        self.button_cancel.controlUp(self.button_dest)       
        
        self.setFocus(self.button_ok)
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_PARENT_DIR:
            self.state = -1 #success
            self.close() #exit
                       
        if action == ACTION_SELECT_ITEM:
            if self.getFocus() == self.button_ok:
                if os.path.exists(self.dir) == False:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Destination directory does not exist")
                else:
                    self.state = 0 #success
                    self.close() #exit
            if self.getFocus() == self.button_cancel:
                self.state = -1 #success
                self.close() #exit
            if self.getFocus() == self.button_dest:
                keyboard = xbmc.Keyboard(self.dir + self.filename)
                keyboard.doModal()
                
                if (keyboard.isConfirmed() == True):
                    fn = keyboard.getText()
                    pos = fn.rfind('\\') #find last '\' in the string
                    if pos != -1:
                        self.dir = fn[:pos+1]
                        filename = fn[pos+1:]
                        if len(filename) > 42:
                            dialog = xbmcgui.Dialog()
                            dialog.ok("Error", "Filename exceeds 42 characters.")
                        else:
                            self.filename = filename
                            
                    self.SetLabel(self.dir + self.filename)

            if self.getFocus() == self.button_browse:              
                dialog = xbmcgui.Dialog()
                fn = dialog.browse(self.type,'Xbox Media Center', 'files', '', False, False)
                if fn:
                    if self.type == 3:
                        if fn[-1] != '\\':
                            fn = fn + '\\'
                            
                        self.dir = fn
                    else:
                        pos = fn.rfind('\\') #find last '\' in the string
                        if pos != -1:
                            self.dir = fn[:pos+1]
                            filename = fn[pos+1:]
                            self.filename = filename
                    
                    self.SetLabel(self.dir + self.filename)
       
    def onControl(self, control):
        self.setFocus(control)
    
    def SetFile(self, dir, filename, type):
        self.dir = dir
        self.filename = filename
        self.SetLabel(dir + filename)
        self.type = type

        if self.type == 3:
            label = 'Browse Folder'
        else:
            label = 'Browse File'
        self.title.setLabel(label)
        
    def SetLabel(self, filename):
        self.button_dest.setLabel(filename[-60:])
        