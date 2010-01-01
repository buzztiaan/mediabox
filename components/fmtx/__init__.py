import platforms


def get_classes():

    if (platforms.PLATFORM == platforms.MAEMO5):    
        from FMTX import FMTX
        #from FMTXDialog import FMTXDialog
        return [FMTX]
    else:
        return []

