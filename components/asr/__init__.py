delayed = True

def get_classes():

    import platforms
    
    classes = []
    
    if (platforms.MAEMO4 or platforms.MAEMO5):
        from RotationPrefs import RotationPrefs
        classes.append(RotationPrefs)

    if (platforms.MAEMO5):
        from RotationMonitor import RotationMonitor
        classes.append(RotationMonitor)
    #end if
    
    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

