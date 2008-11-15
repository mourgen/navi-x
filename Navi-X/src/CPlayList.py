#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CPlaylist:
# Playlist class. Supports loading of Navi-X PLX files, RSS2.0 files, 
# flick feed files and html files.
#############################################################################

from string import *
import sys, os.path
import urllib
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from libs2 import *
from settings import *
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

######################################################################
# Description: Playlist class. Contains CMediaItem objects
######################################################################
class CPlayList:
    def __init__(self):
        self.version = '0'
        self.background = 'default'
        self.logo = 'none'
        self.title = ''
        self.description = ''
        self.URL = ''
        self.player = 'default'
        self.playmode = 'default'
        self.start_index = 0
        self.list = []
    
    ######################################################################
    # Description: Adds a item to playlist.
    # Parameters : item = CMediaItem obect
    # Return     : -
    ######################################################################
    def add(self, item):
        self.list.append(item)

    ######################################################################
    # Description: clears the complete playlist.
    # Parameters : -
    # Return     : -
    ######################################################################
    def clear(self):
        del self.list[:]
    
    ######################################################################
    # Description: removes a single entry from the playlist.
    # Parameters : index=index of entry to remove
    # Return     : -
    ######################################################################
    def remove(self, index):
        del self.list[index]

    ######################################################################
    # Description: Returns the number of playlist entries.
    # Parameters : -
    # Return     : number of playlist entries.
    ######################################################################
    def size(self):
        return len(self.list)

    ######################################################################
    # Description: Loads a playlist .plx file. File source is indicated by
    #              the 'filename' parameter or the 'mediaitem' parameter.
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_plx(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL
        
        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'playlist.plx', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            data = data.split('\n')
            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = '-1'
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = ''
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0

        #parse playlist entries 
        counter = 0
        state = 0
        for m in data:
            if state == 2: #parsing description field
                index = m.find('/description')
                if index != -1:
                    self.description = self.description + "\n" + m[:index]
                    state = 0
                else:
                    self.description = self.description + "\n" + m
            elif m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = m[:index]
                    value = m[index+1:]
                    if key == 'version' and state == 0:
                        self.version = value
                        #check the playlist version
                        if int(self.version) > int(plxVersion):
                            return -1
                    elif key == 'background' and state == 0:
                        self.background=value
                    elif key == 'player' and state == 0:
                        self.player=value
                    elif key == 'logo':
                        self.logo=value
                    elif key == 'title':
                            self.title=value
                    elif key == 'description':
                            index = value.find('/description')
                            if index != -1:
                                self.description=value[:index]
                            else:
                                self.description=value
                                state = 2 #description on more lines
                    elif key == 'playmode':
                            self.playmode=value
                    elif key == 'type':
                        if state == 1:
                            self.list.append(tmp)
                        else: #state=0
                            del self.list[:]
                        tmp = CMediaItem() #create new item
                        tmp.type = value
                        if tmp.type == 'video' or tmp.type == 'audio':
                            tmp.player = self.player

                        counter = counter+1
                        state = 1
                    elif key == 'version' and state == 1:
                        tmp.version=value
                    elif key == 'name':
                        tmp.name=value
                    elif key == 'thumb':
                        tmp.thumb=value
                    elif key == 'URL':
                        tmp.URL=value
                    elif key == 'DLloc':
                        tmp.DLloc=value
                    elif key == 'player':
                        tmp.player=value 
                    elif key == 'background':
                        tmp.background=value 
                    
        if state == 1:
            self.list.append(tmp)
        
        #if no version ID is found then this is not a valid playlist.
        if self.version == '-1':
            return -2
        
        return 0 #successful
        
    ######################################################################
    # Description: Loads a RSS2.0 feed xml file.
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load    
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_rss_20(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL

        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'feed.xml', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            data = data.split('<item>')
            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = ''
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0
        #clear the list
        del self.list[:]
        
        counter=0
        #parse playlist entries 
        for m in data:
            if counter == 0:
                #fill the title
                index = m.find('<title>')
                if index != -1:
                    index2 = m.find('</title>')
                    if index != -1:
                        value = m[index+7:index2]
                        self.title = value

                index = m.find('<description>')
                if index != -1:
                    index2 = m.find('</description>')
                    if index != -1:
                        value = m[index+13:index2]
                        self.description = value
                
                #fill the logo
                index = m.find('<image>')
                if index != -1:
                    index2 = m.find('</image>')
                    if index != -1:
                        index3 = m.find('<url>', index, index2)
                        if index != -1:
                            index4 = m.find('</url>', index, index2)
                            if index != -1:
                                value = m[index3+5:index4]
                                self.logo = value
                else: #try if itunes image
                    index = m.find('<itunes:image href="')
                    if index != -1:
                        index2 = m.find('"', index+20)
                        if index != -1:
                            value = m[index+20:index2]
                            self.logo = value
       
                counter = counter + 1
            else:
                tmp = CMediaItem() #create new item
                tmp.player = self.player

                #get the publication date.
                index = m.find('<pubDate')
                if index != -1:
                    index2 = m.find('>', index)
                    if index2 != -1:
                        index3 = m.find('</pubDate')
                        if index3 != -1:
                            index4 = m.find(':', index2, index3)
                            if index4 != -1:
                                value = m[index2+1:index4-2]
                                tmp.name = value

                #get the title.
                index = m.find('<title')
                if index != -1:
                    index2 = m.find('>', index)
                    if index2 != -1:
                        index3 = m.find('</title>')
                        if index3 != -1:
                            index4 = m.find('![CDATA[', index2, index3)
                            if index4 != -1:
                                value = m[index2+10:index3-3]
                            else:
                                value = m[index2+1:index3]
                            tmp.name = tmp.name + value

                #get the thumb
                index = m.find('<media:thumbnail')
                if index != -1:
                    index2 = m.find('url=', index+16)
                    if index2 != -1:
                        index3 = m.find('"', index2+5)
                        if index3 != -1:
                            value = m[index2+5:index3]
                            tmp.thumb = value

                #get the enclosed content.
                index = m.find('enclosure')
                index1 = m.find ('<media:content')
                if (index != -1) or (index1 != -1):
                    #enclosure is first choice. If no enclosure then use media:content
                    if (index == -1) and (index1 != -1):
                        index = index1
                    index2 = m.find('url="',index)
                    if index2 != -1:
                        index3 = m.find('"', index2+5)
                    else:
                        index2 = m.find("url='",index)
                        if index2 != -1:
                            index3 = m.find("'", index2+5)
                    if (index2 != -1) and (index3 != -1):
                        value = m[index2+5:index3]
                        tmp.URL = value
                            
                    if tmp.URL != '': #valid URL found
                        #validate the type based on file extension
                        ext_pos = tmp.URL.rfind('.') #find last '.' in the string
                        if ext_pos != -1:
                            ext = tmp.URL[ext_pos+1:]
                            ext = ext.lower()
                            if ext == 'jpg' or ext == 'gif' or ext == 'png':
                                tmp.type = 'image'
                            elif ext == 'mp3':
                                tmp.type = 'audio'
                            else:
                                tmp.type = 'video'
                                                        
                else: #no enclosed URL, use the link
                    index = m.find('<link>')
                    if index != -1:
                        index2 = m.find('</link>', index+6)
                        if index2 != -1:
                            value = m[index+6:index2]
                            tmp.URL = value
                        tmp.type = 'html'
                
                if tmp.URL != '':
                    self.list.append(tmp)
                    counter = counter + 1
                    
        return 0

    ######################################################################
    # Description: Loads a Flickr Daily feed xml file.
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load    
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_rss_flickr_daily(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL

        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'feed.xml', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            data = data.split('<item ')
            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = ''
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0
        #clear the list
        del self.list[:]
        
        counter=0
        #parse playlist entries 
        for m in data:
            if counter == 0:
                #fill the title
                index = m.find('<title>')
                if index != -1:
                    index2 = m.find('</title>')
                    if index != -1:
                        value = m[index+7:index2]
                        self.title = value
                
                counter = counter + 1
            else:
                #get the title.
                index = m.find('<title>')
                if index != -1:
                    index2 = m.find('</title>', index)
                    if index2 != -1:
                        value = m[index+7:index2]
                        name = value

                #get the enclosed content.
                items = 0
                index = m.find('<description>')
                if index != -1:
                    index2 = m.find('</description>', index)
                    if index2 != -1:
                        index3 = m.find('src=', index)
                        while index3 != -1:
                            index4 = m.find('"', index3+5)
                            if index4 != -1:
                                tmp = CMediaItem() #create new item
                                tmp.type = 'image'
                                if items > 0:
                                    tmp.name = name + " " + str(items+1)
                                else:
                                    tmp.name = name
                            
                                value = m[index3+5:index4-4]
                                if value[-6] == '_':
                                    value = value[:-6] + ".jpg"
                                tmp.URL = value
                                tmp.thumb = tmp.URL[:-4] + "_m" + ".jpg"
                                
                                self.list.append(tmp)
                                counter = counter + 1

                                items= items + 1
                                index3 = m.find('src=', index4)
                
        return 0

    ######################################################################
    # Description: Loads html elements from the Youtube website
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load    
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_html_youtube(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL
        
        loader = CFileLoader2()
        loader.load(self.URL, cacheDir + 'page.html', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            if data.find('<!-- end vEntry -->') != -1:
                entries = data.split('<!-- end vEntry -->')
#                entries = data.split('class="vlentry"')
            else:
                entries = data.split('class="vDetailEntry"') #playlist

            lines = data.split('\n')
            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = 'Youtube' + ' - ' + mediaitem.name
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        str_nextpage = 'Next Page'
        
        #clear the list
        if (mediaitem.URL != self.list[-1].URL) or (mediaitem.name != str_nextpage):
            del self.list[:]
            self.start_index = 0            
        else:
            self.list.pop()
            self.start_index = self.size()
        
        #parse playlist entries 
        for m in entries:
            index1= m.find('class="vtitle marT5"')
            if index1 == -1:
                index1= m.find('class="vllongTitle"')
            if index1 == -1:
                index1= m.find('class="vlshortTitle"')
            if index1 == -1:
                index1= m.find('class="vSnippetTitle"')
            if index1 == -1:
                index1= m.find('class="title"') #playlist
            if index1 != -1:
                tmp = CMediaItem() #create new item
                tmp.type = 'video'
 
                index2 = m.find('</div>', index1)
                index3 = m.find('watch?v=', index1, index2)
                index4 = m.find('"', index3, index2)
                index7 = m.find('&', index3, index4) #playlist
                if index7 != -1: #just for playlist
                    index4 = index7
                value = m[index3+8:index4]
                tmp.URL = 'http://youtube.com/v/' + value + '.swf'
                tmp.thumb = 'http://img.youtube.com/vi/' + value + '/default.jpg'

                #now get the title
                index5 = m.find('">', index4+1, index2)
                index6 = m.find('</a>', index5, index2)
                value = m[index5+2:index6]
                value = value.replace('<b>',"")
                value = value.replace('</b>',"")
                value = value.replace('&quot;',"")
                value = value.replace('&#39;',"\'")
                tmp.name = value
                
                tmp.player = self.player
                self.list.append(tmp)                

        #check if there is a next page in the html. Get the last one in the page.
        next_page_str = ''
        for m in lines:
            index1 = m.find('class="pagerNotCurrent">')
            if index1 != -1:
                next_page_str = m

        if next_page_str != '': #next page found. Grab the URL
            index2 = next_page_str.find('<a href="')
            if index2 != -1:
                index3 = next_page_str.find('"',index2+9)
                if index3 != -1:
                    value = next_page_str[index2+9:index3]
                    tmp = CMediaItem() #create new item
                    tmp.type = 'html_youtube'
                    tmp.name = str_nextpage
                    tmp.player = self.player
                    tmp.background = self.background
                    
                    #create the next page URL
                    index4 = self.URL.find("?")
                    url = self.URL[:index4]
                    index5 = value.find("?")
                    value = value[index5:]
                    tmp.URL= url+ value
                    
                    self.list.append(tmp)                

        return 0

    ######################################################################
    # Description: Loads shoutcast XML file.
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load    
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_xml_shoutcast(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL
        
        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'shoutcast.xml', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()

            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
#        self.logo = 'none'
        self.logo = "images\shoutcast.jpg"
        self.title = 'Shoutcast' + ' - ' + mediaitem.name
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0
        #clear the list
        del self.list[:]

        if data.find('<stationlist>') != -1:
            #parse playlist entries
            entries = data.split('</station>')            
            for m in entries:
                tmp = CMediaItem() #create new item
                tmp.type = 'audio'
                tmp.player = self.player

                index1 = m.find('station name=')
                if index1 != -1: #valid entry
                    index2= m.find('"', index1+14)
                    tmp.name = m[index1+14:index2]
                
                index1 = m.find('br=')
                if index1 != -1:
                    index2= m.find('"', index1+4)
                    bitrate = m[index1+4:index2]
                    tmp.name = tmp.name + " (" + bitrate + "kbps) "
                    tmp.URL = ''

                index1 = m.find('ct=')
                if index1 != -1:
                    index2= m.find('"', index1+4)
                    np = m[index1+4:index2]
                    tmp.name = tmp.name + "- Now Playing: " + np
                    tmp.URL = ''

                index1 = m.find('br=')
                if index1 != -1:
                    index2= m.find('"', index1+4)
                    bitrate = m[index1+4:index2]
                    tmp.name = tmp.name + " (" + bitrate + "kbps) "
                    tmp.URL = ''
   
                index1 = m.find('genre=')
                if index1 != -1: #valid entry
                    index2= m.find('"', index1+7)
                    genre = m[index1+7:index2]
                    tmp.name = tmp.name + '[' + genre + ']'

                index1 = m.find('id=')
                if index1 != -1:
                    index2= m.find('"', index1+4)
                    id = m[index1+4:index2]
                    tmp.URL = "http://www.shoutcast.com/sbin/shoutcast-playlist.pls?rn=" + id + "&file=filename.pls"

                    self.list.append(tmp)
                
        else: #<genrelist>
            #parse playlist entries
            entries = data.split('</genre>')
            for m in entries:
                tmp = CMediaItem() #create new item
                tmp.type='xml_shoutcast'
                tmp.player = self.player
                
                index1 = m.find('name=')
                if index1 != -1:
                    index2= m.find('"', index1+6)
                    genre = m[index1+6:index2]
                    tmp.name = genre
                    tmp.URL = "http://www.shoutcast.com/sbin/newxml.phtml?genre=" + genre
                    self.list.append(tmp)
                
        return 0
        
    ######################################################################
    # Description: Loads Quicksilverscreen HTML.
    # Parameters : filename=URL or local file
    #              mediaitem=CMediaItem object to load    
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_xml_applemovie(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL
        
        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'page.xml', proxy=proxy)
        if loader.state != 0:
            return -2
        filename = loader.localfile
        
        try:
            f = open(filename, 'r')
            data = f.read()
            entries = data.split('</movieinfo>')
            f.close()
        except IOError:
            return -2
        
        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = 'Apple Movie Trailers'
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0
        #clear the list
        del self.list[:]
        dates = [] #contains the dates
        
        #get the publication date and add it to the title.
        index = data.find('<records date')
        if index != -1:
            index2 = data.find(':', index)
            if index2 != -1:
                value = data[index+15:index2-2]
                self.title = self.title + " (" + value + ")"
        
        #parse playlist entries 
        for m in entries:
            #fill the title
            index = m.find('<title>')
            if index != -1:
                #create a new entry
                tmp = CMediaItem() #create new item
                tmp.type = 'video'
            
                index2 = m.find('</title>')
                if index2 != -1:
                    value = m[index+7:index2]
                    tmp.name = value

                #fill the release date
                date = 0
                index = m.find('<releasedate>')
                if index != -1:
                    index2 = m.find('</releasedate>')
                    if index2 != -1:
                        value = m[index+13:index2]
                        if value != '':
                            date=int(value[2:4]) * 365
                            date = date + int(value[5:7]) * 31
                            date = date + int(value[8:])
                        tmp.name = tmp.name + "  - (Release Date: " + value + ")"
                dates.append(date)
                    
                #fill the thumb
                index = m.find('<location>')
                if index != -1:
                    index2 = m.find('</location>')
                    if index2 != -1:
                        value = m[index+10:index2]
                        tmp.thumb = value

                #fill the URL
                index = m.find('<preview>')
                if index != -1:
                    index2 = m.find('</large>')
                    if index2 != -1:
                        index3 = m.find('http', index, index2)
                        if index3 != -1:
                            value = m[index3:index2]
                            tmp.URL = value

                self.list.append(tmp)

        #sort the list according release date
        for i in range(len(dates)-1):
            oldest = i
            for n in range(i, len(dates)):
                if dates[n] < dates[oldest]:
                    oldest = n
            if oldest != i:
                temp = dates[i]
                dates[i] = dates[oldest]
                dates[oldest] = temp
                
                temp = self.list[i]
                self.list[i] = self.list[oldest]
                self.list[oldest] = temp
        return 0        

    ######################################################################
    # Description: Loads the PLX files from a directory on the local disk. 
    #              Filename indicates the root directory to scan. Also the
    #              subdirectorys will be scanned for PLX files.
    # Parameters : filename=URL or local file (dir name)
    #              mediaitem=CMediaItem object to load
    # Return     : 0=succes, 
    #              -1=invalid playlist version, 
    #              -2=could not open playlist
    ######################################################################
    def load_dir(self, filename='', mediaitem=CMediaItem(), proxy="CACHING"):
        if filename != '':
            self.URL = filename
        else:
            self.URL = mediaitem.URL

        if self.URL[1] != ':':
            self.URL = RootDir + self.URL

        if not os.path.exists(self.URL):
            return -2

        #defaults
        self.version = plxVersion
        self.background = mediaitem.background
        self.logo = 'none'
        self.title = mediaitem.name
        self.description = ''
        self.player = mediaitem.player
        self.playmode = 'default'
        self.start_index = 0
        #clear the list
        del self.list[:]        

        #parse directory (including subdirectory) entries 
        try:        
            for root, dirs, files in os.walk(self.URL , topdown=False):
                for name in files:
                    if name[-4:] == '.plx':
                        tmp = CMediaItem() #create new item
                        tmp.type = 'playlist'
                        tmp.name = name[:-4]
                        tmp.URL = os.path.join(root, name)
                        self.list.append(tmp)                    
        except IOError:
            return -2

        return 0

    ######################################################################
    # Description: Saves a playlist .plx file to disk.
    # Parameters : filename=local path + file name
    # Return     : -
    ######################################################################
    def save(self, filename):
        f = open(filename, 'w')
        f.write('version=' + self.version + '\n')
        if self.background != 'default':
            f.write('background=' + self.background + '\n')
        if self.logo != 'none':
            f.write('logo=' + self.logo + '\n')
        f.write('title=' + self.title + '\n')
        if self.description != '':
            f.write('description=' + self.description + '/description' + '\n')
        if self.player != 'default':
            f.write('player=' + self.player + '\n')
        if self.playmode != 'default':            
            f.write('playmode=' + self.playmode + '\n')
        f.write('#\n')

        for i in range(len(self.list)):
            f.write('type=' + self.list[i].type + '\n')
            f.write('name=' + self.list[i].name + '\n')
            if self.list[i].thumb != 'default':
                f.write('thumb=' + self.list[i].thumb + '\n')
            f.write('URL=' + self.list[i].URL + '\n')
            if self.list[i].player != 'default':
                f.write('player=' + self.list[i].player + '\n')
            if len(self.list[i].DLloc) > 0:
                f.write('DLloc=' + self.list[i].DLloc + '\n')
            f.write('#\n')
        f.close()
        
        