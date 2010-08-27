import mc
from string import *
import sys, os.path
import urllib
import re, random, string
##import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
import copy

from libs2 import *
from CURLLoader import *
from CPlayList import *
from CPlayer import *
from settings import *


        ######################################################################
        # Description: Parse playlist file. Playlist file can be a:
        #              -PLX file; Based on ParsePlaylist in navix.py
        # Parameters : URL (optional) =URL of the playlist file.
        #              mediaitem (optional)=Playlist mediaitem containing 
        #              playlist info. Replaces URL parameter.
        # Return     : 0 if success
        ######################################################################
def ParsePlaylist(URL='', mediaitem=CMediaItem(), reload=True):
    mc.ShowDialogWait()
    playlist = CPlayList()
    listcontrol = mc.GetWindow(14000).GetList(112).GetItems()
    del listcontrol[:]

    #load the playlist

    #type = mediaitem.type
    type = mediaitem.GetType()
    ##mc.ShowDialogOk("Debug", "Parse mediaitem of type " + type)

    if reload == True:
        #load the playlist
        if type == 'rss_flickr_daily':
            result = playlist.load_rss_flickr_daily(URL, mediaitem)                
        elif type[0:3] == 'rss':
            result = playlist.load_rss_20(URL, mediaitem)
        elif type[0:4] == 'atom':
            result = playlist.load_atom_10(URL, mediaitem)
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

    #mc.ShowDialogOk("Error", "playlist.load result =" + str(result))

    if result == -1: #error
        mc.ShowDialogOk("Error", "This playlist requires a newer Navi-X version")
    elif result == -2: #error
        mc.ShowDialogOk("Error", "Cannot open file.")
                
    if result != 0: #failure
        return -1

    #succesful
    ##mc.ShowDialogOk("Ok", "playlist loaded size ="+str(playlist.size()) )

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
    stackitem.SetProperty("listtitle",title);

            #set the background image
#always reload background image when loading playlist
    m = playlist.background
    if m == 'default': #default BG image
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

            icon = getPlEntryThumb(m, playlist)
            
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
            ###item.SetLabel(unicode(m.name, "utf-8", "ignore" ))  # this would not work.???
            label = str(m.name)
            item.SetLabel(label)
            item.SetPath(m.URL + " : " + m.processor )
            item.SetProperty('label2', label2)
            item.SetProperty('description', m.description)
            item.SetProperty('processor', m.processor )
            item.SetProperty('url', m.URL )
            item.SetProperty('media_type', m.GetType() )
            item.SetThumbnail(m.thumb)
            item.SetProperty('icon', icon)
            ##mc.ShowDialogOk("item", "Label = " + item.GetLabel() + "Icon = " + item.GetIcon() + "Thumb = " + item.GetThumbnail() )
            listcontrol.append(item)

    mc.GetWindow(14000).GetList(112).SetItems(listcontrol)        #set displayed list

    mc.HideDialogWait()

    return 0
##################################################################################3            

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
    elif type == 'html_youtube':
        type = 'playlist'
    elif type[0:6] == 'search':
        type = 'search'               
    elif type == 'directory':
        type = 'playlist'
    elif type == 'window':
        type = 'playlist'             
    elif mediaitem.type == 'skin':
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
        URL = mediaitem.icon

    if URL != '':
        ext = getFileExtension(URL)
        loader = CFileLoader2() #file loader
        loader.load(URL, imageCacheDir + "icon." + ext, timeout=2, proxy="ENABLED", content_type='image')
        if loader.state == 0:
            return loader.localfile
            
    return imageDir+'icon_'+str(type)+'.png'

#############################################################################################
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
    ##mc.ShowDialogOk("Debug", "Searchstring entered : " + searchstring)

    if len(searchstring) == 0:
        while len(searchstring) == 0:
             searchstring = mc.ShowDialogKeyboard("Search", "", False)
        else:
           pass
           

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
            URL = 'http://www.youtube.com/results?search_query='
        URL = URL + fn
          
##        #ask the end user how to sort
##        possibleChoices = ["Relevance", "Date Added", "View Count", "Rating"]
##        dialog = xbmcgui.Dialog()
##        choice = dialog.select("Sort by", possibleChoices)

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
        mediaitem.type = 'html_youtube'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player

##        #create history item
##        tmp = CHistorytem()

##        tmp.index = self.getPlaylistPosition()
##        tmp.mediaitem = self.mediaitem

##        self.pl_focus = self.playlist
##        result = self.ParsePlaylist(mediaitem=mediaitem)
        
##        if result == 0 and append == True: #successful
##            self.History.append(tmp)
##            self.history_count = self.history_count + 1

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

##            #create history item
##            tmp = CHistorytem()

##            tmp.index = self.getPlaylistPosition()
##            tmp.mediaitem = self.mediaitem

##            self.pl_focus = self.playlist
##            result = self.ParsePlaylist(mediaitem=mediaitem)
        
##            if result == 0 and append == True: #successful
##                self.History.append(tmp)
##                self.history_count = self.history_count + 1

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

##            #create history item
##            tmp = CHistorytem()

##            tmp.index = self.getPlaylistPosition()
##            tmp.mediaitem = self.mediaitem

##            self.pl_focus = self.playlist
##            result = self.ParsePlaylist(mediaitem=mediaitem)
        
##            if result == 0 and append == True: #successful
##                self.History.append(tmp)
##                self.history_count = self.history_count + 1

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

