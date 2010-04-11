delayed = True

def get_classes():

    from CoverStore import CoverStore
    return [CoverStore]
    

import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

