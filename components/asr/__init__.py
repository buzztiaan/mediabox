def get_classes():

    import platforms
    classes = []

    if (platforms.MAEMO5):
        from RotationMonitor import RotationMonitor
        from RotationPrefs import RotationPrefs
        classes.append(RotationMonitor)
        classes.append(RotationPrefs)
    #end if
    
    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