##            #create history item
##            tmp = CHistorytem()

##            tmp.index = self.getPlaylistPosition()
##            tmp.mediaitem = self.mediaitem

##            self.pl_focus = self.playlist
##            result = self.ParsePlaylist(mediaitem=mediaitem)
        
##            if result == 0 and append == True: #successful
##                self.History.append(tmp)
##                self.history_count = self.history_count + 1

            return mediaitem
                    
##################################################################################################
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
       type == 'xml_applemovie' or type == 'atom':
        #add new URL to the history array
        mc.GetWindow(14000).PushState()

        #exception case: Do not add Youtube pages to history list
        if mediaitem.GetType() == 'html_youtube':
            append = False
                
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
        
        if result != 0:
            mc.ShowDialogOk("Error", "Cannot open file.")
        else:
            #When app reloads after play it will resume at the last playlist viewed 
            mc.GetApp().GetLocalConfig().SetValue("resume", "True")

    #mediaitem is other type: go through possibilites

    elif type == 'image':
##        self.AddHistoryItem()
        mc.GetApp().GetLocalConfig().SetValue("resume", "True")
        viewImage(0,mediaitem) #single file show


    elif type == 'text':
##        self.AddHistoryItem()
        OpenTextFile(mediaitem=mediaitem)
##        mc.ShowDialogOk("Error", "This item is not yet supported because it is a " + type)

    #elif (type[0:6] == 'script') or (type[0:6] == 'plugin') or (type == 'skin'):
    elif (type == 'script') or (type == 'plugin') or (type == 'skin'):
##        self.AddHistoryItem()
##        self.InstallApp(mediaitem=mediaitem)
        mc.ShowDialogOk("Error", "This item is not supported because it is a " + type)

    elif type == 'download':
##        self.AddHistoryItem()
##        self.onDownload()
        mc.ShowDialogOk("Error", "This item is not supported because it is a " + type)

    elif (type[0:6] == 'search'):
        mediaitem_search = PlaylistSearch(mediaitem)
        result = ParsePlaylist(mediaitem=mediaitem_search)
        if result != 0:               ### Search Failed + playlist cleared by ParsePlaylist
            mc.HideDialogWait()
            return -1 
        
    elif type == 'window':
##        xbmc.executebuiltin("xbmc.ActivateWindow(" + mediaitem.URL + ")")
        mc.ShowDialogOk("Error", "This item is not supported because it is a " + type)

    else:
        mc.ShowDialogOk("Playlist format error", '"' + type + '"' + " is not a valid type.")
        
##    self.state_busy = 0

    return 0

######################################################################################
        ######################################################################
        # Description: Handles display of a text file.
        # Parameters : URL=URL to the text file.
        # Parameters : mediaitem=text file media item.
        # Return     : -
        ######################################################################
def OpenTextFile(URL='', mediaitem=0):
    mc.ShowDialogWait() #loading text
                    
##    if (mediaitem.background == 'default'):  ## todo: switch background if 'text'-type mediaitem contains a background
##        mediaitem = copy.copy(mediaitem)
            
##    textwnd = CTextView("CTextViewskin.xml", os.getcwd())
##    result = textwnd.OpenDocument(URL, mediaitem)
           

##    if result == 0:
##        textwnd.doModal()
##    else:
##        dialog = xbmcgui.Dialog()
##        dialog.ok("Error", "Cannot open file.")

###############  CTextView.OpenDocument() partly implemented here
    if mediaitem == 0:
        mediaitem=CMediaItem()
        
    #from here we use the mediaitem object
    loader = CFileLoader()
    #first load the background image
##    if (mediaitem.background != 'default'): #default BG image
##        ext = getFileExtension(mediaitem.background)
##        loader.load(mediaitem.background, imageCacheDir + "backtextview." + ext, 8, proxy="ENABLED")
##        if loader.state == 0: #if this fails we still continue
##            self.bg.setImage(loader.localfile)
        
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
            mc.GetWindow(14000).GetControl(112).SetVisible(False)   #Hide List
            mc.GetWindow(14000).GetControl(60).SetVisible(False)    #Hide List ScrollBar

            stackitem = mc.GetWindow(14000).GetList(555).GetItem(0)
            stackitem.SetProperty("contenttext",text)
            stacklist = mc.ListItems()
            stacklist.append(stackitem)
            mc.GetWindow(14000).GetList(555).SetItems(stacklist)
            #xbmc.executebuiltin("Control.SetLabel(130," +'"' + text + '"' + ")" )  #Put text in TextBox

            mc.GetWindow(14000).GetControl(130).SetVisible(True)    #Show TextBox
            mc.GetWindow(14000).GetControl(131).SetVisible(True)    #Show TextBox
            mc.GetWindow(14000).GetControl(131).SetFocus()  #Focus on TextBox ScrollBar

            return 0 #success
        except IOError:
            mc.HideDialogWait()
            return -1 #failure

    else:
        mc.HideDialogWait()
        return -1 #failure   
                
######################################################################################
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

    if mode == 0: #single file show

#        if iURL != '':
#            URL = iURL
#        else:    
#            URL = playlist.list[pos].URL
#            URL = mediaitem.URL;                   
#            urlopener = CURLLoader()
#            result = urlopener.urlopen(URL, mediaitem)
#            if result == 0:
#                URL = urlopener.loc_url                    
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
            


