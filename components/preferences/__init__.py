def get_classes():

    from ConfigBackend import ConfigBackend
    from ConfigTheme import ConfigTheme

    return [ConfigTheme,
            ConfigBackend]


def get_devices():

    from PrefsDevice import PrefsDevice
    return [PrefsDevice]
