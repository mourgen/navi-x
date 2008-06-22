#############################################################################
#
# Navi-X Playlist browser
# v1.9.3 by rodejo (rodejo16@gmail.com)
#
# -v1.01  (2007/04/01) first release
# -v1.2   (2007/05/10)
# -v1.21  (2007/05/20)
# -v1.22  (2007/05/26)
# -v1.3   (2007/06/15)
# -v1.31  (2007/06/30)
# -v1.4   (2007/07/04)
# -v1.4.1 (2007/07/21)
# -v1.5   (2007/09/14)
# -v1.5.1 (2007/09/17)
# -v1.5.2 (2007/09/22)
# -v1.6   (2007/09/29)
# -v1.6.1 (2007/10/19)
# -v1.7 beta (2007/11/14)
# -v1.7   (2007/11/xx)
# -v1.7.1 (2007/12/15)
# -v1.7.2 (2007/12/20)
# -v1.8 (2007/12/31)
# -v1.9 (2008/02/10)
# -v1.9.1 (2008/02/10)
# -v1.9.2 (2008/02/23)
# -v1.9.3 (2008/03/xx)
#
# Changelog (v1.9.3)
#   - Added download resume support
#   - Added Apple movie trailer support.
#   - Added new media type called 'directory'. This type retrieves all PLX-files 
#     from a given local directory including sub-directories.
#   - Added parsing of RSS new feeds. Link to HTML file cannot be opened.
#   - Extended youtube search. Added sorting option.
#
# Changelog (v1.9.2)
#   - Improved caching of playlists and images to improve UI performance.
#
# Changelog (v1.9.1)
#   - Stage6 HTML parser fix.
#
# Changelog (v1.9)
#   - QuickSilverScreen support.
#   - Shoutcast support.
#   - some minor fixes
#
# Changelog (v1.8)
#   - Youtube download support.
#   - Added Stage6 html parser including stage6 search.
#   - Download queue: New menu items to move items up and down the queue.
#   - Download file: Check if file already exists, ask for overwrite.
#   - New menu item to rename favorite list item.
#
# Changelog (v1.7.2)
#   - Fixed Youtube HTML parser
#
# Changelog (v1.7)
#   - Favorites list supports all type of media, not only playlists.
#   - Added youtube support.
#   - Atrributes in PLX file have been extended:
#       1. Added 'player' attribute which allows selection of default player for
#          whole playlist or single mediaitem. See help.html
#       2. Added 'background' attribute for every playlist item which allows to
#          set the background image for a rss feed. see help.html
#
# Changelog (v1.6.1)
#   -Download destination file browser sometimes shows a empty name. This has been
#    changed. Local filename now based on playlist name field which is more clear.
#
# Changelog (v1.6)
#   -Added selection of player core (Mplayer or DVDplayer).
#   -Added download+sutdown option.
#   -Added download queue
#
# Changelog (v1.5.2)
#   -Reorganised main list. Increased number of item from 5 to 8
#   -Fixed html parser
# 
# Changelog (v1.5)
#   -Fixed http parsing. Some media did not download due to this.
#   -Add menu option to view the playlist source
#   -Code re-organisation to prepare for future changes
#   -Added flickr daily RSS parsing
#   -Added html parser
#
# Changelog (v1.4.1)
#   -Fixed http parsing. Some media did not play due to this.
#   -Improved white key handling to support DVD-kit remote control.
#
# Changelog (v1.4):
#   -Replaced URL button by browse button for more efficient browsing
#   -Improved parsing of URL's which allows to read stage6 podcasts and 
#    Comedy central podcasts
#   -Replaced buttons bitmaps. More common for different backgrounds
#
#############################################################################

from string import *
import sys, os.path
import urllib
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import Image, ImageFile
import shutil
import zipfile
import threading

sys.path.append(os.path.join(os.getcwd().replace(";",""),'src'))
from libs2 import *
from settings import *
from CPlayList import *
from CFileLoader import *
from CDownLoader import *
from CPlayer import *
from CDialogBrowse import *
from skin import *

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
myPlaylistsDir = RootDir + "My Playlists\\"
srcDir = RootDir + "\\src\\"

