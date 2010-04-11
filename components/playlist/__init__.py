delayed = True

def get_devices():

    from PlaylistDevice import PlaylistDevice
    return [PlaylistDevice]


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

