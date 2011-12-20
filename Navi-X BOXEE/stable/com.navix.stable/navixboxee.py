#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# navixboxee:
# Main Boxee file.
#############################################################################

import mc
from string import *
import sys, os.path
import urllib
import re, random, string
import re, os, time, datetime, traceback
import shutil
import zipfile
import copy
import random

from libs2 import *
from CURLLoader import *
from CPlayList import *
from CPlayer import *
from CInstaller import *
from settings import *
from CServer import *
from navixboxee import *

def Init(firsttime=False):
    list = mc.GetWindow(14000).GetList(122)
    listcontrol = list.GetItems()
    del listcontrol[:]
    
    item = mc.ListItem()
    item.SetLabel("Home")
    listcontrol.append(item)

    item = mc.ListItem()
    item.SetLabel("Favorites")
    listcontrol.append(item)
    
    if firsttime == True:
        mc.GetApp().GetLocalConfig().SetValue("listview", "default")
        
#    if firsttime == True:
#        if nxserver.is_user_logged_in() == True:
#            versionlabel = mc.GetWindow(14000).GetLabel(107)
#            versionlabel.SetLabel('version: '+ Version + '.' + SubVersion + " (signed in)")        
    item = mc.ListItem()
    ListView = mc.GetApp().GetLocalConfig().GetValue("listview")
    if ListView == "default":
        item.SetLabel("View: Default")
    if ListView == "thumbnails":
        item.SetLabel("View: Thumbnails")
    elif ListView == "list":   
        item.SetLabel("View: List")
    else:
        mc.GetApp().GetLocalConfig().SetValue("listview", "default")
        item.SetLabel("View: Default")
        #item.SetLabel("View: Thumbnails")
    listcontrol.append(item)    
    
    item = mc.ListItem()    
    if nxserver.is_user_logged_in() == True:
        item.SetLabel("Sign Out Navi-Xtreme")
    else:
        item.SetLabel("Sign In Navi-Xtreme")
    listcontrol.append(item)
            
    item = mc.ListItem()
    item.SetLabel("Exit")
    listcontrol.append(item)
    list.SetItems(listcontrol)
    
    #right popup menu
    list = mc.GetWindow(14000).GetList(127)
    listcontrol = list.GetItems()
    del listcontrol[:]
    
    item = mc.ListItem()
    item.SetLabel("Add to Favorites")
    listcontrol.append(item)
    item = mc.ListItem()
    item.SetLabel("Remove from Favorites")
    listcontrol.append(item)
    item = mc.ListItem()
    item.SetLabel("About Navi-X")
    listcontrol.append(item)    
    list.SetItems(listcontrol)
    
    userkey = mc.GetApp().GetLocalConfig().GetValue("userkey")
    if userkey == "":
        userkey = str(random.randint(1, 1000))
        userkey = userkey + str(random.randint(1, 1000))
        userkey = userkey + str(random.randint(1, 1000))
        mc.GetApp().GetLocalConfig().SetValue("userkey", userkey)
            
