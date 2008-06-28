from Preferences import Preferences
from ConfigMediaRoot import ConfigMediaRoot
from ConfigTheme import ConfigTheme
from DirectoryService import DirectoryService


def get_classes():

    return [Preferences, ConfigMediaRoot, ConfigTheme, DirectoryService]
    
    
messages = [    
    "HWKEY_EV_DECREMENT",
    "HWKEY_EV_INCREMENT",
    "HWKEY_EV_ENTER",
    "HWKEY_EV_FULLSCREEN",
    "HWKEY_EV_HEADSET",

    "CORE_EV_APP_STARTED",
    "CORE_EV_APP_SHUTDOWN",
    "CORE_EV_MEDIA_SCANNING_FINISHED",  # (scanner)
    
    "CORE_EV_DEVICE_ADDED",     # (id, device)
    "CORE_EV_DEVICE_REMOVED",   # (id)
    
    "CORE_SVC_LIST_PATH",       # (path)
    "CORE_SVC_GET_FILE",        # (path)
    
    "MEDIA_EV_PLAY",
    "MEDIA_EV_PAUSE",
    "MEDIA_EV_EOF",
    
    "CORE_EV_VOLUME_CHANGED",   # (volume)

    "COM_EV_COMPONENT_LOADED",  # (component)
    
    "CORE_ACT_RENDER_ALL",
    "CORE_ACT_VIEW_MODE",       # (mode)    
    
    "CORE_ACT_SCAN_MEDIA",      # (force_rescan)
    "CORE_ACT_LOAD_ITEM",       # (item)
    "CORE_ACT_SELECT_ITEM",     # (index)
 
    "CORE_ACT_OPEN_URI",        # (uri)
    
    "CORE_ACT_SET_TITLE",       # (title)
    "CORE_ACT_SET_INFO",        # (info)
    "CORE_ACT_SET_COLLECTION",  # (collection)
    "CORE_ACT_SET_TOOLBAR",     # (toolbar_set)
    
    "CORE_EV_THEME_CHANGED",
]
