#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CInstaller:
# Intaller for scripts and plugins.
#############################################################################

import mc
from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
#import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from settings import *
from CFileLoader import *
from CURLLoader import *
from libs2 import *

######################################################################
# Description: Handles installation of Boxee apps
######################################################################
class CInstaller:

    ######################################################################
    # Description: Handles Installation of a scripts ZIP file.
    # Parameters : URL = URL of the file
    #              mediaitem=CMediaItem object to load
    # Return     : -
    ######################################################################
    def InstallNaviX(self, URL='', mediaitem=CMediaItem()):
        if URL != '':
            self.URL = URL
        else:
            self.URL = mediaitem.URL
        
        urlopener = CURLLoader()
        result = urlopener.urlopen(self.URL, mediaitem)
        if result["code"] == 0:
            self.URL = urlopener.loc_url
        
#        SetInfoText("Downloading... ")
        
        #download the file.
        loader = CFileLoader2()
        loader.load(self.URL, tempCacheDir + 'script.zip')
        if loader.state != 0:
            return -2
        filename = loader.localfile

#        SetInfoText("Installing... ")

        #determine the install dir based on the current Navi-X directory (root)
        if RootDir[0] == '/':
            pos =   RootDir.rfind("/",0,-1)
        else:
            pos =   RootDir.rfind("\\",0,-1)
            
        if pos != -1:
            InstallDir = RootDir[0:pos+1]

            result = self.unzip_file_into_dir(filename, InstallDir)
            
            if result == 0: #remove pyo files (needed for XBMC Boxee)
                self.delPYOFiles(RootDir+'src')
            
        else:
            result = -1
        
        return result

    ######################################################################
    # Description: Unzip a file into a dir
    # Parameters : file = the zip file
    #              dir = destination directory
    # Return     : -
    ######################################################################                    
    def unzip_file_into_dir(self, file, dir):
        chk_confirmation = False

        if os.path.exists(dir) == False:
            try:
                os.makedirs(dir) #create the directory
            except IOError:
                return -1 #failure
            
        zfobj = zipfile.ZipFile(file)

        for name in zfobj.namelist():
            index = name.rfind('/')
            if index != -1:
                #entry contains path
                if os.path.exists(dir+name[:index+1]):
                    #directory exists
                    if chk_confirmation == False:
                        response = mc.ShowDialogConfirm("Installer", "Directory already exists, continue?", "No", "Yes")
                        if response == False:                    
                            return -1
                else:
                    #directory does not exist. Create it.
                    try:
                        #create the directory structure
                        os.makedirs(os.path.join(dir, name[:index+1]))
                    except IOError:
                        return -1 #failure
                    
            if not name.endswith('/'):
                #entry contains a filename
                try:
                    outfile = open(os.path.join(dir, name), 'wb')
                    outfile.write(zfobj.read(name))
                    outfile.close()
                except IOError:
                    pass #There was a problem. Continue...
                 
            chk_confirmation = True
        return 0 #succesful

    ######################################################################
    # Description: Deletes all pyo files in a given folder and sub-folders.
    #              Note that the sub-folders itself are not deleted.
    # Parameters : folder=path to local folder
    # Return     : -
    ######################################################################
    def delPYOFiles(self, folder):
        try:        
            for root, dirs, files in os.walk(folder , topdown=False):
                for name in files:
                    filename = os.path.join(root, name)
                    if filename[-4:] == ".pyo":
                        os.remove(filename)
        except IOError:
            return
            
            
            