######################################################################
# Description: Parse playlist file. Playlist file can be a:
#              -PLX file; Based on ParsePlaylist in navix.py
# Parameters : URL (optional) =URL of the playlist file.
#              mediaitem (optional)=Playlist mediaitem containing 
#              playlist info. Replaces URL parameter.
# Return     : 0 if success
######################################################################
def ParsePlaylist(URL='', mediaitem=CMediaItem(), reload=True, view=''):
    if reload == False:
        listcontrol = mc.GetWindow(14000).GetList(GetListView()).GetItems()
        stackitem = mc.GetWindow(14000).GetList(555).GetItem(0)
        view = stackitem.GetProperty("view")
        SetListView(view)
        mc.GetWindow(14000).GetList(GetListView()).SetFocus()
        mc.GetWindow(14000).GetList(GetListView()).SetItems(listcontrol)
        
        #pos = stackitem.GetProperty("focusseditem")
        #mc.GetWindow(14000).GetList(GetListView()).SetFocusedItem(pos) 
        return

    if URL != '':
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'playlist'

    mc.ShowDialogWait()
    playlist = CPlayList()
                        
    type = mediaitem.GetType()
    ##mc.ShowDialogOk("Debug", "Parse mediaitem of type " + type)
    
    listcontrol = mc.GetWindow(14000).GetList(GetListView()).GetItems()
    del listcontrol[:]
    
    #load the playlist
    if type == 'rss_flickr_daily':
        result = playlist.load_rss_flickr_daily(URL, mediaitem)                
    elif type[0:3] == 'rss':
        result = playlist.load_rss_20(URL, mediaitem)
    elif type[0:4] == 'atom':
        result = playlist.load_atom_10(URL, mediaitem)
    elif type == 'opml':
        result = playlist.load_opml_10(URL, mediaitem)
    elif type == 'html_youtube':
        result = playlist.load_html_youtube(URL, mediaitem)
    elif type == 'xml_shoutcast':
        result = playlist.load_xml_shoutcast(URL, mediaitem)
    elif type == 'xml_applemovie':
        result = playlist.load_xml_applemovie(URL, mediaitem)
    elif type == 'directory':
        result = playlist.load_dir(URL, mediaitem)
    else: #assume playlist file
        result = playlist.load_plx(URL, mediaitem)
    
###    playlist.save(RootDir + 'source.plx')

    if result == -1: #error
        mc.ShowDialogOk("Error", "This playlist requires a newer Navi-X version")
    elif result == -2: #error
        mc.ShowDialogOk("Error", "Cannot open file.")
                
    if result != 0: #failure
        return -1
    
    #display the new URL on top of the screen
    if len(playlist.title) > 0:
        title = playlist.title # + ' - (' + playlist.URL + ')'
    else:
        title = playlist.URL

    #remove the [COLOR] tags from the title as Boxee doesn't seem to support them
    #todo: this still strips out >> and following from labels but it's better than nothing
    reg1 = "(\[.*?\])"
    title = re.sub(reg1, '', title)

    stackitem = mc.ListItem()
    stackitem.SetProperty("URL", mediaitem.URL)
    stackitem.SetProperty("listtitle", title)
    stackitem.SetProperty("view", playlist.view)
    #stackitem.SetProperty("focusseditem", mc.GetWindow(14000).GetList(GetListView()).GetFocusedItem())
    
    #set the background image
    m = playlist.background
    if (m == 'default') or (m == 'previous'): #default BG image
        stackitem.SetProperty("bgimage",imageDir + background_image1)
    else:
        stackitem.SetProperty("bgimage",playlist.background)
    
    stacklist = mc.ListItems()
    stacklist.append(stackitem)
    mc.GetWindow(14000).GetList(555).SetItems(stacklist)

    today=datetime.date.today()
    ## CPlayList -> mc.ListItems
    for i in range(0, playlist.size()):
        m = playlist.list[i]
        if int(m.version) <= int(plxVersion):

            icon, thumb = getPlEntryThumb(m, playlist)
            
            # set label2      
            label2=''
            if m.date != '':
                l=m.date.split('-')
                entry_date = datetime.date(int(l[0]), int(l[1]), int(l[2]))
                days_past = (today-entry_date).days
                if days_past <= 10:
                    if days_past <= 0:
                        label2 = 'NEW today'
                    elif days_past == 1:
                        label2 = 'NEW yesterday'
                    else:
                        label2 = 'NEW ('+ str(days_past) + ' days ago)'
                    
            if m.description != '':
                label2 = label2 + ' >'

            item = mc.ListItem()          
            item.SetLabel(m.name)
            if m.URL != "":
                item.SetPath(m.URL + " : " + m.processor )
            item.SetProperty('label2', label2)
            item.SetProperty('description', m.description)
            item.SetProperty('background', m.background)
            item.SetProperty('processor', m.processor )
            item.SetProperty('thumb', m.thumb)
            item.SetProperty('url', m.URL )
            item.SetProperty('rating', imageDir + "rating" + m.rating + ".png" )
                        
            item.SetProperty('media_type', m.type)
            
            if (m.thumb != 'default'):
                item.SetThumbnail(m.thumb)
            elif  playlist.logo != 'none':
                item.SetThumbnail(playlist.logo)
            else:
                item.SetThumbnail(thumb)
            
            item.SetProperty('icon', icon)
            ##mc.ShowDialogOk("item", "Label = " + item.GetLabel() + "Icon = " + item.GetIcon() + "Thumb = " + item.GetThumbnail() )
            listcontrol.append(item)

    if view != '':
        playlist.view = view

    newview = SetListView(playlist.view, passive=True)
    mc.GetWindow(14000).GetList(newview).SetItems(listcontrol)        #set displayed list
    SetListView(playlist.view, passive=False)
    mc.GetWindow(14000).GetList(newview).SetFocus()    
    mc.HideDialogWait()
        
    return 0           

