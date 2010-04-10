def get_classes():

    from SSDPMonitor import SSDPMonitor
    return [SSDPMonitor]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

