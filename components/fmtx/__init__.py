delayed = True

def get_classes():

    import platforms
    if (platforms.PLATFORM == platforms.MAEMO5):    
        from FMTX import FMTX
        #from FMTXDialog import FMTXDialog
        return [FMTX]
    else:
        return []