######################################################################
# Description: Main Window class
######################################################################
class MainWindow(xbmcgui.Window):
        def __init__(self):
            if Emulating: xbmcgui.Window.__init__(self)
            if not Emulating:
                self.setCoordinateResolution(PAL_4x3)

            self.delFiles(cacheDir) #clear the cache first

            #Create DIRs
            if not os.path.exists(cacheDir): 
                os.mkdir(cacheDir) 
            if not os.path.exists(myDownloadsDir): 
                os.mkdir(myDownloadsDir)

            #load the screen widget elements from another file.
            load_skin(self)

            #Create playlist object contains the parsed playlist data. The self.list control displays
            #the content of this list
            self.playlist = CPlayList()
            #Create favorite object contains the parsed favorite data. The self.favorites control displays
            #the content of this list
            self.favoritelist = CPlayList()
            #fill the playlist with favorite data
            result = self.favoritelist.load_plx(favorite_file)
            if result != 0:
                shutil.copyfile(initDir+favorite_file, RootDir+favorite_file)
                self.favoritelist.load_plx(favorite_file)

            self.downloadslist = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadslist.load_plx(downloads_complete)
            if result != 0:
                shutil.copyfile(initDir+downloads_complete, RootDir+downloads_complete)
                self.downloadslist.load_plx(downloads_complete)

            self.downloadqueue = CPlayList()
            #fill the playlist with downloads data
            result = self.downloadqueue.load_plx(downloads_queue)
            if result != 0:
                shutil.copyfile(initDir+downloads_queue, RootDir+downloads_queue)
                self.downloadqueue.load_plx(downloads_queue)
            
            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")

            #check if My Playlists exists, otherwise copy it from the init dir
            if not os.path.exists(myPlaylistsDir + "My Playlists.plx"): 
                shutil.copyfile(initDir+"My Playlists.plx", myPlaylistsDir+"My Playlists.plx")
            
            #check if My skin file exists, otherwise copy it from the init dir
            if not os.path.exists(srcDir + "skin.py"): 
                shutil.copyfile(initDir+"skin.py", srcDir+"skin.py")

            #Create the downloader object
            self.downloader = CDownLoader(self.downloadqueue, self.downloadslist)
            
            #Next a number of class private variables
            self.home=home_URL
            self.dwnlddir=myDownloadsDir
            self.History = [] #contains the browse history
            self.history_count = 0 #number of entries in history array
            self.background = 0 #background image
            self.userlogo = '' #user logo image at bottom left of screen
            self.userthumb = '' #user thumb image at bottom left of screen
            self.state_busy = 0 # key handling busy state
            self.state2_busy = 0 # logo update busy state
            self.URL='http://'
            self.type=''
            self.player_core=xbmc.PLAYER_CORE_AUTO #default
            self.pl_focus = self.playlist
            self.downlshutdown = False # shutdown after download flag
            self.mediaitem = 0
            self.searchstring = '' # default search string for (youtube) search
            self.logo_visible = False # true if logo shall be displayed
            self.thumb_visible = False # true if thumb shall be displayed
            
            self.loader = CFileLoader() #file loader
            
            #read the non volatile settings from the settings.dat file
            self.onReadSettings()
 
            #parse the home URL
            self.ParsePlaylist(URL=self.home)

        ######################################################################
        # Description: Handles key events.
        # Parameters : action=user action
        # Return     : -
        ######################################################################
        def onAction(self, action):
            self.state_action = 1
            
            if action == ACTION_PREVIOUS_MENU:
                self.onSaveSettings()
                self.delFiles(cacheDir) #clear the cache first
                self.close() #exit
                
            if self.state_busy == 0:
                if action == ACTION_SELECT_ITEM:
                    if self.getFocus() == self.list:
                        #main list
                        if self.URL == favorite_file:
                            self.onSelectFavorites()
                        elif self.URL == downloads_file or self.URL == downloads_queue or self.URL == downloads_complete:
                            self.onSelectDownloads()
                        else:
                            pos = self.list.getSelectedPosition()
                            self.SelectItem(self.playlist, pos)
                    #home button
                    elif self.getFocus() == self.button_home:
                        self.pl_focus = self.playlist
                        self.ParsePlaylist(URL=self.home)
                    #favorite button
                    elif self.getFocus() == self.button_favorites:
                        self.onOpenFavorites()
                    #downloads button
                    elif self.getFocus() == self.button_downloads:
                        self.onOpenDownloads()
                    #URL button
                    elif self.getFocus() == self.button_url:
                        self.onSelectURL()
                    elif self.getFocus() == self.button_about:
                        self.OpenTextFile('readme.txt')
                elif action == ACTION_PARENT_DIR:
                    if self.state_busy == 0:
                        if self.URL == favorite_file:            
                            self.onCloseFavorites()
                        elif self.URL == downloads_queue or self.URL == downloads_complete:    
                            self.onCloseDownloads()
                        else:
                            if self.history_count > 0:
                                previous = self.History[len(self.History)-1]
                                result = self.ParsePlaylist(mediaitem=previous.mediaitem, start_index=previous.index, proxy="ENABLED")
                                if result == 0:
                                    flush = self.History.pop()
                                    self.history_count = self.history_count - 1
