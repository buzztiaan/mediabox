from maemo4 import *

PLATFORM = "maemo5"


def request_fmradio():

    import dbus
    bus = get_system_bus()
    obj = bus.get_object("de.pycage.FMRXEnabler", "/de/pycage/FMRXEnabler")
    enabler = dbus.Interface(obj, "de.pycage.FMRXEnabler")
    retval, device = enabler.request()

    return (retval, device)