######################################################################
# Description: Gets the playlist entry thumb image for different types
# Parameters : mediaitem: item for which to retrieve the thumb
# Return     : thumb image (local) file name
######################################################################
def getPlEntryThumb(mediaitem, playlist):
    pl_focus = playlist        ### only one playlist used so it's always in focus            
    type = mediaitem.GetType()       
        
    #some types are overruled.
    if type[0:3] == 'rss':
        type = 'rss'
    elif type[0:4] == 'atom':
        type = 'rss'
    elif type[0:3] == 'xml':
        type = 'playlist'
    elif type[0:4] == 'opml':
        type = 'playlist'
    elif type[0:6] == 'search':
        type = 'search'               
    elif type == 'directory':
        type = 'playlist'
    elif type == 'window':
        type = 'playlist'             
    elif mediaitem.type == 'skin':
        type = 'script'   
    elif mediaitem.type == 'app':
        type = 'script'
    
    #we now know the image type. Check the playlist specific icon is set
    URL=''
    if type == 'playlist':
        if pl_focus.icon_playlist != 'default':
            URL = pl_focus.icon_playlist
    elif type == 'rss':
        if pl_focus.icon_rss != 'default':
            URL = pl_focus.icon_rss
    elif type == 'script':
        if pl_focus.icon_script != 'default':
            URL = pl_focus.icon_script
    elif type == 'plugin':
        if pl_focus.icon_plugin != 'default':
            URL = pl_focus.icon_plugin                    
    elif type == 'video':
        if pl_focus.icon_video != 'default':
            URL = pl_focus.icon_video
    elif type == 'audio':
        if pl_focus.icon_audio != 'default':
            URL = pl_focus.icon_audio
    elif type == 'image':
        if pl_focus.icon_image != 'default':
            URL = pl_focus.icon_image
    elif type == 'text':
        if pl_focus.icon_text != 'default':
            URL = pl_focus.icon_text
    elif type == 'search':
        if pl_focus.icon_search != 'default':
            URL = pl_focus.icon_search
    elif type == 'download':
        if pl_focus.icon_download != 'default':
            URL = pl_focus.icon_download
    
    #if the icon attribute has been set then use this for the icon.
    if mediaitem.icon != 'default':
        ext = getFileExtension(mediaitem.icon)
        loader = CFileLoader2() #file loader
        loader.load(mediaitem.icon, imageCacheDir + "icon." + ext, proxy="ENABLED", content_type='image')
        if loader.state == 0:    
            URL = loader.localfile

    if URL == '':
        URL = imageDir+'icon_' + str(type) + '.png'
        
    URL_thumb = imageDir+'thumb_' + str(type) + '.png'
        
    return URL, URL_thumb

