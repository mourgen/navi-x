'''
NAVI-X App Builder
A Python script that builds an application from source and packages it for distribution on XBMC/Boxee repo.


CONFIGURATION
Windows Configuration:
- Install python 2.6 (www.python.org)
- Install lxml compiled python version from (http://pypi.python.org/pypi/lxml/2.3)
- Setup CMD Path
	*open Control Panel, System, Environment,
	* System Variables: append to the path variable ;C:\python2.6 (replace with your own path if different)
	* User Variables: Create nw variable 'Path' with value C:\python2.6


INFO
The script automaticly creates a package ready for deployment.
It cleans and restructures the file and directory structre depending on the platform chooses.
Any file with the extension '_xbmc' will be removed on the boxee platform and will be renamed on 
the xbmc platform from filename_xbmc to filename and overwrites any file if there.

Please specifiy the platform [xbmc, boxee] and source folder [source]

python build.py -i [source] -p [platform]

Build your app with compiled Python!
python build.py -i [source] -p [platform] -c

Get some usage help!
python build.py --help

Get debug output!
python build.py -i [source] -p [platform] --debug

'''

import sys
import os
import zipfile
import lxml.etree as ET
import logging
import subprocess
import shutil
import getopt
import cStringIO

'''
Logging Configuration
'''
logging_level = logging.INFO
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging_level)
log_formatter = logging.Formatter('%(asctime)s::%(name)s::%(levelname)s::%(message)s')
log_handler.setFormatter(log_formatter)

'''
Info
'''
VERSION = 1.0
__cwd__ = os.getcwd().replace(";","")

