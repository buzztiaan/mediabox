"""
Module for maemo-specific stuff.
"""


_osso_context = None


try:
    import hildon
    IS_MAEMO = True
except:
    IS_MAEMO = False

import dbus, dbus.glib
_system_bus = dbus.SystemBus(private = True)
_session_bus = dbus.SessionBus(private = True)


def set_osso_context(ctx):
    """
    Sets the OSSO context for the application.
    
    @param ctx: OSSO context
    """

    global _osso_context
    _osso_context = ctx
    
    
def get_osso_context():
    """
    Returns the OSSO context.
    
    @return: OSSO context
    """

    return _osso_context


def get_system_bus():
    """
    Returns the DBus system bus.
    
    @return: dbus system bus
    """

    return _system_bus
    

def get_session_bus():
    """
    Returns the DBus session bus.
    
    @return: dbus session bus
    """

    return _session_bus
    

def get_product_code():
    """
    Returns the product code of the system.

     - Nokia 770:    SU-18
     - Nokia N800:   RX-34
     - Nokia N810:   RX-44
     - Nokia N810WE: RX-48
     - Unknown:      ?
    
    @return: product code
    """
    
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
    
    return product

