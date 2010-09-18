def get_classes():

    from HTTPServer import HTTPServer
    return [HTTPServer]


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