######################################################################
# Description: Handle selection of playlist search item (e.g. Youtube)
# Parameters : item=mediaitem
#              append(optional)=true is playlist must be added to 
#              history list;
# Return     : MediaItem to be parsed
######################################################################
def PlaylistSearch(item):
    string = ''
    
    searchstring = mc.ShowDialogKeyboard("Search", "", False)
     
    if len(searchstring) == 0:
        return None      

    #get the search type:
    index=item.type.find(":")
    if index != -1:
        search_type = item.type[index+1:]
    else:
        search_type = ''

    #youtube search
    if (item.type == 'search_youtube') or (search_type == 'html_youtube'):
        fn = searchstring.replace(' ','+')
        if item.URL != '':
            URL = item.URL
        else:
            URL = 'http://gdata.youtube.com/feeds/base/videos?max-results=50&alt=rss&q='
        URL = URL + fn
          
        choice = 0                 ## no easy way to do a Select Dialog in Boxee API
                                   ## youtube search always by Relevance

        #validate the selected item
        if choice == 1: #Date Added
            URL = URL + '&search_sort=video_date_uploaded'
        elif choice == 2: #View Count
            URL = URL + '&search_sort=video_view_count'
        elif choice == 3: #Rating
            URL = URL + '&search_sort=video_avg_rating'
       
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'rss:video'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player
        mediaitem.processor = item.processor     

        return mediaitem

    elif (item.type == 'search_shoutcast') or (search_type == 'xml_shoutcast'):
        fn=urllib.quote(searchstring)
        URL = 'http://www.shoutcast.com/sbin/newxml.phtml?search='
        URL = URL + fn

        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'xml_shoutcast'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player
        mediaitem.processor = item.processor

        return mediaitem

    ############ Haven't tested search_flickr yet

    elif (item.type == 'search_flickr') or (search_type == 'html_flickr'):
        fn = searchstring.replace(' ','+')
        URL = 'http://www.flickr.com/search/?q='
        URL = URL + fn

        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'html_flickr'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player
        mediaitem.processor = item.processor

        return mediaitem

    else: #generic search
         
        fn = urllib.quote(searchstring)
        URL = item.URL
        URL = URL + fn
               
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        if search_type != '':
            mediaitem.type = search_type
        else: #default
            mediaitem.type = 'playlist'
            
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player
        mediaitem.processor = item.processor

        return mediaitem
                    
######################################################################
# Description: Handles the selection of an item in the list. 
# Either listitem or URL should be specified
# Parameters : listitem(optional)=Boxee listitem selected
#              URL(optional)=link to media file;
# Return     : -
######################################################################
def SelectItem(iURL='', listitem=''):
    if listitem != '':
        mediaitem=CMediaItem()
        mediaitem.URL = listitem.GetProperty("url")
        mediaitem.processor = listitem.GetProperty("processor")
        mediaitem.type = listitem.GetProperty("media_type")
        mediaitem.background = listitem.GetProperty("background")
    elif iURL != '':
        mediaitem=CMediaItem()
        mediaitem.URL = iURL
        ext = getFileExtension(iURL)
        if ext == 'plx':
            mediaitem.type = 'playlist'
        elif ext == 'xml' or ext == 'atom':
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
    
    #type = mediaitem.type
    type = mediaitem.GetType()

    #mediaitem is some type of playlist (non-search, non-media)
    
    if type == 'playlist' or type == 'favorite' or type[0:3] == 'rss' or \
       type == 'rss_flickr_daily' or type == 'directory' or \
       type == 'html_youtube' or type == 'xml_shoutcast' or \
       type == 'xml_applemovie' or type == 'atom' or type == 'opml':
        #add new URL to the history array
        mc.GetWindow(14000).PushState()

        #exception case: Do not add Youtube pages to history list
