def get_classes():

    from AppWindow import AppWindow
    from Preferences import Preferences
    from ConfigTheme import ConfigTheme
    from DirectoryService import DirectoryService
    from MediaWidgetRegistry import MediaWidgetRegistry
    from NotificationService import NotificationService

    return [AppWindow, Preferences, ConfigTheme, DirectoryService,
            MediaWidgetRegistry, NotificationService]
    
    
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
    "HWKEY_EV_HEADSET",
    "HWKEY_EV_UP",
    "HWKEY_EV_DOWN",
    "HWKEY_EV_LEFT",
    "HWKEY_EV_RIGHT",

    "CORE_EV_APP_STARTED",
    "CORE_EV_APP_SHUTDOWN",
    #"CORE_EV_MEDIA_SCANNING_FINISHED",  # (scanner)
    
    # Notifications about adding or removing storage devices.
    #
    "CORE_EV_DEVICE_ADDED",     # (id, device)
    "CORE_EV_DEVICE_REMOVED",   # (id)

    #"CORE_EV_PANEL_CHANGED",    # (top_pbuf, bottom_pbuf)
    #"CORE_ACT_SHOW_MENU",
    
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
    
    "CORE_ACT_RENDER_ALL",
    "CORE_ACT_VIEW_MODE",       # (mode)    
    
    "CORE_ACT_SCAN_MEDIA",      # (force_rescan)
    "CORE_ACT_LOAD_ITEM",       # (item)
    "CORE_ACT_SELECT_ITEM",     # (index)
    "CORE_ACT_HILIGHT_ITEM",    # (index)
    "CORE_ACT_SCROLL_TO_ITEM",  # (index)
    "CORE_ACT_RENDER_ITEMS",
 
    "CORE_ACT_OPEN_URI",        # (uri)
    
    "CORE_ACT_SET_TITLE",       # (title)
    "CORE_ACT_SET_INFO",        # (info)
    "CORE_ACT_SET_COLLECTION",  # (collection)
    "CORE_ACT_SET_TOOLBAR",     # (toolbar_set)
    "CORE_ACT_SEARCH_ITEM",     # (key)
    
    "CORE_EV_THEME_CHANGED",

    # The media widget registry provides widgets for displaying media of a
    # certain MIME type.
    #
    "MEDIAWIDGETREGISTRY_SVC_GET_WIDGET",      # (caller_id, mimetype)
    
    # The notification service lets you show notifications to the user.
    #
    "NOTIFY_SVC_SHOW_INFO",     # (text)
    "NOTIFY_SVC_SHOW_PROGRESS", # (amount, total, text)
    
    "UI_ACT_FREEZE",
    "UI_ACT_THAW",
    "UI_ACT_RENDER",
    "UI_ACT_VIEW_MODE",         # (mode)
]    

