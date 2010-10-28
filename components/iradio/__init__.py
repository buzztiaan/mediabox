def get_classes():

    from IRadioThumbnailer import IRadioThumbnailer
    return [IRadioThumbnailer]


def get_devices():

    from IRadioDevice import IRadioDevice
    return [IRadioDevice]


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