#                elif action == ACTION_YBUTTON:
#                    self.onPlayUsing()
                elif self.ChkContextMenu(action) == True: #White
                    if self.URL == favorite_file:
                        self.selectBoxFavoriteList()
                    elif  self.URL == downloads_file or self.URL == downloads_queue or self.URL == downloads_complete:
                        self.selectBoxDownloadsList()
                    else:
                        self.selectBoxMainList()
                    
                pos = self.list.getSelectedPosition()
                self.listpos.setLabel(str(pos+1) + '/' + str(self.list.size()))
                
                self.UpdateThumb() #update thumb image
                
        ######################################################################
        # Description: Checks if one of the context menu keys is pressed.
        # Parameters : control=handle to UI control
        # Return     : True if valid context menu key is pressed.
        ######################################################################
        def ChkContextMenu(self, action):
            result = False
               
            #Support for different remote controls.
        
            if action == 261:
                result = True
            elif action == ACTION_CONTEXT_MENU:
                result = True
            elif action == ACTION_CONTEXT_MENU2:
                result = True
            
            return result

        ######################################################################
        # Description: Handles UI events.
        # Parameters : control=handle to UI control
        # Return     : -
        ######################################################################
        def onControl(self, control):
        
            #Nothing to do for now.
            if control == self.list:
                self.setFocus(self.list)
                    
        ######################################################################
        # Description: Displays the logo or media item thumb on left side of
        #              the screen.
        # Parameters : -
        # Return     : -
        ######################################################################
        def UpdateThumb(self):
            #if still busy updating the image then exit here. Avoid
            #recursive call of this function.
            if self.state2_busy != 0:
                return
        
            self.state2_busy = 1
            
            playlist = self.pl_focus
            index = self.list.getSelectedPosition()
            index2 = -1 #this value never will be reached
            thumb_update = False
            
            while index != index2:
                index = self.list.getSelectedPosition()
                m = self.pl_focus.list[index].thumb
                if m != self.userthumb:
                    if m == 'default': #no image
                        self.thumb_visible = False
                    elif m != 'previous': #URL to image located elsewhere
                        ext = getFileExtension(m)
                        self.loader.load(m, cacheDir + "thumb." + ext, 2)
                        if self.loader.state == 0: #success
                            #next line is fix, makes sure thumb is update.
                            self.thumb_visible = True
                            thumb_update = True
                        else:
                            self.thumb_visible = False
                    self.userthumb = m
             
                index2 = self.list.getSelectedPosition()

            if self.thumb_visible == True:
                self.user_logo.setVisible(0)
                if thumb_update == True:
                    self.user_thumb.setVisible(0)
                    self.user_thumb.setImage("")
                    self.user_thumb.setImage(self.loader.localfile)
                self.user_thumb.setVisible(1)
            else:
                self.user_thumb.setVisible(0)
                if self.logo_visible == True:
                    self.user_logo.setVisible(1)
                else:
                    self.user_logo.setVisible(0)
            
            self.state2_busy = 0
                    
        ######################################################################
        # Description: Parse playlist file. Playlist file can be a:
        #              -PLX file;
        #              -RSS v2.0 file (e.g. podcasts);
        #              -RSS daily Flick file (XML1.0);
        #              -html page having stage6 like format;
        #              -html Youtube file;
        # Parameters : URL (optional) =URL of the playlist file.
        #              mediaitem (optional)=Playlist mediaitem containing 
        #              playlist info. Replaces URL parameter.
        #              start_index (optional) = cursor position after loading 
        #              playlist.
        #              reload (optional)= indicates if the playlist shall be 
        #              reloaded or only displayed.
        # Return     : 0 on success, -1 if failed.
        ######################################################################
        def ParsePlaylist(self, URL='', mediaitem=CMediaItem(), start_index=0, reload=True, proxy="CACHING"):
            #avoid recursive call of this function by setting state to busy.
            self.state_busy = 1

            #The application contains three CPlayList objecs:
            #(1)main list, 
            #(2)favorites,
            #(3)download queue
            #(4)download completed list
            #Parameter 'self.pl_focus' points to the playlist in focus (1-4).
            playlist = self.pl_focus

            #The application contains one xbmcgui list control which displays 
            #the playlist in focus. 
            listcontrol = self.list

            listcontrol.setVisible(0)
            self.loading.setVisible(1)
            
            type = mediaitem.type
            if reload == True:
                #load the playlist
                if type == 'rss':
                    result = playlist.load_rss_20(URL, mediaitem, proxy)
                elif type == 'rss_flickr_daily':
                    result = playlist.load_rss_flickr_daily(URL, mediaitem, proxy)
                elif type == 'html_youtube':
                    result = playlist.load_html_youtube(URL, mediaitem, proxy)
                elif type == 'xml_shoutcast':
                    result = playlist.load_xml_shoutcast(URL, mediaitem, proxy)
                elif type == 'xml_applemovie':
                    result = playlist.load_xml_applemovie(URL, mediaitem, proxy)
                elif type == 'directory':
                    result = playlist.load_dir(URL, mediaitem, proxy)
                else: #assume playlist file
                    result = playlist.load_plx(URL, mediaitem, proxy)
                
                if result == -1: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "This playlist requires a newer Navi-X version")
                elif result == -2: #error
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "The requested file could not be opened or does not exist")
                
                if result != 0:
                    self.loading.setVisible(0)
                    listcontrol.setVisible(1)
                    self.setFocus(listcontrol)
                    self.state_busy = 0            
                    return -1
            
            #succesful
            playlist.save(RootDir + 'source.plx')                    
        
            self.URL = playlist.URL
            self.type = type
            if URL != '':
                mediaitem.URL = URL
            self.mediaitem = mediaitem
                        
            #display the new URL on top of the screen
            if len(playlist.title) > 0:
                title = playlist.title + ' - (' + playlist.URL + ')'
            else:
                title = playlist.URL
            self.urllbl.setLabel(title)

            #set the background image
            m = self.playlist.background
            if m != self.background:
                if m == 'default': #default BG image
                    self.bg.setImage(imageDir + "background.png")
                elif m != 'previous': #URL to image located elsewhere
                    ext = getFileExtension(m)
                    self.loader.load(m, cacheDir + "background." + ext, 8, proxy="ENABLED")
                    if self.loader.state == 0:
                        self.bg.setImage(self.loader.localfile)
                self.background = m
            
            #set the user logo image
            m = playlist.logo
            if m != self.userlogo:
                if m == 'none': #no image
                    self.logo_visible = False
                elif m != 'previous': #URL to image located elsewhere
                    ext = getFileExtension(m)
                    self.loader.load(m, cacheDir + "logo." + ext, 8, proxy="ENABLED")
                    if self.loader.state == 0: #success
                        #next line is fix, makes sure logo is update.
                        self.user_logo.setVisible(0)
                        self.user_logo.setImage("")
                        self.user_logo.setImage(self.loader.localfile)
                        self.logo_visible = True
                    else:
                        self.logo_visible = False                        
                self.userlogo = m
            
            #loading was successful
            listcontrol.reset() #clear the list control view
            
            #fill the main list
            i=0
            for m in playlist.list:
                if int(m.version) <= int(plxVersion):
                    thumb = self.getPlEntryThumb(m.type)
                    item = xbmcgui.ListItem(m.name,"" ,"", thumb)
                    listcontrol.addItem(item)                    
                    i=i+1
 
            listcontrol.selectItem(start_index)
            self.loading.setVisible(0)
            listcontrol.setVisible(1)
            self.setFocus(listcontrol)

            pos = self.list.getSelectedPosition()
            self.listpos.setLabel(str(pos+1) + '/' + str(self.list.size()))
           
            self.UpdateThumb() #update thumb image
           
            self.state_busy = 0
            
            return 0 #success

        ######################################################################
        # Description: Gets the playlist entry thumb image for different types
        # Parameters : type = playlist entry type
        # Return     : thumb image (local) file name
        ######################################################################
        def getPlEntryThumb(self, type):
            if type == 'rss_flickr_daily':
                return imageDir+'icon_rss.png'
            elif type == 'xml_applemovie':
                return imageDir+'icon_playlist.png'
            elif type == 'html_youtube':
                return imageDir+'icon_playlist.png'
            elif type == 'search_youtube':
                return imageDir+'icon_search.png'
            elif type == 'xml_shoutcast':
                return imageDir+'icon_playlist.png'
            elif type == 'search_shoutcast':
                return imageDir+'icon_search.png'
            elif type == 'directory':
                return imageDir+'icon_playlist.png'
                
            return imageDir+'icon_'+str(type)+'.png'
                
        ######################################################################
        # Description: Download file to local cache.
        # Parameters : URL=URL to source file
        #              localfile=path+name of local (destination) file
        # Return     : 0=succes, -1=failed
        ######################################################################
