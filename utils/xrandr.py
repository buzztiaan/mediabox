import ctypes
import os

NORMAL = 1
LEFT = 2
INVERTED = 4
RIGHT = 8

_xlib = ctypes.CDLL("libX11.so.6")
_xrandr = ctypes.CDLL("libXrandr.so.2")
_rr = _xrandr

class _XRRScreenConfiguration(ctypes.Structure): pass


def set_orientation(orientation):

    display = _xlib.XOpenDisplay(os.getenv("DISPLAY"))
    screen = _xlib.XDefaultScreen(display)
    root = _xlib.XDefaultRootWindow(display, screen)

    gsi = _rr.XRRGetScreenInfo
    gsi.restype = ctypes.POINTER(_XRRScreenConfiguration)
    config = gsi(display, root)

    current_time = ctypes.c_ulong()
    _rr.XRRTimes.restype = ctypes.c_ulong
    timestamp = _rr.XRRTimes(display, screen, ctypes.byref(current_time))

    xccr = _rr.XRRConfigCurrentRate
    xccr.restype = ctypes.c_int
    rate = xccr(config)

    rotation = ctypes.c_ushort()
    size = _rr.XRRConfigCurrentConfiguration(config, ctypes.byref(rotation))


    _rr.XRRSetScreenConfigAndRate(display, config, root, size,
                                  orientation, rate, timestamp)