#        if mediaitem.GetType() == 'html_youtube':
#            append = False
                
        result = ParsePlaylist(mediaitem=mediaitem)
        ##mc.ShowDialogOk("Debug", "ParsePlaylist result = " + str(result))
        
        if result != 0:        ### ParsePlaylist failed + playlist cleared by ParsePlaylist
            mc.HideDialogWait()
            return -1      

    #mediaitem is a audio or video to play

    elif type == 'video' or type == 'audio' or type == 'html':
        mc.ShowDialogWait()
        MyPlayer = CPlayer()

        ##mc.ShowDialogOk("Debug in SelectItem", "type = " + mediaitem.type + '\n' + "processor = " + mediaitem.processor)

        result = MyPlayer.play_URL(mediaitem.URL, mediaitem)
                                                
        mc.HideDialogWait()

        if result["code"] == 1:
            # general error
            try:
                result["data"]
            except KeyError:
                result["data"]="Cannot open file"
            
            if result["data"][0:2] == 'p:':
                result["data"]=result["data"][2:]
                etitle="Processor Error"
            else:
                etitle="Error"
            mc.ShowDialogOk(etitle, result["data"])

        elif result["code"] == 2:
            # redirect to playlist
            redir_item=CMediaItem()
            redir_item.URL=result["data"]
            redir_item.type='playlist'
            ParsePlaylist(mediaitem=redir_item, URL=result["data"])

        else:
            #When app reloads after play it will resume at the last playlist viewed 
            mc.GetApp().GetLocalConfig().SetValue("resume", "True")

    #mediaitem is other type: go through possibilites

    elif type == 'image':
        viewImage(0,mediaitem) #single file show
        mc.GetApp().GetLocalConfig().SetValue("resume", "True")        


    elif type == 'text':
        mc.GetWindow(14000).PushState()
        OpenTextFile(mediaitem=mediaitem)

    elif (type[0:3] == 'app'):
        InstallApp(mediaitem=mediaitem)

    elif type == 'download':
        mc.ShowDialogOk("Error", "This item is not supported because it is a " + type)

    elif (type[0:6] == 'search'):
        mediaitem_search = PlaylistSearch(mediaitem)
        if mediaitem_search != None:
            mc.GetWindow(14000).PushState()
            result = ParsePlaylist(mediaitem=mediaitem_search)
        
    elif type == 'window':
        mc.ShowDialogOk("Error", "This item is not supported because it is a " + type)

    else:
        mc.ShowDialogOk("Playlist format error", '"' + type + '"' + " is not a valid type.")
        
    return 0

######################################################################
# Description: Handles display of a text file.
# Parameters : URL=URL to the text file.
# Parameters : mediaitem=text file media item.
# Return     : -
######################################################################
def OpenTextFile(URL='', mediaitem=0):
    mc.ShowDialogWait() #loading text
                    
    if mediaitem == 0:
        mediaitem=CMediaItem()
        
    #from here we use the mediaitem object
    loader = CFileLoader2()
    #first load the background image
        
    if URL == '':
        URL = mediaitem.URL
        
    #now load the text file
    loader.load(URL, tempCacheDir + 'document.txt')
    if loader.state == 0:
        #open the local file
        try:            
            f=open(loader.localfile, 'r')
            data = f.read()
            f.close()
            text=""
            lines = data.split("\n")
            #we check each line if it exceeds 80 characters and does not contain
            #any space characters (e.g. long URLs). The textbox widget does not
            #split up these strings. In this case we add a space characters ourself.
            for m in lines:
                if (len(m) > 80) and (m.find(" ") == -1):
                    m = m[:80] + " " + m[80:]
                text = text + m + "\n"
                
            offset = 0

            mc.HideDialogWait() #loading text finished

            ## Hide list, Show text in textbox, Focus on textbox scrollbar
            ##mc.ShowDialogOk("Text file", text)
            mc.GetWindow(14000).GetControl(GetListView()).SetVisible(False)   #Hide List

            #stackitem = mc.GetWindow(14000).GetList(555).GetItem(0)
            stackitem = mc.ListItem()
            stackitem.SetProperty("contenttext",text)
            stacklist = mc.ListItems()
            stacklist.append(stackitem)
            mc.GetWindow(14000).GetList(555).SetItems(stacklist)

            mc.GetWindow(14000).GetControl(130).SetVisible(True)    #Show TextBox
            mc.GetWindow(14000).GetControl(131).SetVisible(True)    #Show Scrollbar
            mc.GetWindow(14000).GetControl(131).SetFocus()  #Focus on TextBox ScrollBar

            return 0 #success
        except IOError:
            mc.HideDialogWait()
            return -1 #failure

    else:
        mc.HideDialogWait()
        return -1 #failure   
                
