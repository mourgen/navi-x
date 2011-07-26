import os, sys
import mc, difflib

sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
from config import *
from api import *
from library import *
from tools import *
from language import *
from database import *

global data_save
data_save = []
genres = {'movie':'movie', 'tv':'tv', 'tv show':'tv', 'podcast':'podcast', 'audio':'audio', 'pictures':'pictures', 'video':'video', 'browser':'browser'}
api = Navi_API(None)
filename = mc.GetApp().GetAppDir() + os.sep + 'data' + os.sep + 'scraper.json'
scraper_url = "http://navix.turner3d.net/playlist/2229/realtime_scrapers/"


def run():
    data_save.append("{ 'scrapers' : \n")
    data_save.append("  [ \n")

    data = api._PLX(url = scraper_url)
    if len(data) == 0: return
    
    scraper_file = open(filename,"w")
    playlist = Navi_PLAYLIST(data)

    for i in range(playlist.count()):
        item = playlist.get(i)
        if item.type == 'playlist':
            addScrapeSource(item, scraper_url)

    data_save.append( "  ], \n")
    data_save.append( "'version' : 1} \n")

    scraper_file.writelines(data_save)
    scraper_file.close()

def addScrapeSource(item, blockurl):
    data = api._PLX(item.path, 30, blockurl)
    if len(data) == 0: return None
    playlist = Navi_PLAYLIST(data)

    search = False
    options = {}

    for i in range(playlist.count()):
        item2nd = playlist.get(i)

        if item2nd.type == 'search':
            search = (item2nd.name, item2nd.path)

        elif item2nd.type == 'playlist':
            for genre in genres.keys():
                if difflib.SequenceMatcher(None, item2nd.name.lower(), genre).quick_ratio() > 0.8:
                    options[genres[genre]] = item2nd.path

    if search: addSearchSource(item.thumb, options, *search)
    addStreamSource(item.name, item.path, item.thumb, options)

def addSearchSource(thumb, options, name, url):
    if len(options) > 0:
        for option in options.keys():
            #self.search.insert(option, name, url, thumb)
            data_save.append( "    {'type':'search', 'tags':'"+option+"', 'name':'"+name+"', 'path':'"+url+"', 'thumb':'"+thumb+"'}, \n")
    data_save.append( "    {'type':'search', 'tags':'', 'name':'"+name+"', 'path':'"+url+"', 'thumb':'"+thumb+"'}, \n")

def addStreamSource(name, url, thumb, options):
    if len(options) > 0:
        for option in options.keys():
            #self.scrapers.insert(option, name, url, thumb)
            data_save.append("    {'type':'scraper', 'tag':'"+option+"', 'name':'"+name+"', 'path':'"+url+"', 'thumb':'"+thumb+"'}, \n")
    #self.scrapers.insert('None', name, url, thumb)
    data_save.append("    {'type':'scraper', 'tag':'', 'name':'"+name+"', 'path':'"+url+"', 'thumb':'"+thumb+"'}, \n")
