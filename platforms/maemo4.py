PLATFORM = "maemo4"

_osso_ctx = None


def create_osso_context(name, version, v):
    global _osso_ctx
    
    import osso
    _osso_ctx = osso.Context(name, version, v)


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


def get_device_state():
    """
    Returns the OSSO device state object.
    @since: 0.96.3
    
    @return: OSSO device state
    """
    
    import osso
    return osso.DeviceState(_osso_ctx)


def inhibit_screen_blanking():
    """
    Inhibits screen blanking. This function must be called repeatedly as long
    as blanking must not take place.
    """
    
    devstate = get_device_state()
    devstate.display_blanking_pause()
    

def get_product_code():
    """
    Returns the product code of the device.

     - Nokia 770:    SU-18
     - Nokia N800:   RX-34
     - Nokia N810:   RX-44
     - Nokia N810WE: RX-48
     - Nokia N900:   RX-51
     - Unknown:      ?
    
    @since: 0.96
    
    @return: product code
    """
    
    # you can override the product code by setting the environment variable
    # MEDIABOX_MAEMO_DEVICE
    import os
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


def plugin_execute(so_file):

    import osso
    plugin = osso.Plugin(_osso_ctx)
    plugin.plugin_execute(so_file, True)


if (get_product_code() == "SU-18"):
    # bad hack!
    # work around broken D-Bus bindings on OS 2006; this breaks urllib2 for us,
    # but we don't use it anyway
    def _f(*args): raise RuntimeError("Ignore me...")
    import urllib2
    urllib2.AbstractHTTPHandler.do_open = _f
#end if

import dbus, dbus.glib
_system_bus = dbus.SystemBus()
_session_bus = dbus.SessionBus()
