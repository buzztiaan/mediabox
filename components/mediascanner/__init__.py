def get_classes():

    classes = []
    from MediaScanner import MediaScanner
    from Tracker import Tracker
    from Thumbnailer import Thumbnailer
    #classes.append(MediaScanner)
    classes.append(Tracker)
    classes.append(Thumbnailer)

    from Prefs import Prefs
    classes.append(Prefs)
    
    try:
        from FileWatcher import FileWatcher
        classes.append(FileWatcher)
    except:
        pass
    
    return classes



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

