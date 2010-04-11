delayed = True

def get_classes():

    #from Preferences import Preferences
    #from ConfigBackend import ConfigBackend
    from ConfigTheme import ConfigTheme

    return [ConfigTheme] #ConfigBackend]


def get_devices():

    from PrefsDevice import PrefsDevice
    return [PrefsDevice]
