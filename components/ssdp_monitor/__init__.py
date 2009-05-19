from SSDPMonitor import SSDPMonitor


def get_classes():

    return [SSDPMonitor]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

