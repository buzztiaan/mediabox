import platforms

def get_classes():
    
    classes = []

    from ConfigBackend import ConfigBackend
    classes.append(ConfigBackend)

    from ConfigTheme import ConfigTheme
    classes.append(ConfigTheme)

    return classes


def get_devices():

    from PrefsDevice import PrefsDevice
    return [PrefsDevice]
