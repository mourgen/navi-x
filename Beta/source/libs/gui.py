from default import *
from tools import *

#Module specific Imports
try: import cPickle as pickle
except: import pickle

######
### GUI
######
### All Gui functions are called in this section, this makes porting the app more easy
######

### Main gui functions
class GUI:
    def __init__(self, **kwarg):
        self.windows = WINDOWS_ID
        self.id = kwarg.get('window',False)
        
        if kwarg.get('window',False):   self.window = mc.GetWindow(kwarg['window'])
        if kwarg.get('listid',False):   self.list = self.window.GetList(kwarg['listid'])
        if kwarg.get('window',False):   self.focus = self.window.GetControl(2000).SetFocus
        
    def SetVisible(self, id, bool):
        control = self.window.GetControl(id)
        control.SetVisible(bool)

    def ClearLists(self, lists):
        for id in lists:
            list = self.window.GetList(id)
            list.SetItems(mc.ListItems())

    def SetTexture(self, id, texture):
        self.window.GetImage(id).SetTexture(str(texture))

    def SetLabel(self, id, label):
        self.window.GetLabel(id).SetLabel(str(label))

    def SetButton(self, id, label):
        self.window.GetButton(id).SetLabel(str(label))

    def SetFocus(self, id):
        self.window.GetControl(id).SetFocus()

    def SetEnabled(self, id, bool):
        self.window.GetControl(id).SetEnabled(bool)

    def SetFocusedItem(self, list, id):
        _list = self.window.GetList(list)
        _list.SetFocusedItem(id)

    def PushState(self):
        self.window.PushState()
    
    def ClearStateStack(self, bool):
        self.window.ClearStateStack(bool)

    def GetInfoString(self, string):
        return mc.GetInfoString(string)
        
    def ShowDialog(self, id):
        mc.ActivateWindow(self.windows[id])

    def HideDialog(self, id):
        xbmc.executebuiltin("Dialog.Close(" + str(self.windows[id]) + ")")

    def ShowDialogConfirm(self, *args):
        return mc.ShowDialogConfirm(*args)

    def ShowDialogNotification(self, msg):
        mc.ShowDialogNotification(msg)

    def ShowDialogKeyboard(self, *args):
        return mc.ShowDialogKeyboard(*args)

    def ShowDialogNumeric(self, *args):
        import xbmcgui
        dialog = xbmcgui.Dialog()
        return dialog.numeric(*args)

    def ShowDialogBrowse(self, *args):
        import xbmcgui
        dialog = xbmcgui.Dialog()
        return dialog.browse(*args)

    def ShowDialogOk(self, *args):
        args = (str(r) for r in args)
        return mc.ShowDialogOk(*args)

### Create list from object and sets to gui
class createList:
    def __init__(self, items):
        self.listItems = mc.ListItems()
        if len(items) > 0: self._createItems(items)

    def _createItems(self, items):
        for item in items:
            listItem = self._createItem(item)
            self.listItems.append(listItem)

    def _createItem(self, dict, type=mc.ListItem.MEDIA_UNKNOWN):
        listItem = mc.ListItem(type)
        try:
            listItem.SetLabel(checkUTF8(dict['label']))
            del dict['label']
        except: pass
        try:
            listItem.SetPath(str(dict['path']))
            del dict['path']
        except: pass
        try:
            listItem.SetProperty('label2', checkUTF8(dict['label2']))
            del dict['label']
        except: pass
        try:
            listItem.SetProperty('description', checkUTF8(dict['description']))
            del dict['label']
        except: pass
        try:
            listItem.SetProperty('handle', pickle.dumps(dict['handle'], pickle.HIGHEST_PROTOCOL))
            del dict['handle']
        except: pass
        try:
            listItem.SetThumbnail(str(dict['thumb']))
            del dict['thumb']
        except: pass
        try:
            listItem.SetContentType(str(dict['SetContentType']))
            del dict['SetContentType']
        except: pass
        #
        if not isinstance(dict, str):
            for key in dict.keys():
                try: listItem.SetProperty(str(key), dict[key])
                except: pass
        return listItem

    def _set(self, gui):
        gui.list.SetItems(self.listItems)
        if gui.id == gui.windows['main']: gui.focus()
