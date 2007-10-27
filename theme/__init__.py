"""
This package contains the available graphics themes. Valid themes are detected
automatically.
"""

import gtk
import pango
import os


_THEMES_DIR = os.path.dirname(__file__)


# TODO: make these themable, too
font_plain = pango.FontDescription("Nokia Sans 18")
font_tiny = pango.FontDescription("Nokia Sans Cn 8")
panel_foreground = gtk.gdk.color_parse("#ffffff")
item_foreground = gtk.gdk.color_parse("#444466")


def list_themes():

    themes = []
    for d in os.listdir(_THEMES_DIR):
        path = os.path.join(_THEMES_DIR, d)
        if (os.path.isdir(path)):
            preview = os.path.join(path, "PREVIEW.png")
            themes.append((d, preview))
    #end for
        
    return themes


def set_theme(name):

    theme_dir = os.path.join(_THEMES_DIR, name)
    items = [ os.path.splitext(f)[0] for f in os.listdir(theme_dir)
              if os.path.splitext(f)[1] == ".png" ]

    for i in items:
        path = os.path.join(_THEMES_DIR, name, i + ".png")
        try:
            globals()[i] = gtk.gdk.pixbuf_new_from_file(path)    
        except:
            path = os.path.join(_THEMES_DIR, "default", i + ".png")
            globals()[i] = gtk.gdk.pixbuf_new_from_file(path)    
    #end for


set_theme("default")