#        def downloadFile(self, URL, localfile):
#            try:
#                loc = urllib.URLopener()
#                loc.retrieve(URL, localfile)
#            except IOError:
#                return -1
#            return 0

        ######################################################################
        # Description: Handles the selection of an item in the list.
        # Parameters : playlist(optional)=the source playlist;
        #              pos(optional)=media item position in the playlist;
        #              append(optional)=true is playlist must be added to 
        #              history list;
        #              URL(optional)=link to media file;
        # Return     : -
        ######################################################################
        def SelectItem(self, playlist=0, pos=0, append=True, iURL=''):
            if iURL != '':
                mediaitem=CMediaItem()
                mediaitem.URL = iURL
                ext = getFileExtension(iURL)
                if ext == 'plx':
                    mediaitem.type = 'playlist'
                elif ext == 'xml':
                    mediaitem.type = 'rss'
                elif ext == 'jpg' or ext == 'png' or ext == 'gif':
                    mediaitem.type = 'image'
                elif ext == 'txt':
                    mediaitem.type == 'text'
                elif ext == 'zip':
                    mediaitem.type == 'script'
                else:
                    mediaitem.type = 'video' #same as audio
            else:
                if playlist.size() == 0:
                    #playlist is empty
                    return
               
                mediaitem = playlist.list[pos]
            
            self.state_busy = 1                
            
            type = mediaitem.type
            if type == 'playlist' or type == 'favorite' or type == 'rss' or \
               type == 'rss_flickr_daily' or type == 'directory' or \
               type == 'html_youtube' or type == 'xml_shoutcast' or \
               type == 'xml_applemovie':
                #add new URL to the history array
                tmp = CHistorytem() #new history item
                tmp.index = self.list.getSelectedPosition()
                tmp.mediaitem = self.mediaitem

                #exception case: Do not add Youtube pages to history list
                if self.mediaitem.type == 'html_youtube':
                    append = False
            
                self.pl_focus = self.playlist #switch back to main list
                result = self.ParsePlaylist(mediaitem=mediaitem)
                
                if result == 0 and append == True: #successful
                    self.History.append(tmp)
                    self.history_count = self.history_count + 1

            elif type == 'video' or type == 'audio':
