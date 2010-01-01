def get_classes():

    from FileIndex import FileIndex
    from FileUndertaker import FileUndertaker
    from FileScannerPrefs import FileScannerPrefs

    classes = [FileIndex,
               FileUndertaker,
               FileScannerPrefs]

    import os
    if (os.path.exists("/usr/bin/tracker-files")):
        from TrackerScanner import TrackerScanner
        classes.append(TrackerScanner)

    else:
        from SimpleScanner import SimpleScanner
        classes.append(SimpleScanner)


    return classes
    

import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

