#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CServer:
# Handles all services with the Navi-Xtreme server.
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
from CFileLoader import *
from libs2 import *
from CDialogLogin import *
from CDialogRating import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

######################################################################
# Description: Text viewer
######################################################################
class CServer: 
    def __init__(self):
        
        #public member of CServer class.
        self.user_id = ''
        
        #read the stored user ID
        self.read_user_id()

    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ######################################################################            
    def login(self):
        login = CDialogLogin("CLoginskin.xml", os.getcwd())
        login.doModal()
        if login.state != 0:
            return -2
                   
        #login to the Navi-X server
        self.user_id = self.nxLogin(login.username, login.password)
        if self.user_id == '':
            #failed
            return -1

#@todo: show dialog again using existing user name and password.

        print "Login to the NXServer was successful"

        #save the returned user ID
        self.save_user_id()             
        #success   
        return 0          

    ######################################################################
    # Description: Login function for Navi-Xtreme login.
    # Parameters : username: user name
    #              password: user password
    # Return     : blowfish-encrypted string identifying the user for 
    #              saving locally, or an empty string if the login failed.
    ######################################################################  
    def nxLogin(self, username, password):
        return getRemote('http://navix.turner3d.net/login/',{
            'method':'post',
            'postdata':urllib.urlencode({'username':username,'password':password})
        })

    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ######################################################################                     
    def logout(self):
        #empty the user ID
        self.user_id=''
        self.save_user_id()

    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ######################################################################             
    def is_user_logged_in(self):
        if self.user_id != '':
            return True  
        return False

    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ######################################################################            
    def rate_item(self, mediaitem):    
        rate = CDialogRating("CRatingskin.xml", os.getcwd())
        rate.doModal()
        if rate.state != 0:
            return -2
                
        if self.is_user_logged_in() == False:
            dialog = xbmcgui.Dialog()
            dialog.ok(" Error", "You are not logged in.")
            return -1

        #login to the Navi-X server
        result = self.nxrate_item(mediaitem, rate.rating)

    ######################################################################
    # Description: -
    # Parameters : mediaitem: CMediaItem instance to rate
    #              rating = value [0-5]
    # Return     : -
    # API Return : Success: value [0-5] representing the new average rating
    #              Failure: error message string
    ######################################################################      
    def nxrate_item(self, mediaitem, rating):  
        #print "Rating: " + str(rating) + " " + mediaitem.URL
        #return 0
                   
        #rate mediaitem
        result=getRemote('http://navix.turner3d.net/rate/',{
            'method':'post',
            'postdata':urllib.urlencode({'url':mediaitem.URL,'rating':rating}),
            'cookie':'nxid='+nxserver.user_id
        })

        dialog = xbmcgui.Dialog()                            
        p=re.compile('^\d$')
        match=p.search(result)
        if match:
            dialog.ok(" Rate", "Rating Successful.")
            mediaitem.rating=result
        else:
            dialog.ok(" Rate", result)

        return 0
    
    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ######################################################################     
    def read_user_id(self):
        try:
            f=open(RootDir + 'user_id.dat', 'r')
            self.user_id = f.read()
            f.close()
        except IOError:
            return   

    ######################################################################
    # Description: -
    # Parameters : -
    # Return     : -
    ###################################################################### 
    def save_user_id(self):
        f=open(RootDir + 'user_id.dat', 'w')
        f.write(self.user_id)    
        f.close()
        pass
 

#Create server instance here and use it as a global variable for all other components that import server.py.
global nxserver
nxserver = CServer() 

global re_server
re_server = re.compile('^[^:]+://(?:www\.)?([^/]+)')