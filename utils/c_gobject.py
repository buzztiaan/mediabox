import ctypes
import gobject


# GObject wrapping code adapted from
# http://faq.pygtk.org/index.py?req=show&file=faq23.041.htp

class _PyGObject_Functions(ctypes.Structure):

    _fields_ = [
        ('register_class',
         ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p,
                           ctypes.c_int, ctypes.py_object,
                           ctypes.py_object)),
        ('register_wrapper',
         ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.py_object)),
        ('register_sinkfunc',
         ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.c_void_p)),
        ('lookupclass',
         ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.c_int)),
        ('newgobj',
         ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.c_void_p)),
        ]

class _PyGObjectCPAI(object):

    def __init__(self):
    
        addr = ctypes.pythonapi.PyCObject_AsVoidPtr(
            ctypes.py_object(gobject._PyGObject_API))
        self._api = _PyGObject_Functions.from_address(addr)

    def pygobject_new(self, addr):
    
        return self._api.newgobj(addr)


_capi = _PyGObjectCPAI()


def wrap(obj):
    """
    Takes a ctypes pointer to a GObject and returns a PyGObject.
    
    @param obj: GObject to wrap
    @return: GObject wrapped as PyGObject
    """

    return _capi.pygobject_new(obj)

