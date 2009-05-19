def get_classes():

    from PlaylistViewer import PlaylistViewer
    return [PlaylistViewer]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

