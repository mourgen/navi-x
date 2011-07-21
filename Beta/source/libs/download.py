from default import *

#Module specific Imports
from threading import Thread, Semaphore
from urlgrabber.grabber import URLGrabber, URLGrabError
from urlgrabber.progress import MultiFileMeter
from tools import *
import traceback

######
### DOWNLOADER
######
### Note, gui update is done in external/urlgrabber/progress L253
######

class Navi_DOWNLOAD:
    def __init__(self, app):
        #Init vars
        self.app = app
        self.active = False
        
        progress_obj = MultiFileMeter(app)
        max_bandwidth = app.url_max_bandwidth *1000

        #Init grabber
        if app.os =='windows':
            self.grabber = URLGrabber(reget=None, user_agent=app.url_useragent, bandwidth=max_bandwidth, keepalive=1, progress_obj=progress_obj)
        else:
            self.grabber = URLGrabber(reget="simple", user_agent=app.url_useragent, bandwidth=max_bandwidth, keepalive=1, progress_obj=progress_obj)

        self.maxthreads = 1
        self.queue = []
        self.threads = []
        self.sem = Semaphore()
    
    #Add download url
    def urlgrab(self, url, filename=None, **kwargs):
        self.queue.append( (url, filename, kwargs) )

    #Start download from que
    def start(self, freespace):
        if hasattr(self.grabber.opts.progress_obj, 'start'):
            self.grabber.opts.progress_obj.start(freespace, len(self.queue))

        if self.queue and (len(self.threads) < self.maxthreads):
            url, filename, kwargs = self.queue[0]
            del self.queue[0]
            thread = Worker(self, self.app, url, filename, kwargs)
            self.threads.append(thread)
            print "NAVI-X: Starting Download: %s" % url
            thread.start()
            self.active = True


###Worker class for downloading
class Worker(Thread):
    def __init__(self, parent, app, url, filename, kwargs):
        #Init vars
        Thread.__init__(self)
        self.app = app
        self.parent = parent
        self.url = url
        self.filename = filename
        self.kwargs = kwargs

    def run(self):
        print "NAVI-X: Download worker started"
        grabber = self.parent.grabber
        progress_obj = grabber.opts.progress_obj
        if isinstance(progress_obj, MultiFileMeter):
            self.kwargs['progress_obj'] = progress_obj.newMeter()
        try:
            #Download file
            self.parent.grabber.urlgrab(self.url, self.filename, **self.kwargs)
            #Create info file as json
            json_dumps(self.kwargs.get('infodata', ''), self.kwargs.get('infopath', ''))
            #Show Complete notification
            self.app.gui.ShowDialogNotification('Download of %s is completed' % self.kwargs.get('text', ''))
            Log(self.app, 'NAVI-X: Download Completed - %s' % self.url)
        except URLGrabError, e:
            try:
                self.app.api.download.active = False
                try: os.remove( os.path.join(path, '%s.plx' % self.kwargs.get('text', '') ) )
                except: pass
                self.app.gui.ShowDialogOk(self.app.local['39'], 'Error: %s' % e)
                Log(self.app, 'NAVI-X: %s, %s' % (e, self.url))
            except:
                pass
        except:
            self.app.api.download.active = False
            Log(self.app, traceback.format_exc() )
        self.close()

    #Try to end thread
    def close(self):
        try:
            self.app.gui.SetEnabled(4000, False)
            self.app.api.download.active = False
        except:
            pass

        if self.isAlive():
            try:
                self._Thread__stop()
            except:
                print(str(self.getName()) + ' could not be terminated')
