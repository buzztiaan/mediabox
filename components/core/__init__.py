def get_classes():

    from AppWindow import AppWindow
    from IdleDetector import IdleDetector
    from Preferences import Preferences
    from ConfigBackend import ConfigBackend
    from ConfigTheme import ConfigTheme
    from DirectoryService import DirectoryService
    from MediaWidgetRegistry import MediaWidgetRegistry
    from NotificationService import NotificationService

    return [AppWindow, IdleDetector, Preferences, ConfigTheme, ConfigBackend,
            DirectoryService, MediaWidgetRegistry, NotificationService]
    
    
def get_devices():

    from LocalDevice import LocalDevice
    return [LocalDevice]
    
    
messages = [
    # Certain hardware keys generate events when pressed.
    #
    "HWKEY_EV_DECREMENT",
    "HWKEY_EV_INCREMENT",
    "HWKEY_EV_ENTER",
    "HWKEY_EV_FULLSCREEN",
    "HWKEY_EV_MENU",
    "HWKEY_EV_ESCAPE",
    "HWKEY_EV_EJECT",
    "HWKEY_EV_BACKSPACE",
    "HWKEY_EV_HEADSET",
    "HWKEY_EV_HEADSET_DOUBLE",
    "HWKEY_EV_HEADSET_TRIPLE",
    "HWKEY_EV_UP",
    "HWKEY_EV_DOWN",
    "HWKEY_EV_LEFT",
    "HWKEY_EV_RIGHT",
    "HWKEY_EV_KEY",             # (key)

    "CORE_EV_APP_STARTED",
    "CORE_EV_APP_SHUTDOWN",
    "CORE_EV_APP_IDLE_BEGIN",
    "CORE_EV_APP_IDLE_END",
    "CORE_EV_MAY_BLANK_DISPLAY",  # (value)
    
    # Notifications about adding or removing storage devices.
    #
    "CORE_EV_DEVICE_ADDED",     # (id, device)
    "CORE_EV_DEVICE_REMOVED",   # (id)
   
    "CORE_SVC_LIST_PATH",       # (path)
    "CORE_SVC_GET_FILE",        # (path)
    
    # Media actions control the currently playing media viewer.
    #
    "MEDIA_ACT_PLAY",
    "MEDIA_ACT_PAUSE",
    "MEDIA_ACT_STOP",
    "MEDIA_ACT_PREVIOUS",
    "MEDIA_ACT_NEXT",
    
    # Media events notify about player status.
    #
    "MEDIA_EV_LOADED",           # (viewer, f)
    "MEDIA_EV_PLAY",
    "MEDIA_EV_PAUSE",
    "MEDIA_EV_EOF",
    "MEDIA_EV_VOLUME_CHANGED",   # (volume)

    "COM_EV_COMPONENT_LOADED",  # (component)
    "COM_EV_LOADING_MODULE",    # (name)
    
    "CORE_ACT_RENDER_ALL",
    
    "CORE_ACT_SCAN_MEDIA",      # (force_rescan)
    "CORE_ACT_LOAD_ITEM",       # (item)
    "CORE_ACT_SCROLL_UP",
    "CORE_ACT_SCROLL_DOWN",
    "CORE_ACT_RENDER_ITEMS",
  
    "CORE_ACT_SET_TITLE",       # (title)
    "CORE_ACT_SET_INFO",        # (info)
    "CORE_ACT_SET_TOOLBAR",     # (toolbar_set)
    "CORE_ACT_SEARCH_ITEM",     # (key)
    
    "CORE_EV_THEME_CHANGED",

    # The media widget registry provides widgets for displaying media of a
    # certain MIME type.
    #
    "MEDIAWIDGETREGISTRY_SVC_GET_WIDGET",      # (caller_id, mimetype)
    
    # The notification service lets you show notifications to the user.
    #
    "NOTIFY_SVC_SHOW_INFO",      # (text)
    
    "UI_ACT_FREEZE",
    "UI_ACT_THAW",
    "UI_ACT_RENDER",

    "UI_ACT_VIEW_MODE",          # (mode)
    "UI_ACT_SHOW_MESSAGE",       # (text, subtext, icon)
    "UI_ACT_HIDE_MESSAGE",
    
    "UI_EV_VIEWER_CHANGED",      # (index)
    "UI_EV_DEVICE_SELECTED",     # (device_id)
       
    "UI_ACT_SET_STRIP",          # (viewer, items)
    "UI_ACT_HILIGHT_STRIP_ITEM", # (viewer, index)
    "UI_ACT_SELECT_STRIP_ITEM",  # (viewer, index)
    "UI_ACT_SHOW_STRIP_ITEM",    # (viewer, index)
    
    "UI_ACT_SELECT_VIEWER",      # (name)
    "UI_ACT_SELECT_DEVICE",      # (device_id)
]    

