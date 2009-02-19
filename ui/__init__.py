"""
User Interface Classes
======================

This package contains user interface widgets and classes. The widget framework
is based on GDK.

@copyright: 2008
@author: Martin Grimme  <martin.grimme@lintegra.de>

@license: This package is licensed under the terms of the GNU LGPL.
"""


def try_rgba(w):

    import gtk
    screen = gtk.gdk.screen_get_default()
    try:
        have_rgba = screen.is_composited()
    except:
        have_rgba = False
        
    if (have_rgba):
        cmap = screen.get_rgba_colormap()
    else:
        cmap = screen.get_rgb_colormap()

    w.set_colormap(cmap)

