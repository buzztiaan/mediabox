"""
This package contains the built-in graphics themes. Valid themes are detected
automatically.
"""

import gtk
import pango
import os


_THEMES_DIR = os.path.dirname(__file__)
_USER_THEMES_DIR = os.path.expanduser("~/.mediabox/themes")
_DEFAULT_THEME_DIR = os.path.join(_THEMES_DIR, "default")
os.system("mkdir -p " + _USER_THEMES_DIR)



def list_themes():

    themes = []
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        try:        
            files = os.listdir(themes_dir)
        except:
            continue
        files.sort()
        
        for d in files:
            path = os.path.join(themes_dir, d)
            if (os.path.isdir(path) and not d.startswith(".")):
                preview = os.path.join(path, "PREVIEW.png")
                themes.append((d, preview))
        #end for
    #end for
        
    return themes



def _read_colors(themepath):

    try:
        lines = open(os.path.join(themepath, "colors")).readlines()
    except:
        lines = open(os.path.join(_DEFAULT_THEME_DIR, "colors")).readlines()
        
    for line in lines:
        line = line.strip()
        if (not line or line.startswith("#")):
            continue

        idx = line.find(":")
        name = line[:idx].strip()
        colorname = line[idx + 1:].strip()
        try:
            globals()[name] = gtk.gdk.color_parse(colorname)
        except:
            pass
    #end for
    
    
def _read_fonts(themepath):

    try:
        lines = open(os.path.join(themepath, "fonts")).readlines()
    except:
        lines = open(os.path.join(_DEFAULT_THEME_DIR, "fonts")).readlines()
        
    for line in lines:
        line = line.strip()
        if (not line or line.startswith("#")):
            continue

        idx = line.find(":")
        name = line[:idx].strip()
        fontname = line[idx + 1:].strip()
        try:
            globals()[name] = pango.FontDescription(fontname)
        except:
            pass
    #end for


    


def set_theme(name):

    theme_dir = _DEFAULT_THEME_DIR
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        theme_dir = os.path.join(themes_dir, name)
        if (os.path.exists(theme_dir)):
            break
    #end for

    items = [ os.path.splitext(f)[0] for f in os.listdir(theme_dir)
              if os.path.splitext(f)[1] == ".png" ]

    for i in items:
        path = os.path.join(theme_dir, i + ".png")
        try:
            globals()[i] = gtk.gdk.pixbuf_new_from_file(path)    
        except:
            path = os.path.join(_DEFAULT_THEME_DIR, i + ".png")
            globals()[i] = gtk.gdk.pixbuf_new_from_file(path)    
    #end for

    # define some subregions
    _subregion("panel_bg", panel, 20, 0, 760, 80)
    _subregion("panel_button_bg", panel, 20, 0, 80, 80)

    # read fonts and colors
    _read_fonts(theme_dir)
    _read_colors(theme_dir)


def _subregion(name, src, x, y, w, h):

    globals()[name] = src.subpixbuf(x, y, w, h)


set_theme("default")