#                self.onDownload()
#                self.state_busy = 0
#                return
                
                self.infotekst.setVisible(1)
                if mediaitem.player == 'mplayer':
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                elif mediaitem.player == 'dvdplayer':
                    MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                else:
                    MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                result = MyPlayer.play_URL(mediaitem.URL)
                self.infotekst.setVisible(0)
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not open file.")
            elif type == 'image':
                self.viewImage(playlist, pos, 0, mediaitem.URL) #single file show
            elif type == 'text':
                self.OpenTextFile(mediaitem.URL)
            elif type == 'script':
                self.InstallScript(mediaitem.URL)
            elif type == 'search_youtube' or type == 'search_shoutcast':
                self.PlaylistSearch(mediaitem, append)
            elif type == 'html':
                #at this moment we do nothing with HTML files
                pass
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Playlist format error", '"' + type + '"' + " is not a valid type.")
                
            self.state_busy = 0

        ######################################################################
        # Description: Player changed info can be catched here
        # Parameters : action=user key action
        # Return     : -
        ######################################################################
        def myPlayerChanged(self, state):
            #At this moment nothing to handle.
            pass


        def viewHTML(self, URL):
            pass

        ######################################################################
        # Description: Handles the player selection menu which allows the user
        #              to select the player core to use for playback.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onPlayUsing(self):
            possibleChoices = ["DVD Player", "MPlayer", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)
            pos = self.list.getSelectedPosition()
            URL = self.pl_focus.list[pos].URL
              
            result = 0
            if choice == 0:
                self.infotekst.setVisible(1) 
                MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=self.myPlayerChanged)
                result = MyPlayer.play_URL(URL) 
                self.infotekst.setVisible(0)  
            elif choice == 1:
                self.infotekst.setVisible(1)
                MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
                result = MyPlayer.play_URL(URL) 
                self.infotekst.setVisible(0)
                
            if result != 0:
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Could not open file.")
            
        ######################################################################
        # Description: Handles display of a text file.
        # Parameters : URL=URL to the text file.
        # Return     : -
        ######################################################################
        def OpenTextFile( self, URL):
            textwnd = CTextView()
            result = textwnd.OpenDocument(URL)
            if result == 0:
                textwnd.doModal()
                
        ######################################################################
        # Description: Handles image slideshow.
        # Parameters : playlist=the source playlist
        #              pos=media item position in the playlist
        #              mode=view mode (0=slideshow, 1=recursive slideshow)
        #              URL(optional) = URL to image
        # Return     : -
        ######################################################################
        def viewImage(self, playlist, pos, mode, iURL=''):
            self.infotekst.setVisible(1)
            #clear the imageview cache
            self.delFiles(imageCacheDir)

            if not os.path.exists(imageCacheDir): 
                os.mkdir(imageCacheDir) 

            if mode == 0: #single file show
                localfile= imageCacheDir + '0.'
                if iURL != '':
                    URL = iURL
                else:    
                    URL = playlist.list[pos].URL
                ext = getFileExtension(URL)

                if URL[:4] == 'http':
                    self.loader.load(URL, localfile + ext, proxy="DISABLED")
                    if self.loader.state == 0:
                        xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
                    else:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "Unable to open image.")
                else:
                    #local file
                    shutil.copyfile(URL, localfile + ext)
                    xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
            
            elif mode == 1: #recursive slideshow
                #in case of slideshow store default image
                count=0
                for i in range(self.list.size()):
                    if playlist.list[i].type == 'image':
                        localfile=imageCacheDir+'%d.'%(count)
                        URL = playlist.list[i].URL
                        ext = getFileExtension(URL)
                        shutil.copyfile(imageDir+'imageview.png', localfile + ext)
                        count = count + 1
                if count > 0:
                    count = 0
                    for i in range(self.list.size()):
                        if count == 2:
                            xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
                            self.state_action = 0
                        elif count > 2 and self.state_action == 1:
                            break
                            
                        if playlist.list[i].type == 'image':
                            localfile=imageCacheDir+'%d.'%(count)
                            URL = playlist.list[i].URL
                            ext = getFileExtension(URL)
                            self.loader.load(URL, localfile + ext, proxy="DISABLED")
                            if self.loader.state == 0:
                                count = count + 1

                    if self.list.size() < 3:
                        #start the slideshow after the first two files. load the remaining files
                        #in the background
                        xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
                if count == 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "No images in playlist.")
            
            self.infotekst.setVisible(0)
            
        ######################################################################
        # Description: Handles Installation of scripts
        # Parameters : URL=URL to the script ZIP file.
        # Return     : -
        ######################################################################
        def InstallScript(self, URL):            
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Message", "Install script?") == False:
                return

            #download the script ZIP file
            self.loader.load(URL, cacheDir + 'script.zip')
            if self.loader.state != 0:
                dialog.ok(" Script installer", "Script file could not be downloaded.")
                return
             
            filename = self.loader.localfile

            #todo display something on the screen while installing
                
            result = self.unzip_file_into_dir(filename, scriptDir)
            if result == 0:
                dialog.ok(" Script installer", "Installation successful.")
            else:
                dialog.ok(" Script installer", "Installation failed.")

        ######################################################################
        # Description: Handle selection of playlist search item (e.g. Youtube)
        # Parameters : item=CMediaItem
        #              append(optional)=true is playlist must be added to 
        #              history list;
        # Return     : -
        ######################################################################
        def PlaylistSearch(self, item, append):
            #youtube search
            if item.type == 'search_youtube':
                keyboard = xbmc.Keyboard(self.searchstring, 'Youtube Search')
                keyboard.doModal()
                
                if (keyboard.isConfirmed() == True):
                    self.searchstring = keyboard.getText()
                    
                    fn = self.searchstring.replace(' ','+')
                    URL = 'http://www.youtube.com/results?search_query='
                    URL = URL + fn
                    
                    #ask the end user how to sort
                    possibleChoices = ["Relevance", "Date Added", "View Count", "Rating"]
                    dialog = xbmcgui.Dialog()
                    choice = dialog.select("Sort by", possibleChoices)

                    #validate the selected item
                    if choice == 1: #Date Added
                        URL = URL + '&search_sort=video_date_uploaded'
                    elif choice == 2: #View Count
                        URL = URL + '&search_sort=video_view_count'
                    elif choice == 3: #Rating
                        URL = URL + '&search_sort=video_avg_rating'
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'html_youtube'
                    mediaitem.name = 'search results: ' + self.searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()
                    tmp.index = self.list.getSelectedPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1
            elif item.type == 'search_shoutcast':
                keyboard = xbmc.Keyboard(self.searchstring, 'Shoutcast Search: Station, Genre')
                keyboard.doModal()
                
                if (keyboard.isConfirmed() == True):
                    self.searchstring = keyboard.getText()
                    
                    fn=self.searchstring
