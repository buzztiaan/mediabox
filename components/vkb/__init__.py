def get_classes():

    from VirtualKeyboard import VirtualKeyboard
    return [VirtualKeyboard]
    
    
    
import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

