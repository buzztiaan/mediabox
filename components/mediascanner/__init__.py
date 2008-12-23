

def get_classes():

    classes = []
    from MediaScanner import MediaScanner
    classes.append(MediaScanner)   

    from Prefs import Prefs
    classes.append(Prefs)
    
    try:
        from FileWatcher import FileWatcher
        classes.append(FileWatcher)
    except:
        pass
    
    return classes



messages = [
    "MEDIASCANNER_ACT_SCAN",             # (mediaroots, rebuild_index)
    "MEDIASCANNER_SVC_GET_MEDIA",        # (mimetypes: items, added, removed)

    "MEDIASCANNER_SVC_CREATE_THUMBNAIL", # (file, cb, *args)
    "MEDIASCANNER_SVC_GET_THUMBNAIL",    # (file: path, up_to_date)
    "MEDIASCANNER_SVC_SET_THUMBNAIL",    # (file, pbuf)    
    
    "MEDIASCANNER_EV_SCANNING_STARTED",
    "MEDIASCANNER_EV_SCANNING_FINISHED",
    "MEDIASCANNER_EV_SCANNING_PROGRESS", # (name)
]

