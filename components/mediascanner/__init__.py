from MediaScanner import MediaScanner


def get_classes():

    return [MediaScanner]
    
    
messages = [
    "MEDIASCANNER_ACT_SCAN",             # (mediaroots)
    "MEDIASCANNER_SVC_GET_MEDIA",        # (mimetypes: items, added, removed)

    "MEDIASCANNER_SVC_CREATE_THUMBNAIL", # (file, cb, *args)
    "MEDIASCANNER_SVC_GET_THUMBNAIL",    # (file: path)
    "MEDIASCANNER_SVC_SET_THUMBNAIL",    # (file, pbuf)
    
    "MEDIASCANNER_EV_SCANNING_STARTED",
    "MEDIASCANNER_EV_SCANNING_FINISHED",
    "MEDIASCANNER_EV_SCANNING_PROGRESS", # (name)
]

