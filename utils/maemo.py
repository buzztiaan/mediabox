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
_system_bus = dbus.SystemBus()
_session_bus = dbus.SessionBus()


def set_osso_context(ctx):

    global _osso_context
    _osso_context = ctx
    
    
def get_osso_context():

    return _osso_context


def get_system_bus():

    return _system_bus
    

def get_session_bus():

    return _session_bus
    

def get_product_code():
    """
    Returns the product code.
    Nokia 770:  SU-18
    Nokia N800: RX-34
    Nokia N810: RX-44
    Unknown:    ?
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

