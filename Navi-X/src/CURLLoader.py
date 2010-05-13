#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CURLLoader:
# This class Retrieves the URL to a media item which the XBMC player 
# understands.
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
from libs2 import *
from settings import *
from CFileLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

class CURLLoader:
    def __init__(self, parent=0):
        self.parent=parent
        
    ######################################################################
    # Description: This class is used to retrieve the direct URL of given
    #              URL which the XBMC player understands.
    #              
    # Parameters : URL=source URL, mediaitem = mediaitem to open
    # Return     : 0=successful, -1=fail
    ######################################################################
    def urlopen(self, URL, mediaitem=0):
        result = 0 #successful
        
        if mediaitem.processor != '':
            result = self.geturl_processor(mediaitem) 
        elif URL.find('http://youtube.com') != -1:
            result = self.geturl_youtube(URL)
        else:
            self.loc_url = URL
              
        #special handling for apple movie trailers
        if (result == 0) and self.loc_url.find('http://movies.apple.com') != -1:
            result = self.geturl_applemovie(self.loc_url)         
        
        return result

    ######################################################################
    # Description: This class is used to retrieve the URL of a FlyUpload
    #              webpage
    #              
    # Parameters : URL=source URL
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_youtube(self, URL):
        #retrieve the flv file URL
        #URL parameter is not used.
        #Trace("voor "+self.loc_url)

        id=''
        #pos = self.loc_url.rfind('/')
        #pos2 = self.loc_url.rfind('.swf')
        #id = self.loc_url[pos+1:pos2] #only the video ID
        
        pos = URL.rfind('/')
        pos2 = URL.rfind('.swf')
        id = URL[pos+1:pos2] #only the video ID
        

        #Trace(id)
               
        try:
#            oldtimeout=socket_getdefaulttimeout()
#            socket_setdefaulttimeout(url_open_timeout)

            #retrieve the timestamp based on the video ID
            #self.f = urllib.urlopen("http://www.youtube.com/api2_rest?method=youtube.videos.get_video_token&video_id=" + id)
            self.f = urllib.urlopen("http://youtube.com/get_video_info?video_id=" + id)
            data=self.f.read()
            

            
            #index1 = data.find('<t>')
            #index2 = data.find('</t>')
            index1 = data.find('&token=')
            index2 = data.find('&thumbnail_url')
            if (index1 != -1) and (index2 != -1):
                #t = data[index1+3:index2]
                t = data[index1+7:index2]
                #t contains the timestamp now. Create the URL of the video file (high quality).
                self.loc_url = "http://www.youtube.com/get_video.php?video_id=" + id + "&amp;t=" + t + "&amp;fmt=18"
            else:
                self.loc_url = ""
        
        except IOError:
            self.loc_url = "" #could not open URL
            return -1 #fail
        
