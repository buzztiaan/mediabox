def get_classes():

    classes = []
    from MediaScanner import MediaScanner
    from Thumbnailer import Thumbnailer
    classes.append(MediaScanner)
    classes.append(Thumbnailer)

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

    "MEDIASCANNER_SVC_LOAD_THUMBNAIL",    # (file, cb, *args)
    "MEDIASCANNER_SVC_COPY_THUMBNAIL",    # (file1, file2)    

    "MEDIASCANNER_SVC_GET_THUMBNAIL",    # DEPRECATED (file: path, up_to_date)
    "MEDIASCANNER_SVC_SET_THUMBNAIL",    # DEPRECATED (file, pbuf)    
    
    "MEDIASCANNER_EV_SCANNING_STARTED",
    "MEDIASCANNER_EV_SCANNING_FINISHED",
    "MEDIASCANNER_EV_SCANNING_PROGRESS", # (name)
]

