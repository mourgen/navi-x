from default import *
from tools import *

import urllib2
import threading
import stat

class Navi_DOWNLOAD:
    def __init__(self, app):
        #Init vars
        self.app    = app
        self.active = False
        self.url    = ''
        self.saveto = ''
        self.chunk_size = 8192

    def urlgrab(self, url, filename):
        self.url    = url
        self.saveto = filename

    def start(self, infodata, infopath, freespace, filename):
        if self.active:
            return
        
        self.active = True

        self.infodata   = infodata
        self.infopath   = infopath
        self.freespace  = freespace
        self.file       = filename

        #Start Download Thread
        t = threading.Thread(name='Downloader', target=self.run, args=())
        t.start()

    def run(self):

        #Check Write access
        if can_create_file(self.infopath):
            self.app.gui.ShowDialogNotification('No write access to %s' % self.infopath)
            self.active = False
            return

        #Check if file exists
        if os.path.isfile(self.file):
            os.chmod(self.file, stat.S_IWUSR)
            os.remove(self.file)

        print

        #Init url/path pointers
        response     = urllib2.urlopen(self.url)
        total_size   = response.info().getheader('Content-Length').strip()
        total_size   = int(total_size)
        bytes_so_far = 0
        result       = open(self.file, 'wb')

        print 'total_size'
        print total_size
        print 'self.freespace'
        print self.freespace

        #check if enough freespace
        if self.freespace < total_size and self.freespace != 0:
            self.app.gui.ShowDialogNotification('Not enough freespace to download the item')
            self.active = False
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

        response.close()
        result.close()

        #Create info file as json
        json_dumps(self.infodata, self.infopath)

        self.app.gui.ShowDialogNotification('Download Complete')
        self.app.gui.SetVisible(4000, False)
        self.active = False

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