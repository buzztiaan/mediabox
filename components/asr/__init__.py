import platforms

def get_classes():

    classes = []

    if (platforms.PLATFORM == platforms.MAEMO5):
        from RotationMonitor import RotationMonitor
        #classes.append(RotationMonitor)
    #end if
    
    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