######################################################################
# Description: Handles image slideshow.
# Parameters : playlist=the source playlist
#              pos=media item position in the playlist
#              mode=view mode (0=slideshow)
#              iURL(optional) = URL to image
# Return     : -
######################################################################
def viewImage(mode=0, mediaitem=''):
    mc.ShowDialogWait()

    URL = mediaitem.URL;                                                          
    ext = getFileExtension(URL)
    
    mc.HideDialogWait()    

    listitem_image = mc.ListItem(mc.ListItem.MEDIA_PICTURE)
    listitem_image.SetContentType("url")
    listitem_image.SetLabel(mediaitem.name)
    listitem_image.SetPath(URL)

    player = mc.Player()
    player.PlayWithActionMenu(listitem_image)    
    
    return 0       
            
######################################################################
# Description: Handles Installation of Boxee Applications
# Parameters : URL=URL to the script ZIP file.
# Parameters : mediaitem=media item containing application.        
# Return     : -
######################################################################
def InstallApp(URL='', mediaitem=CMediaItem()):           
    type = mediaitem.GetType(0)
    attributes = mediaitem.GetType(1)
            
    if type == 'app':
        response = mc.ShowDialogConfirm("Message", "Install Boxee App?", "No", "Yes")
        if response == False:
            return
    
    mc.ShowDialogWait() #loading text
    
    installer = CInstaller()
#    if attributes == 'navi-x':
    result = installer.InstallNaviX(URL, mediaitem)
#    else:    
#        result = installer.InstallScript(URL, mediaitem)

    if result == 0:
        mc.ShowDialogOk("Installer", "Installation successful.")
        mc.ShowDialogOk("Installer", "Please restart Boxee.")
    elif result == -1:
        mc.ShowDialogOk("Installer", "Installation aborted.")
    elif result == -3:
        mc.ShowDialogOk("Installer", "Invalid ZIP file.")
    else:
        mc.ShowDialogOk("Installer", "Installation failed.")

    mc.HideDialogWait()

    return

######################################################################
# Description: 
# Parameters : 
# Return     : -
######################################################################   
def MenuLeftSelectItem( itemNumber):
    if itemNumber == 0:
        SelectItem(iURL=home_URL)
        mc.GetWindow(14000).GetList(GetListView()).SetFocus()
    elif itemNumber == 1:
        userkey = mc.GetApp().GetLocalConfig().GetValue("userkey")
        arguments = "?user=" + userkey + "&request=get&type=.plx"              
        SelectItem(iURL = favorites_URL + arguments)
    elif itemNumber == 2:     
        ListView = mc.GetApp().GetLocalConfig().GetValue("listview")
        if ListView == "default":  
            mc.GetApp().GetLocalConfig().SetValue("listview", "thumbnails")        
        elif ListView == "thumbnails":
            mc.GetApp().GetLocalConfig().SetValue("listview", "list")  
        else:
            mc.GetApp().GetLocalConfig().SetValue("listview", "default")                    
        Init()
        ParsePlaylist(reload=False)
        mc.GetWindow(14000).GetList(122).SetFocus()
        mc.GetWindow(14000).GetList(122).SetFocusedItem(itemNumber)
    elif itemNumber == 3:
        if nxserver.is_user_logged_in() == True:
            response = mc.ShowDialogConfirm("Message", "Sign out?", "No", "Yes")
            if response:
                nxserver.logout()
                mc.ShowDialogOk("Sign out", "Sign out Successful.")
                Init()
        else:
            result = nxserver.login()
            if result == 0:
                mc.ShowDialogOk("Sign in", "Sign in Successful.")
                Init()
            elif result == -1:
                mc.ShowDialogOk("Sign in", "Sign in Failed.")
        mc.GetWindow(14000).GetList(GetListView()).SetFocus()
    elif itemNumber == 4:
        mc.CloseWindow()
    pass