class BuildApp:
    def __init__(self, path, platform, compile=False):
        self.path = path
        self.platform = platform
        self.compile = compile
        self.build_dir = os.path.join(__cwd__, "build")
        self.app_dir = os.path.basename(self.path)
        self.log = logging.getLogger("BuildApp")
        self.log.setLevel(logging_level)
        self.log.addHandler(log_handler)
        self.log.debug("Initialized BuildApp.")

    def main(self):
        if self.isApp():
            app = self.getApp()
            if self.platform == 'xbmc':
                appid, version = self.prepareAddon(app)
                self.convertSkin(app)
            else:
                appid, version = self.prepareDescriptor(app)
            package = self.packageApp(app, appid, version, self.compile)
            shutil.rmtree(app)
            self.log.info("Build located here: %s" % (package))

    def isApp(self):
        for root, dirs, files in os.walk(self.path):
            if self.platform == 'xbmc':
                if "addon.xml" in files:
                    return True
            else:
                if "descriptor.xml" in files:
                    return True
        raise BuildAppException("Could not find descriptor.xml or addon.xml in path: %s" % (self.path), "BuildError")

    def getApp(self):
        self.log.info("Copying source to builddir: %s" % self.build_dir)
        tmpdir = os.path.join(self.build_dir, self.path)
        if os.path.exists(tmpdir): shutil.rmtree(tmpdir)
        shutil.copytree(self.path, tmpdir)
        return os.path.join(self.build_dir, os.path.basename(self.path))

    def prepareDescriptor(self, path, output = None):
        self.log.info("Preparing descriptor.xml at: %s" % path)
        try:
            doc = ET.parse(os.path.join(path, "descriptor.xml"))
        except Exception, e:
            raise BuildAppException("Could not parse descriptor.xml in %s" % path, e)
        modified = False
        if doc.getroot().findall(".//test-app"):
            for node in doc.getroot().findall(".//test-app"):
                doc.getroot().remove(node)
                modified = True
        appid = doc.getroot().find(".//id").text
        version = doc.getroot().find(".//version").text
        if modified:
            if output:
                self.log.debug("Writing new descriptor at: %s" % output)
                try:
                    doc.write(os.path.join(output, "descriptor.xml"))
                except Exception, e:
                    raise BuildAppException("Could not write to descriptor.xml at: %s" % output, e)
            else:
                self.log.debug("Writing new descriptor at: %s" % path)
                try:
                    doc.write(os.path.join(path, "descriptor.xml"))
                except Exception, e:
                    raise BuildAppException("Could not write to descriptor.xml at: %s" % path, e)

        self.log.info("BUILD NAVI-X FOR BOXEE")
        self.log.info("AppID: %s" % appid)
        self.log.info("Version: %s" % version)

        for root, dirs, files in os.walk(path):
            for filename in files:
                if '_xbmc' in filename:
                    try: os.remove(os.path.join(root, filename))
                    except: pass
        try:
            os.remove(os.path.join(path, 'icon.png'))
            os.remove(os.path.join(path, 'addon.xml'))
        except: pass

        return appid, version

    def prepareAddon(self, path, output = None):
        self.log.info("Reading addon.xml at: %s" % path)
        try:
            doc = ET.parse(os.path.join(path, "addon.xml"))
        except Exception, e:
            raise BuildAppException("Could not parse descriptor.xml in %s" % path, e)
        appid = doc.getroot().get("id")
        version = doc.getroot().get("version")
        self.log.info("BUILD NAVI-X FOR XBMC")
        self.log.info("AppID: %s" % appid)
        self.log.info("Version: %s" % version)
        
        self.log.info("Processing xbmc reorganisations: %s" % path)
        if os.path.isdir(os.path.join(path, 'resources')):
            os.makedirs(os.path.join(path, 'resources'))

        for item in os.listdir(path):
            if os.path.isdir(os.path.join(path, item)):
                shutil.move(os.path.join(path, item), os.path.join(path, 'resources', item))

        if os.path.isdir(os.path.join(path, 'resources', 'skin')):
            os.rename(  os.path.join(path, 'resources', 'skin'),  os.path.join(path, 'resources', 'skins')  )
        if os.path.isdir(os.path.join(path, 'resources', 'skins', 'Boxee Skin NG')):
            os.rename(  os.path.join(path, 'resources', 'skins', 'Boxee Skin NG'),  os.path.join(path, 'resources', 'skins', 'Default')  )

        for root, dirs, files in os.walk(path):
            for filename in files:
                if '_xbmc' in filename:
                    try: os.remove(os.path.join(root, filename.replace('_xbmc', '')))
                    except: pass
                    os.rename(  os.path.join(root, filename),  os.path.join(root, filename.replace('_xbmc', ''))  )

        try:
            os.remove(os.path.join(path, 'thumb.png'))
            os.remove(os.path.join(path, 'descriptor.xml'))
        except: pass

        return appid, version

    def convertSkin(self, path):
        template_path = os.path.join(__cwd__, 'build', 'window_template.build')
        template = self.readTemplate
        windowDir = os.path.join(path, 'resources', 'windows')
        xmlDir = os.path.join(path, 'resources', 'skins', 'Default', '720p')
        os.makedirs(windowDir)
        for root, dirs, files in os.walk(xmlDir):
            for filename in files:
                onclick, onaction = self.parseSkin(xmlDir, filename)
                window = self.insertTemplate(onclick, onaction, template(template_path))
                if 'dialog' in filename: window = window.replace('WindowXML', 'WindowXMLDialog')
                self.saveTemplate(windowDir, filename, window)

    def insertTemplate(self, onclick, onaction, template):
        indent = "    "
        t_onaction = ""
        t_onclick = ""
        if len(onaction) > 0:
            for item in onaction:
                action, id, text = item
                t_onaction = "".join([t_onaction, "%selif action.getId() == mc.%s and controlID == %s:\n" % (indent*2, action, id) ])
                t_onaction = "".join([t_onaction, self.readText(indent, text) ])
                t_onaction = "".join([t_onaction, "\n\n" ])

        if len(onclick) > 0:
            for item in onclick:
                action, id, text = item
                t_onclick = "".join([t_onclick, "%sif controlID ==  %s:\r\n" % (indent*2, id) ])
                t_onclick = "".join([t_onclick, self.readText(indent, text) ])
                t_onclick = "".join([t_onclick, "\r\n\r\n" ])


        template = template.replace('#|onaction|', t_onaction)
        template = template.replace('#|onclick|', t_onclick)
        return template

    def readText(self, indent, text):
        data = ""
        for line in text.readlines():
            if not line.strip():
                continue
            else:
                data = "".join([data, "%s%s" % (indent*3, line) ])
        text.close()
        return data

    def saveTemplate(self, root, filename, window):
        path = os.path.join(root, filename.replace('.xml','.py'))
        f = open(path, 'w')
        f.write(window)
        f.close()

    def readTemplate(self, path):
        f = open(path, 'r')
        data = f.read()
        f.close()
        return data


    def parseSkin(self, path, file):
        self.log.info("Preparing %s" % file)
        onclick = []
        onaction = []
        try:
            doc = ET.parse(os.path.join(path, file))
        except Exception, e:
            raise BuildAppException("Could not parse %s in %s" % (file, path), e)

        if doc.findall("//*[@lang='python']"):
            for node in doc.findall("//*[@lang='python']"):
                if node.tag in XBMC_ACTIONS.keys():
                    parent_id = node.getparent().get('id')
                    onaction.append( [ XBMC_ACTIONS[node.tag], parent_id, self.stream(node.text) ] )
                    node.getparent().remove(node)
                elif node.tag in ['onclick']:
                    if node.getparent().getparent().get('type') in ['list', 'wraplist', 'fixedlist', 'panel']:
                        parent_id = node.getparent().getparent().get('id')
                    else:
                        parent_id = node.getparent().get('id')
                    onclick.append( [node.tag, parent_id, self.stream(node.text)] )
                    par = node.getparent()
                    par.getparent().remove(par)

        if doc.findall("//font"):
            for node in doc.findall("//font"):
                if node.text in XBMC_FONTS.keys():
                    node.text = XBMC_FONTS[node.text]


        self.log.debug("Writing new skin file %s at: %s" % (file, path))
        try:
            doc.write(os.path.join(path, file))
        except Exception, e:
            raise BuildAppException("Could not write to %s at: %s" % (file, path), e)

        return onclick, onaction

    def stream(self, text):
        data = cStringIO.StringIO()
        data.write(text)
        data.seek(0)
        return data

    def packageApp(self, path, appid, version, compile=False):
        self.log.info("Packaging app: %s-%s" % (appid, version))
        if compile:
            self.log.info("Compiling Python modules...")
            compile = subprocess.Popen(["python2.4", "-O", "-m", "compileall", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            compile.wait()
        if os.path.exists(os.path.join(self.build_dir, appid)):
            self.log.debug("Temporary build directory matching appid exists: %s, deleting." % (os.path.join(self.build_dir, appid)))
            shutil.rmtree(os.path.join(self.build_dir, appid))
        shutil.copytree(path, os.path.join(self.build_dir, appid))
        zip = zipfile.ZipFile(self.build_dir + "/" + appid + "-" + version + ".zip", "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.build_dir + "/" + appid):
            if "git" not in root and "svn" not in root and "CVS" not in root and "tests" not in root:
                for file in files:
                    if "py" in file and "pyo" not in file and compile:
                        pass
                    else:
                        split = root.split(appid)
                        zip.write(os.path.join(root,file), os.path.join(appid, split[1][1:], file))
        zip.close()
        shutil.rmtree(os.path.join(self.build_dir, appid))
        return os.path.join(self.build_dir, appid + "-" + version + ".zip")

class BuildAppException(Exception):
    def __init__(self, message, e):
        Exception.__init__(self, message)
        self.log = logging.getLogger("Exception")
        self.log.addHandler(log_handler)
        self.logError(message, e)

    def logError(self, e, message):
        return self.log.critical("%s! %s" % (str(e), message))

def usage():
    print "Navi-X App Builder - " + str(VERSION)
    print "Usage: ",sys.argv[0]," [-i /path/to/app] [-c] [-h] [-d]"
    print "-i (--input): Required.  Path to the Navi app you wish to build."
    print "-p (--platform): Required.  Platform to deploy to [xbmc, boxee]."
    print "-c (--compile): Optional. Compiles all Python modules into .pyo files."
    print "-d (--debug): Optional. Turns on debug output."
    print "-h (--help): Optional.  Displays this message."


XBMC_ACTIONS = {
    "onleft"	: "ACTION_MOVE_LEFT",
    "onright"	: "ACTION_MOVE_RIGHT",
    "onup"	: "ACTION_MOVE_UP",
    "ondown"	: "ACTION_MOVE_DOWN",
}

XBMC_FONTS = {
    "font8" : "font10",
    "font8b" : "font10_title",
    "font10" : "font10",
    "font10b" : "font10_title",
    "font12" : "font10",
    "font12b" : "font10_title",
    "font13" : "font12",
    "font14" : "font12",
    "font14b" : "font12_title",
    "font16" : "font12",
    "font16b" : "font12_title",
    "font17" : "fontContextMenu",
    "font17b" : "fontContextMenu",
    "font18" : "fontContextMenu",
    "font18b" : "fontContextMenu",
    "font19" : "font13",
    "font19b" : "font13_title",
    "font20" : "font13",
    "font20b" : "font13_title",
    "font21" : "font13",
    "font21b" : "font13_title",
    "font22" : "font13",
    "font22b" : "font13_title",
    "font23" : "font24_title",
    "font23b" : "font24_title",
    "font24" : "font24_title",
    "font24b" : "font24_title",
    "font26" : "font28_title",
    "font26b" : "font28_title",
    "font28" : "font28_title",
    "font28b" : "font28_title",
    "font30" : "font30",
    "font30b" : "font30",
    "font32" : "font30",
    "font32b" : "font30",
    "font34" : "font35_title",
    "font34b" : "font35_title",
    "font36" : "font35_title",
    "font36b" : "font35_title",
    "font38" : "font35_title",
    "font38b" : "font35_title",
    "font40" : "font35_title",
    "font40b" : "font35_title",
    "font48" : "font35_title",
    "font48b" : "font35_title",
    "font56" : "WeatherTemp",
    "font56b" : "WeatherTemp",
    "font64" : "WeatherTemp",
    "font64b" : "WeatherTemp",
    "font80" : "WeatherTemp",
    "font80b" : "WeatherTemp"
}










if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:cd", ["help", "input=", "platform=", "compile", "debug"] )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    input = None
    compile = False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            logging.DEBUG
        elif opt in ("-i", "--input"):
            input = arg
        elif opt in ("-p", "--platform"):
            platform = arg
        elif opt in ("-c", "--compile"):
            compile = True
        else:
            assert False, "Unrecognized command line flag."

    if input and platform:
        if platform in ['boxee', 'xbmc']:
            if os.path.exists(input):
                if input[-1] == "/" or input[-1] == "/":
                    input = input[:-1]
                build = BuildApp(input, platform, compile)
                build.main()
            else:
                assert False, "Input directory %s does not exist!" % (input)
        else:
            assert False, "Wrong platform type! %s" % (platform)
    else:
        assert False, "Did not provide input directory or platform."