#                    fn = self.searchstring.replace(' ','&plus;')
                    URL = 'http://www.shoutcast.com/sbin/newxml.phtml?search='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'xml_shoutcast'
                    mediaitem.name = 'search results: ' + self.searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()
                    tmp.index = self.list.getSelectedPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1
            elif item.type == 'search_flickr':
                keyboard = xbmc.Keyboard(self.searchstring, 'Flickr Search')
                keyboard.doModal()
                
                if (keyboard.isConfirmed() == True):
                    self.searchstring = keyboard.getText()

                    fn = self.searchstring.replace(' ','+')
                    URL = 'http://www.flickr.com/search/?q='
                    URL = URL + fn
        
                    mediaitem=CMediaItem()
                    mediaitem.URL = URL
                    mediaitem.type = 'html_flickr'
                    mediaitem.name = 'search results: ' + self.searchstring
                    mediaitem.player = item.player

                    #create history item
                    tmp = CHistorytem()
                    tmp.index = self.list.getSelectedPosition()
                    tmp.mediaitem = self.mediaitem

                    self.pl_focus = self.playlist
                    result = self.ParsePlaylist(mediaitem=mediaitem)
                
                    if result == 0 and append == True: #successful
                        self.History.append(tmp)
                        self.history_count = self.history_count + 1

        ######################################################################
        # Description: Handles selection of 'Browse' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectURL(self):
            browsewnd = CDialogBrowse()
            browsewnd.SetFile('', self.URL, 1)
            browsewnd.doModal()
            
            if browsewnd.state != 0:
                return
        
            self.pl_focus = self.playlist
        
            self.URL = browsewnd.dir + browsewnd.filename
            
            self.SelectItem(iURL=self.URL)
            
            
        ######################################################################
        # Description: Handles selection of 'Favorite' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenFavorites(self):
            #Select the favorite playlist.
            self.pl_focus = self.favoritelist
              
            #Show the downloads list
            self.ParsePlaylist(reload=False) #display favorite list

        ######################################################################
        # Description: Handles selection within favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectFavorites(self):
            if self.favoritelist.size() == 0:
                #playlist is empty
                return
            
            pos = self.list.getSelectedPosition()
            self.SelectItem(self.favoritelist, pos, append=False)

        ######################################################################
        # Description: Handles closing of the favorite list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseFavorites(self):
            #Select the main playlist.
            self.pl_focus = self.playlist
        
