import platforms


def get_classes():

    from FileIndex import FileIndex
    from FileUndertaker import FileUndertaker
    from FileScannerPrefs import FileScannerPrefs

    classes = [FileIndex,
               FileUndertaker,
               FileScannerPrefs]

    if (platforms.MAEMO5):
        from TrackerScanner import TrackerScanner
        classes.append(TrackerScanner)

        from DCIMScanner import DCIMScanner
        classes.append(DCIMScanner)

    if (platforms.MAEMO4):
        from MetalayerScanner import MetalayerScanner
        classes.append(MetalayerScanner)

    from SimpleScanner import SimpleScanner
    classes.append(SimpleScanner)

    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

