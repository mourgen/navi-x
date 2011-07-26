from default import *
from tools import *

import urllib2
from threading import Thread
import stat

class Navi_DOWNLOAD:
    def __init__(self, app):
        #Init vars
        self.app    = app
        self.active = False
        self.url    = ''
        self.saveto = ''


    def urlgrab(self, url, filename):
        self.url    = url
        self.saveto = filename

    def start(self, infodata, infopath, freespace, filename):
        self.active = True

        # Perform the mapping
        info = (self.app, infodata, infopath, freespace, filename)
        
        #Start Download Thread
        thread = Worker(self.url, self.saveto, info)
        thread.start()

        # Send shutdown jobs to all threads, and wait until all the jobs have been completed
        self.pool.shutdown()



###Worker class for downloading
class Worker(Thread):
    def __init__(self, url, file, info, chunk_size=8192):
        Thread.__init__(self)
        self.app, self.infodata, self.infopath, self.freespace, self.filename = info
        self.file       = file
        self.url        = url
        self.chunk_size = chunk_size

    def run(self):
        #Check Write access
        if can_create_file(self.infopath):
            self.app.gui.ShowDialogNotification('No write access to %s' % self.infopath)
            self.app.api.download.active = False
            return

        #Check if file exists
        if os.path.isfile(self.file):
            os.chmod(self.file, stat.S_IWUSR)
            os.remove(self.file)

        #Init url/path pointers
        response   = urllib2.urlopen(self.url)
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0
        result     = open(self.file, 'wb')

        #check if enough freespace
        if self.freespace < total_size and self.freespace != 0:
            self.app.gui.ShowDialogNotification('Not enough freespace to download the item')
            self.app.api.download.active = False
            return

        self.app.gui.SetVisible(4000, True)

        i = 0
        while 1:
            chunk = response.read(self.chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            result.write(chunk)

            i += 1
            if((i/10)%1 == 0):
                self.update_gui(bytes_so_far, total_size)

        #Create info file as json
        json_dumps(self.infodata, self.infopath)

        self.app.gui.ShowDialogNotification('Download Complete')
        self.app.gui.SetVisible(4000, False)
        self.app.api.download.active = False

        return bytes_so_far

    def update_gui(self, bytes_so_far, total_size):
        try:
            #calculate percentage
            perc = float(bytes_so_far) / total_size

            #update gui window
            self.app.gui.SetTexture(4001, 'download/download-%s.png' % int(round( perc*100, -1)) )
            self.app.gui.SetLabel(4002, 'Item: %s' % self.filename)
            self.app.gui.SetLabel(4005, 'Downloading: %s%%' % round(perc*100, 1) )
        except:
            pass