#            self.favoritelist.save(RootDir + favorite_file)
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within favorite list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxFavoriteList(self):
            possibleChoices = ["Play Using...", "Remove Item", "Rename", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)

            if self.favoritelist.size() == 0:
                #playlist is empty
                return
            
            #validate the selected item
            if choice == 0: #Play using
                self.onPlayUsing()
            elif choice == 1: #Remove Item
                pos = self.list.getSelectedPosition()
                self.favoritelist.remove(pos)
                self.favoritelist.save(RootDir + favorite_file)
                self.ParsePlaylist(reload=False) #display favorite list
            elif choice == 2: #Rename
                pos = self.list.getSelectedPosition()
                item = self.favoritelist.list[pos]
                keyboard = xbmc.Keyboard(item.name, 'Rename')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    item.name = keyboard.getText()
                    self.favoritelist.save(RootDir + favorite_file)
                    self.ParsePlaylist(reload=False) #display favorite list
            
        ######################################################################
        # Description: Handles selection of the 'downloads' button.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onOpenDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            self.SelectItem(iURL=downloads_file)
         
        ######################################################################
        # Description: Handles selection within download list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSelectDownloads(self):
            if self.URL == downloads_file:
                pos = self.list.getSelectedPosition()
                if pos == 0:
                    #Select the DL queue playlist.
                    self.pl_focus = self.downloadqueue
                    #fill and show the download queue
                    self.ParsePlaylist(reload=False) #display download list
                else:
                    #Select the download list playlist.
                    self.pl_focus = self.downloadslist
                    #fill and show the downloads list
                    self.ParsePlaylist(reload=False) #display download list
            elif self.URL == downloads_queue: #download queue
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return
            
                pos = self.list.getSelectedPosition()
            
                self.SelectItem(self.downloadqueue, pos, append=False)
            else: #download completed
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return
            
                pos = self.list.getSelectedPosition()
            
                self.SelectItem(self.downloadslist, pos, append=False)
            
        ######################################################################
        # Description: Handles closing of the downloads list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onCloseDownloads(self):
            #select main playlist
            self.pl_focus = self.playlist
            
            self.ParsePlaylist(reload=False) #display main list

        ######################################################################
        # Description: Handles context menu within download list
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxDownloadsList(self):
            if self.URL == downloads_file:
                return #no menu
            elif self.URL == downloads_queue:
                possibleChoices = ["Download Queue", "Download Queue + Shutdown", "Move Item Up", "Move Item Down", "Remove Item", "Clear List", "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if self.downloadqueue.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0 or choice == 1: #Download Queue / Shutdown
                    self.downlshutdown = False #Reset flag
                    if choice == 1: #Download Queue + Shutdown
                        self.downlshutdown = True #Set flag
                    
                    #Download all files in the queue 
                    self.downloader.download_queue(self.downlshutdown)
                    
                    #Download completed. Now check the next step
                    if self.downloader.state != -2 and self.downlshutdown == True:
                        #No cancel button and shutdown requested
                        xbmc.shutdown() #shutdown the X-box
                    elif self.downloader.state == 0:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Downloading", "Download complete.")
                    elif self.downloader.state == -1:
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Error", "Download failed.")                    
                    
                    #Display the updated Queue playlist
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 2: #Move Item Up
                    pos = self.list.getSelectedPosition()
                    if pos > 0:
                        item = self.downloadqueue.list[pos-1]
                        self.downloadqueue.list[pos-1] = self.downloadqueue.list[pos]
                        self.downloadqueue.list[pos] = item
                        self.downloadqueue.save(RootDir + downloads_queue)
                        self.ParsePlaylist(reload=False) #display download list
                elif choice == 3: #Move Item Down
                    pos = self.list.getSelectedPosition()
                    if pos < (self.list.size())-1:
                        item = self.downloadqueue.list[pos+1]
                        self.downloadqueue.list[pos+1] = self.downloadqueue.list[pos]
                        self.downloadqueue.list[pos] = item
                        self.downloadqueue.save(RootDir + downloads_queue)
                        self.ParsePlaylist(reload=False) #display download list
                elif choice == 4: #Remove
                    pos = self.list.getSelectedPosition()
                    self.downloadqueue.remove(pos)
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 5: #Clear List
                    self.downloadqueue.clear()
                    self.downloadqueue.save(RootDir + downloads_queue)
                    self.ParsePlaylist(reload=False) #display download list
            else: #download completed
                possibleChoices = ["Play Using...", "Remove Item", "Clear List", "Delete Item", "Cancel"]
                dialog = xbmcgui.Dialog()
                choice = dialog.select("Select", possibleChoices)
            
                if self.downloadslist.size() == 0:
                    #playlist is empty
                    return
            
                #validate the selected item
                if choice == 0: #Play using
                    self.onPlayUsing()
                elif choice == 1: #Remove
                    pos = self.list.getSelectedPosition()
                    self.downloadslist.remove(pos)
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 2: #Clear List
                    self.downloadslist.clear()
                    self.downloadslist.save(RootDir + downloads_complete)
                    self.ParsePlaylist(reload=False) #display download list
                elif choice == 3: #Delete
                    pos = self.list.getSelectedPosition()            
                    URL = self.downloadslist.list[pos].URL
                    dialog = xbmcgui.Dialog()                 
                    if dialog.yesno("Message", "Delete file from disk?") == True:
                        if os.path.exists(URL): 
                            os.remove(URL)
                        selfs.downloadslist.remove(pos)
                        self.downloadslist.save(RootDir + downloads_complete)
                        self.ParsePlaylist(reload=False) #display download list

        ######################################################################
        # Description: Handle download context menu in main list.
        # Parameters : -
        # Return     : -
        ######################################################################
        def onDownload(self):
            self.state_busy = 1 #busy
            
            possibleChoices = ["Add To Download Queue", "Download", "Download + Shutdown", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)
                       
            if choice < 3:
                self.downlshutdown = False #Reset flag
                if choice == 2:
                    self.downlshutdown = True #Set flag
                    
                pos = self.list.getSelectedPosition()
                entry = self.playlist.list[pos]
                #select destination location for the file.
                self.downloader.browse(entry, self.dwnlddir)

                if self.downloader.state == 0:
                    #update download dir setting
                    self.dwnlddir = self.downloader.dir
                    
                    #Get playlist entry
                    #Set the download location field.
                    entry.DLloc = self.downloader.localfile
                
                    if choice == 1 or choice == 2:
                        #foreground download
                        self.downloader.download_file(entry, self.downlshutdown)
                    
                        if self.downloader.state != -2 and self.downlshutdown == True:
                            xbmc.shutdown() #shutdown the X-box
                        elif self.downloader.state == 0:
                            dialog = xbmcgui.Dialog()
                            dialog.ok("Downloading", "Download complete.")
                        elif self.downloader.state == -1:
                            dialog = xbmcgui.Dialog()
                            dialog.ok("Error", "Download failed.")                    
                    else: #add to queue
                        #download later
                        self.downloader.add_queue(entry)
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Result", "File was successfully added to the Queue.")

                elif self.downloader.state == -1:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not locate file.")
                    
            self.state_busy = 0 #not busy            

    
        ######################################################################
        # Description: Handles selection of the 'black' button in the main list.
        #              This will open a selection window.
        # Parameters : -
        # Return     : -
        ######################################################################
        def selectBoxMainList(self):
            possibleChoices = ["Download...", "Play Using...", "Play + Auto Next", "Image Slideshow", \
            "Add Selected Item to Favorites", "Add Playlist to Favorites", "Set Playlist as Home", \
            "View Playlist Source", "Cancel"]
            dialog = xbmcgui.Dialog()
            choice = dialog.select("Select", possibleChoices)
            
            if choice == 0: #Download
                self.onDownload()
            elif choice == 1: #play using
                self.onPlayUsing()
            elif choice == 2: #Play auto next
                pos = self.list.getSelectedPosition()
                size = self.playlist.size()
                self.infotekst.setVisible(1)
                MyPlayer = CPlayer(self.player_core, function=self.myPlayerChanged)                
                result=MyPlayer.play(self.playlist, pos, size-1)
                self.infotekst.setVisible(0)
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "No video or audio in playlist.")
            elif choice == 3: #Slideshow
                self.viewImage(self.playlist, 0, 1) #slide show show
            elif choice == 4: #Add selected file to Favorites
                pos = self.list.getSelectedPosition()
                tmp = CMediaItem() #create new item
                tmp.type = self.playlist.list[pos].type
                keyboard = xbmc.Keyboard(self.playlist.list[pos].name, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.list[pos].name
                tmp.thumb = self.playlist.list[pos].thumb
                tmp.URL = self.playlist.list[pos].URL
                tmp.player = self.playlist.list[pos].player
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 5: #Add playlist to Favorites
                tmp = CMediaItem() #create new item
                tmp.type = self.mediaitem.type
                keyboard = xbmc.Keyboard(self.playlist.title, 'Add to Favorites')
                keyboard.doModal()
                if (keyboard.isConfirmed() == True):
                    tmp.name = keyboard.getText()
                else:
                    tmp.name = self.playlist.title
                tmp.URL = self.URL
                tmp.player = self.mediaitem.player
                self.favoritelist.add(tmp)
                self.favoritelist.save(RootDir + favorite_file)
            elif choice == 6: #Set Playlist as Home
                self.home = self.URL
 #               self.onSaveSettings()
            elif choice == 7: #View playlist properties
                self.OpenTextFile(RootDir + "source.plx")
                
        ######################################################################
        # Description: Read the home URL from disk. Called at program init. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onReadSettings(self):
            try:
                f=open(RootDir + 'settings.dat', 'r')
                data = f.read()
                data = data.split('\n')
                home=data[0]
                if home != home_URL_old:
                    self.home=home
                self.dwnlddir=data[1]
                f.close()
            except IOError:
                return

        ######################################################################
        # Description: Saves the home URL to disk. Called at program exit. 
        # Parameters : -
        # Return     : -
        ######################################################################
        def onSaveSettings(self):
            f=open(RootDir + 'settings.dat', 'w')
            f.write(self.home + '\n')
            f.write(self.dwnlddir + '\n')
            f.close()
            
        ######################################################################
        # Description: Deletes all files in a given folder and sub-folders.
        #              Note that the sub-folders itself are not deleted.
        # Parameters : folder=path to local folder
        # Return     : -
        ######################################################################
        def delFiles(self, folder):
            try:        
                for root, dirs, files in os.walk(folder , topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
            except IOError:
                return
                    
        ######################################################################
        # Description: Unzip a file into a dir
        # Parameters : zip filename and destination directory
        # Return     : -
        ######################################################################                    
        def unzip_file_into_dir(self, file, dir):
            chk_confirmation = False
            
            if os.path.exists(dir) == False:
                return -1
            
            zfobj = zipfile.ZipFile(file)
            
            for name in zfobj.namelist():
                if name.endswith('/'):
                    if os.path.exists(dir+name):
                        #directory exists
                        if chk_confirmation == False:
                            dialog = xbmcgui.Dialog()
                            if dialog.yesno("Message", "Directory " + name + " already exists, continue?") == False:
                                return -1
                            chk_confirmation = True
                    else: 
                        #create the directory
                        os.mkdir(os.path.join(dir, name))
                else:
                    outfile = open(os.path.join(dir, name), 'wb')
                    outfile.write(zfobj.read(name))
                    outfile.close()
                    
            return 0 #succesful


win = MainWindow()
win.doModal()
del win
