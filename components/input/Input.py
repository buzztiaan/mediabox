from com import Component, msgs
from InputSchema import InputSchema
import keymap
from utils import maemo

import os

if (maemo.get_product_code() != "?"):
    _SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "maemo.input")
else:
    _SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "htpc.input")

_HW_KEYS = [ getattr(msgs, key) for key in dir(msgs)
             if key.startswith("HWKEY_EV_") ]

_CONTEXTS = [ getattr(msgs, key) for key in dir(msgs)
              if key.startswith("INPUT_EV_CONTEXT_") ]



class Input(Component):
    """
    Component for mapping hardware keys to input events according to a given
    input schema.
    """

    def __init__(self):
    
        self.__schema = InputSchema(open(_SCHEMA_FILE).read())
    
    
        Component.__init__(self)


    def handle_INPUT_SVC_SEND_KEY(self, keycode, pressed):
        """
        Accepts a key code and emits the appropriate INPUT event according to
        the current context. This is the preferred method of handling hardware
        keys.
        @since: 0.97
        
        @param keycode: key code string
        @param pressed: (reserved for future use; must be C{True} for now)
        """
        
        hwkey = keymap.get(keycode)
        if (pressed):
            if (hwkey):
                self.__schema.send_key(hwkey)
                event = self.__schema.get_event()
                if (event):
                    self.emit_message(event)
            elif (len(keycode) == 1 and ord(keycode) > 31):      
                self.emit_message(msgs.HWKEY_EV_KEY, keycode)
        #end if

        
    def handle_message(self, msg, *args):
    
        if (msg in _HW_KEYS):
            self.__schema.send_key(msg)
            event = self.__schema.get_event()
            if (event):
                self.emit_message(event)

        elif (msg in _CONTEXTS):
            print "CONTEXT", msgs._id_to_name(msg)
            self.__schema.set_context(msg)