######################################################################
# Description: 
# Parameters : 
# Return     : -
######################################################################   
def MenuRightSelectItem( itemNumber):
    if itemNumber == 0: #add item to favorites
        stackitem = mc.GetWindow(14000).GetList(555).GetItem(0)
        URL = stackitem.GetProperty("URL")
        if URL.find(favorites_URL) != -1:
            mc.ShowDialogOk("Error", "Cannot Add From Favorite List.")  
            return
        ModifyFavoriteList('add')        
        mc.GetWindow(14000).GetList(GetListView()).SetFocus()
    elif itemNumber == 1: #remove items from favorites
        stackitem = mc.GetWindow(14000).GetList(555).GetItem(0)
        URL = stackitem.GetProperty("URL")
        if URL.find(favorites_URL) == -1:
            mc.ShowDialogOk("Error", "Please Select Favorite List First.") 
            return
        ModifyFavoriteList('remove')
        
        userkey = mc.GetApp().GetLocalConfig().GetValue("userkey")
        arguments = "?user=" + userkey + "&request=get&type=.plx"              
        ParsePlaylist(URL = favorites_URL + arguments)
        
        mc.GetWindow(14000).GetList(GetListView()).SetFocus()
    elif itemNumber == 2: #about Navi-X
        mc.GetWindow(14000).PushState()
        OpenTextFile(URL='readme.txt') 
    
######################################################################
# Description: 
# Parameters : 
# Return     : -
######################################################################   
def GetListView():
    if mc.GetWindow(14000).GetControl(212).IsVisible() == True:
        return 212
    else:
        return 112
    
######################################################################
# Description: 
# Parameters : 
# Return     : -
######################################################################   
def SetListView(view, passive=False):
    ListView = mc.GetApp().GetLocalConfig().GetValue("listview")
    if ListView == "list":
        view = "list"
    elif ListView == "thumbnails":
        view = "thumbnails"
     
    if view == "default":
        oldview = 212
        newview = 112
    if view == "list":
        oldview = 212
        newview = 112
    elif view == "thumbnails":
        oldview = 112
        newview = 212        
    else: #list
        oldview = 212
        newview = 112
        
    if passive == False:    
        mc.GetWindow(14000).GetControl(oldview).SetVisible(False)   #Hide List
        mc.GetWindow(14000).GetControl(newview).SetVisible(True)   #Show List
    
    return newview
       
######################################################################
# Description: 
# Parameters : 
# Return     : -
######################################################################   
def ModifyFavoriteList(command='none'):
    list = mc.GetWindow(14000).GetList(GetListView())
    itemNumber = list.GetFocusedItem()
    
    if itemNumber < 0:
        return
            
    if command == 'add':
        listitem = list.GetItem( itemNumber)
        mediaitem=CMediaItem()
        mediaitem.type = listitem.GetProperty("media_type")
        mediaitem.name = listitem.GetLabel()
        mediaitem.thumb = listitem.GetProperty("thumb")
        mediaitem.URL = listitem.GetProperty("url")
        mediaitem.processor = listitem.GetProperty("processor")
    
        postdata = "type=" + mediaitem.type + "\n"
        postdata = postdata + "name=" + mediaitem.name + "\n"
        postdata = postdata + "thumb=" + mediaitem.thumb + "\n"       
        postdata = postdata + "URL=" + mediaitem.URL + "\n"
        postdata = postdata + "processor=" + mediaitem.processor + "\n"
    
        try:
            userkey = mc.GetApp().GetLocalConfig().GetValue("userkey")
            arguments = "?user=" + userkey + "&request=add"
            req = urllib2.Request(favorites_URL + arguments, postdata)
            f = urllib2.urlopen(req)
            data = f.read()
            f.close()
        except IOError:
            pass
    elif command == 'remove':
        try:
            userkey = mc.GetApp().GetLocalConfig().GetValue("userkey")
            arguments = "?user=" + userkey + "&request=remove&index=" + str(itemNumber)
            req = urllib2.Request(favorites_URL + arguments)
            f = urllib2.urlopen(req)
            data = f.read()
            f.close()
        except IOError:
            pass