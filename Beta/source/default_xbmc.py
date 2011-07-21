import os
import sys

# SET APP WIDE GLOBAL VARS
CWD             = os.getcwd().replace(";","")
ROOT            = os.path.join(CWD, 'resources')
PLATFORM        = "xbmc"
WINDOWS_ID      = {
                        'main':15000, 'dialog-wait':15100, 'dialog-splash':15110, 'dialog-info':15120, 'dialog-search-history':15140,
                        'dialog-search-options':15150, 'dialog-text':15160, 'dialog-subtitle':15170, 'dialog-settings':15190, 'dialog-options':15200
                }
WINDOWS_STACK   =   []

sys.path.append(os.path.join(ROOT, 'libs'))
sys.path.append(os.path.join(ROOT, 'external'))

import mc

# Init App
if ( __name__ == "__main__" ):
    mc.ActivateWindow(15110)
    mc.ActivateWindow(15100)
    mc.ActivateWindow(15000)

    import navi

    if len(mc.GetWindow(15000).GetList(60).GetItems()) < 1:
        app = navi.Navi_APP()
    else:
        app.api.download.active = False
        app.gui.HideDialog('wait')
    app.gui.HideDialog('splash')

