def get_devices():

    #from PlaylistViewer import PlaylistViewer
    from PlaylistDevice import PlaylistDevice
    return [PlaylistDevice] #PlaylistViewer]


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

