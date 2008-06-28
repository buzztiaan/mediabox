from MediaScanner import MediaScanner


def get_classes():

    return [MediaScanner]
    
    
messages = [
    "MEDIASCANNER_ACT_SCAN",             # (mediaroots)
    "MEDIASCANNER_SVC_GET_MEDIA",        # (mimetypes)
    "MEDIASCANNER_SVC_GET_THUMBNAIL",    # (file: path)
    
    "MEDIASCANNER_EV_SCANNING_STARTED",
    "MEDIASCANNER_EV_SCANNING_FINISHED",
    "MEDIASCANNER_EV_THUMBNAIL_GENERATED",  # (thumburi, name)
]
