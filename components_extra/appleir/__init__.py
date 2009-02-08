def _has_apple_remote():

    from utils import maemo
    if (maemo.get_product_code() == "?"):
        mods = open("/proc/modules", "r").read()
        return "appleir" in mods
    else:
        return False
    

def get_classes():
    
    # do we have an AppleRemote?
    if (_has_apple_remote()):
        from AppleIR import AppleIR
        return [AppleIR]
    else:
        return []