#        socket_setdefaulttimeout(oldtimeout)
       
        #Trace(self.loc_url)        
        
        if self.loc_url != "":
            return 0 #success
        else:
            return -1 #failure
    

    ######################################################################
    # Description: This class is used to retrieve media playback
    #              parameters using a processor server
    #              
    # Parameters : mediaitem = mediaitem to open
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_processor(self, mediaitem):
        print "Processor: phase 1 - query\n URL: "+mediaitem.URL+"\n Processor: "+mediaitem.processor
        SetInfoText("Processor: getting filter...")
        htmRaw=getRemote(mediaitem.processor+'?url='+urllib.quote_plus(mediaitem.URL))
        if htmRaw <= '':
            print "Processor error: nothing returned from learning phase";
            SetInfoText("")
            return -1

        if htmRaw[:2]=='v2':
            htmRaw=htmRaw[3:]
            inst=htmRaw
            htmRaw=''
            phase=0
            exflag=False
            phase1complete=False
            verbose=0
            proc_args=''
            inst_prev=''
            headers={}
            def_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4'

            ## initialize parameter dict
            v_defaults={
                'htmRaw':'',
                's_url':'',
                'regex':'',
                's_method':'get',
                's_action':'read',
                's_agent':def_agent,
                's_referer':'',
                's_cookie':'',
                's_postargs':'',
                'url':'',
                'swfplayer':'',
                'playpath':'',
                'agent':'',
                'pageurl':''
            }
            v=v_defaults

            ## command parser
            lparse=re.compile('^([^ =]+)([ =])(.+)$')
            
            ## condition parser
            ifparse=re.compile('^([^<>=!]+)\s*([!<>=]+)\s*(.+)$');

            while exflag==False:
                scrape=1
                phase=phase+1
                rep={}

                if_satisfied=False
                if_next=False
                if_end=False

                src_printed=False

                ## load defaults into v, leave undefined keys alone
                for ke in v_defaults:
                    v[ke]=v_defaults[ke]

                ## get instructions if args present
                if proc_args>'':
                    SetInfoText("Processor: phase "+str(phase)+" learn")
                    print "Processor: phase "+str(phase)+" learn"
                    inst=getRemote(mediaitem.processor+'?'+proc_args)
                    proc_args=''
                elif phase1complete:
                    SetInfoText("")
                    print "Processor error: nothing to do"
                    exflag=True
                else:
                    v['s_url']=mediaitem.URL

                if inst==inst_prev:
                    print "Processor error: endless loop detected"
                    SetInfoText("")
                    return -1

                inst_prev=inst
                lines=inst.splitlines()
                if len(lines) < 1:
                    print "Processor error: nothing returned from phase "+phase
                    SetInfoText("")
                    return -1
                linenum=0
                for line in lines:
                    linenum=linenum+1
                    line=re.sub('^\s*', '', line)

                    if verbose>0 and src_printed==False:
                        print "Processor NIPL source:\n"+inst
                        src_printed=True

                    if line>'' and verbose>1:
                        noexec=''
                        if if_next or if_end:
                            noexec=' (skipped)'
                        str_report="NIPL line "+str(linenum)+noexec+": "+line
                        if verbose>2 and (if_next or if_satisfied or if_end):
                            str_report=str_report+"\n (IF: satisfied="+str(if_satisfied)+", skip to next="+str(if_next)+", skip to end="+str(if_end)+")"
                        print str_report

                    # skip comments and blanks
                    if line[:1]=='#' or line=='':
                        continue

                    if if_end and line!='endif':
                        continue
                        
                    if if_next and line[0:5]!='elseif' and line!='else' and line!='endif':
                        continue
                
                    if line=='else':
                        if if_satisfied:
                            if_end=True
                        else:
                            if_next=False
                            if verbose>0:
                                print "Proc debug else: executing"
                        continue
                
                    elif line=='endif':
                        if_satisfied=False
                        if_next=False
                        if_end=False
                        continue

                    elif line=='scrape':
                        str_info="Processor:"
                        if phase>1:
                            str_info=str_info+" phase "+str(phase)
                        str_info=str_info+" scrape"
                        if scrape>1:
                            str_info=str_info+" "+str(scrape)
                        SetInfoText(str_info)
                        if v['s_url']=='':
                            print "Processor error: no scrape URL defined"
                            SetInfoText("")
                            return -1
                        scrape=scrape+1
                        scrape_args={
                          'referer': v['s_referer'],
                          'cookie': v['s_cookie'],
                          'method': v['s_method'],
                          'agent': v['s_agent'],
                          'action': v['s_action']
                        }
                        print "Processor "+v['s_method'].upper()+"."+v['s_action']+": "+v['s_url']
                        if verbose>0:
                            print "Proc debug remote args:"
                            print scrape_args
                        remoteObj=getRemote(v['s_url'], scrape_args)
                        
                        if v['s_action']=='headers':
                            headers=remoteObj
                            str_out="Proc debug headers:"
                            for ke in headers:
                                str_out=str_out+"\n "+ke+": "+str(headers[ke])
                                v[ke]=str(headers[ke])
                            if verbose>0:
                                print str_out
                        elif v['s_action']=='geturl':
                            v['v1']=remoteObj
                        else:
                            v['htmRaw']=remoteObj

                        if v['s_action']=='read' and v['regex']>'':
                            # get finished - run regex, populate v(alues) and rep(ort) if regex is defined
                            v['nomatch']=''
                            rep['nomatch']=''
                            for i in range(1,11):
                                ke='v'+str(i)
                                v[ke]=''
                                rep[ke]=''
                            p=re.compile(v['regex'])
                            match=p.search(v['htmRaw'])
                            if match:
                                rerep='Processor scrape:';
                                for i in range(1,len(match.groups())+1):
                                    val=match.group(i)
                                    key='v'+str(i)
                                    rerep=rerep+"\n "+key+'='+val
                                    rep[key]=val
                                    v[key]=val
                                if verbose>0:
                                    print rerep
    
                            else:
                                if verbose>0:
                                    print 'Processor scrape: no match'
                                rep['nomatch']=1
                                v['nomatch']=1
                        
                        # reset scrape params to defaults
                        v['s_method']='get'
                        v['s_action']='read'
                        v['s_agent']=def_agent
                        v['s_referer']=''
                        v['s_cookie']=''
                        v['s_postargs']=''
                        

                    elif line=='play':
                        if verbose==1:
                            print "Proc debug: play"
                        exflag=True
                        break

                    elif line=='report':
                        rep['phase']=str(phase)
                        proc_args=urllib.urlencode(rep)
                        proc_args=re.sub('v\d+=&','&',proc_args)
                        proc_args=proc_args.replace('nomatch=&','&')
                        proc_args=re.sub('&+','&',proc_args)
                        proc_args=re.sub('^&','',proc_args)
                        str_report="Processor report:"
                        for ke in rep:
                            if rep[ke]>'':
                                str_report=str_report+"\n "+ke+": "+rep[ke]
                        print str_report
                        break

                    else:
                        # parse
                        match=lparse.search(line)
                        if match is None:
                            print "Processor syntax error: "+line
                            SetInfoText("")
                            return -1
                        subj=match.group(1)
                        arg=match.group(3)

                        if subj=='if' or subj=='elsif':
                            if if_satisfied:
                                if_end=True
                            else:

                                ### process if / elseif operators
                                match=ifparse.search(arg)
                                if match:
                                    ### process if with operators
                                    lkey=match.group(1)
                                    oper=match.group(2)
                                    rraw=match.group(3)
                                    if oper=='=':
                                        oper='=='
                                    try:
                                        v[lkey]
                                    except KeyError:
                                        v[lkey]=''
                                    if rraw[0:1]=="'":
                                        rside=rraw[1:]
                                    else:
                                        try:
                                            v[rraw]
                                        except KeyError:
                                            v[rraw]=''
                                        rside=v[rraw]
                                    bool=eval("v[lkey]"+oper+"rside")
                                    if_report=" test: "+lkey+" "+oper+" "+rraw+"\n  left: "+v[lkey]+"\n right: "+rside

                                else:
                                    ### process single if argument for >''
                                    try:
                                        v[arg]
                                    except KeyError:
                                        v[arg]=''
                                    bool=v[arg]>''
                                    if_report=arg
                                    if bool:
                                        if_report=if_report+" > "
                                    else:
                                        if_report=if_report+" = "
                                    if_report=if_report+"'': "+v[arg]

                            if bool:
                                if_satisfied=True
                                if_next=False
                            else:
                                if_next=True

                            if verbose>0:
                                print "Proc debug "+subj+" => "+str(bool)+":\n "+if_report
                            continue
                    
                        if match.group(2)=='=':
                            # assignment operator
                            if arg[0:1]=="'":
                                v[subj]=arg[1:]
                                if verbose>0:
                                    print "Proc debug: "+subj+" set to string literal\n "+arg[1:]
                            else:
                                try:
                                    v[arg]
                                except KeyError:
                                    v[arg]=''
                                v[subj]=v[arg]
                                if verbose>0:
                                    print "Proc debug: "+subj+" set to "+arg+"\n "+v[arg]
                            
                        else:
                            ## do command
                            if subj=='verbose':
                                verbose=int(arg)

                            elif subj=='error':
                                print "Processor error: "+arg[1:]
                               	SetInfoText("")
                               	return -1

                            elif subj=='report_val':
                                match=lparse.search(arg)
                                if match is None:
                                    print "Processor syntax error: "+line
                                    SetInfoText("")
                                    return -1
                                ke=match.group(1)
                                va=match.group(3)
                                if va[0:1]=="'":
                                    rep[ke]=va[1:]
                                    if verbose>0:
                                        print "Proc debug report value: "+ke+" set to string literal\n "+va[1:]
                                else:
                                    try:
                                        v[va]
                                    except KeyError:
                                        v[va]=''
                                    rep[ke]=v[va]
                                    if verbose>0:
                                        print "Proc debug report value: "+ke+" set to "+va+"\n "+v[va]

                            elif subj=='concat':
                                match=lparse.search(arg)
                                if match is None:
                                    print "Processor syntax error: "+line
                                    SetInfoText("")
                                    return -1
                                ke=match.group(1)
                                va=match.group(3)
                                oldtmp=v[ke]
                                if va[0:1]=="'":
                                    v[ke]=v[ke]+va[1:]
                                else:
                                    try:
                                        v[va]
                                    except KeyError:
                                        v[va]=''
                                    v[ke]=v[ke]+v[va]
                                if verbose>0:
                                    print "Proc debug concat:\n old="+oldtmp+"\n new="+v[ke]

                            elif subj=='match':
                                v['nomatch']=''
                                rep['nomatch']=''
                                for i in range(1,11):
                                    ke='v'+str(i)
                                    v[ke]=''
                                    rep[ke]=''
                                p=re.compile(v['regex'])
                                match=p.search(v[arg])
                                if match:
                                    rerep='Processor match '+arg+':';
                                    for i in range(1,len(match.groups())+1):
                                        val=match.group(i)
                                        key='v'+str(i)
                                        rerep=rerep+"\n "+key+'='+val
                                        v[key]=val
                                    if verbose>0:
                                        print rerep
        
                                else:
                                    if verbose>0:
                                        print "Processor match: no match\n regex: "+v['regex']+"\n search: "+v[arg]
                                    v['nomatch']=1

                            elif subj=='replace':
                               # pre-set regex, replace var [']val
                                match=lparse.search(arg)
                                if match is None:
                                    print "Processor syntax error: "+line
                                    SetInfoText("")
                                    return -1
                                ke=match.group(1)
                                va=match.group(3)
                                if va[0:1]=="'":
                                    va=va[1:]
                                else:
                                    try:
                                        v[va]
                                    except KeyError:
                                        v[va]=''
                                    va=v[va]
                                oldtmp=v[ke]
                                v[ke]=re.sub(v['regex'], va, v[ke])
                                if verbose>0:
                                    print "Proc debug replace "+ke+":\n old="+oldtmp+"\n new="+v[ke]

                            elif subj=='unescape':
                                try:
                                    v[arg]
                                except KeyError:
                                    v[arg]=''
                                oldtmp=v[arg]
                                v[arg]=urllib.unquote(v[arg])
                                if verbose>0:
                                    print "Proc debug unescape:\n old="+oldtmp+"\n new="+v[arg]
                                
                            elif subj=='debug' and verbose>0:
                                print "Processor debug "+arg+":\n "+v[arg]

                            elif subj=='print':
                                if arg[0:1]=="'":
                                    print "Processor print: "+arg[1:]
                                else:
                                    print "Processor print "+arg+":\n "+v[arg]

                            else:
                                print "Processor error: unrecognized method '"+subj+"'"
                                SetInfoText("")
                                return -1

            if v['agent']>'':
                v['url']=v['url']+'?|User-Agent='+v['agent']
            mediaitem.URL=v['url']
            mediaitem.swfplayer=v['swfplayer']
            mediaitem.playpath=v['playpath']
            mediaitem.pageurl=v['pageurl']
            mediaitem.processor=''

        else:
            ## proc v1
            arr=htmRaw.splitlines()
            if len(arr) < 1:
                print "Processor error: nothing returned from learning phase";
                SetInfoText("")
                return -1
            URL=arr[0]
            if URL.find('error')==0:
                print "Processor: "+URL
                SetInfoText("")
                return -1
            report="Processor: phase 2 - instruct\n URL: "+URL
            if len(arr) < 2:
                self.loc_url = URL
                SetInfoText("")
                print "Processor: single-line processor stage 1 result\n playing "+URL
                return 0
            filt=arr[1]
            report=report+"\n filter: "+filt
            if len(arr) > 2:
                ref=arr[2]
                report=report+"\n referer: "+ref
            else:
                ref=''
            if len(arr) > 3:
                cookie=arr[3]
                report=report+"\n cookie: "+cookie
            else:
                cookie=''
    
            print report
            SetInfoText("Processor: scraping...")
            htm=getRemote(URL,{'referer':ref,'cookie':cookie})
            if htm == '':
                print "Processor error: nothing returned from scrape"
                SetInfoText("")
                return -1
    
            p=re.compile(filt)
            match=p.search(htm)
            if match:
                tgt=mediaitem.processor
                sep='?'
                report='Processor: phase 3 - scrape and report'
                for i in range(1,len(match.groups())+1):
                    val=urllib.quote_plus(match.group(i))
                    tgt=tgt+sep+'v'+str(i)+'='+val
                    sep='&'
                    report=report+"\n v"+str(i)+": "+val
                print report
                SetInfoText("Processor: processing...")
                htmRaw2=getRemote(tgt)
                if htmRaw2<='':
                    print "Processor error: could not retrieve data from process phase"
                    SetInfoText("")
                    return -1
                arr=htmRaw2.splitlines()
                mediaitem.URL=arr[0]
    
                if arr[0].find('error')==0:
                    print "Processor: "+arr[0]
                    SetInfoText("")
                    return -1
                if len(arr) > 1:
                    mediaitem.swfplayer=arr[1]
                if len(arr) > 2:
                    mediaitem.playpath=arr[2]
                if len(arr) > 3:
                    mediaitem.pageurl=arr[3]
                mediaitem.processor=''
            else:
                print "Processor error: pattern not found in scraped data"
                SetInfoText("")
                return -1
    
        self.loc_url = mediaitem.URL

        SetInfoText("Processor complete - playing...")
        time.sleep(.1)
        SetInfoText("")
        report="Processor final result:\n URL: "+self.loc_url
        if mediaitem.playpath>'':
            report=report+"\n PlayPath: "+mediaitem.playpath
        if mediaitem.swfplayer>'':
            report=report+"\n SWFPlayer: "+mediaitem.swfplayer
        if mediaitem.pageurl>'':
            report=report+"\n PageUrl: "+mediaitem.pageurl
        print report
            
        return 0
        
        
    ######################################################################
    # Description: This class is used to retrieve the URL Apple movie trailer
    #              webpage
    #              
    # Parameters : URL=source URL
    # Return     : 0=successful, -1=fail
    ######################################################################
    def geturl_applemovie(self, URL):

        if xbmc.getInfoLabel("System.BuildVersion")[:4] != '9.04':
            self.loc_url = URL + "?|User-Agent=QuickTime%2F7.2+%28qtver%3D7.2%3Bos%3DWindows+NT+5.1Service+Pack+3%29"
            return 0
              
        #for older XBMC versions we download the file before playing
        
        #calculate unique hash URL
        sum_str = ''
        sum = 0
        #calculate hash of URL
        for i in range(len(URL)):
            sum = sum + (ord(URL[i]) * i)
        localfile = str(sum) + ".mov"

        SetInfoText("Downloading Video...")
        
        values = { 'User-Agent' : 'QuickTime/7.6 (qtver=7.6;cpu=IA32;os=Mac 10,5,7)'}
        req = urllib2.Request(URL, None, values)
        f = urllib2.urlopen(req)
        
        file = open(tempCacheDir + localfile, "wb")        
        
        data=f.read(100 * 1024)
        while data != "":
            file.write(data)
            data=f.read(100 * 1024)
            
        file.close()
        f.close()  
        
        self.loc_url = tempCacheDir + localfile

        return 0 #success
