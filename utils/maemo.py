"""
Module for maemo-specific stuff.
"""


_osso_context = None

IS_MAEMO = False
"""
this constant is C{True} when running on a maemo system
@since: 0.96
"""

IS_MER = False
"""
this constant is C{True} when running on a mer system
@since: 0.96.5
"""

try:
    import hildon
    IS_MAEMO = True
except:
    IS_MAEMO = False

import os

IS_MER = os.system("dpkg -l | grep maemo-launcher | grep mer") == 0



def set_osso_context(ctx):
    """
    Sets the OSSO context for the application. This function should only be
    used internally.
    @since: 0.96
    
    @param ctx: OSSO context
    """

    global _osso_context
    _osso_context = ctx
    
    
def get_osso_context():
    """
    Returns the OSSO context.
    @since: 0.96
    
    @return: OSSO context
    """

    return _osso_context
    
    
def get_device_state():
    """
    Returns the OSSO device state object.
    @since: 0.96.3
    
    @return: OSSO device state
    """
    
    import osso
    return osso.DeviceState(get_osso_context())



def get_system_bus():
    """
    Returns the DBus system bus.
    @since: 0.96
    
    @return: dbus system bus
    """

    return _system_bus
    

def get_session_bus():
    """
    Returns the DBus session bus.
    @since: 0.96
    
    @return: dbus session bus
    """

    return _session_bus
    

def get_product_code():
    """
    Returns the product code of the device.

     - Nokia 770:    SU-18
     - Nokia N800:   RX-34
     - Nokia N810:   RX-44
     - Nokia N810WE: RX-48
     - Unknown:      ?
    
    @since: 0.96
    
    @return: product code
    """
    
    # you can override the product code by setting the environment variable
    # MEDIABOX_MAEMO_DEVICE
    product = os.environ.get("MEDIABOX_MAEMO_DEVICE")
    
    if (not product):
        try:
            lines = open("/proc/component_version", "r").readlines()
        except:
            lines = []
            
        product = "?"
        for line in lines:
            line = line.strip()
            if (line.startswith("product")):
                parts = line.split()
                product = parts[1].strip()
                break
        #end for
    #end if

    return product


def request_connection():
    """
    If the device is not connected, tries to establish the default connection
    or pop up the connection dialog.
    Does nothing if the device does already have a network connection.
    @since: 0.96.3
    """
    
    # dbus-send --type=method_call --system --dest=com.nokia.icd/com/nokia/icd com.nokia.icd.connect
    # dbus-send --system --dest=com.nokia.icd /com/nokia/icd_ui com.nokia.icd_ui.disconnect boolean:true
    
    try:
        import conic
        conn = conic.Connection()
        conn.request_connection(conic.CONNECT_FLAG_NONE)
    except:
        pass



if (get_product_code() == "SU-18"):
    # bad hack!
    # work around broken D-Bus bindings on OS 2006; this breaks urllib2 for us,
    # but we don't use it anyway
    def _f(*args): raise RuntimeError("Ignore me...")
    import urllib2
    urllib2.AbstractHTTPHandler.do_open = _f
#end if

import dbus, dbus.glib
_system_bus = dbus.SystemBus(private = True)
_session_bus = dbus.SessionBus(private = True)

