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
                name, description = _get_info(path)
                themes.append((d, preview, name, description))
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
            globals()[name] = colorname #gtk.gdk.color_parse(colorname)
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


def _get_info(themepath):

    name, description = (os.path.basename(themepath), "")

    try:
        lines = open(os.path.join(themepath, "info")).readlines()
    except:
        return (name, description)
        
    for line in lines:
        line = line.strip()
        if (not line or line.startswith("#")):
            continue
            
        elif (line.startswith("name:")):    
            idx = line.find(":")
            name = line[idx + 1:].strip()
        elif (line.startswith("description:")):
            idx = line.find(":")
            description = line[idx + 1:].strip()
    #end for
    
    return (name, description)
        

    


def set_theme(name):

    theme_dir = _DEFAULT_THEME_DIR
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        theme_dir = os.path.join(themes_dir, name)
        if (os.path.exists(theme_dir)):
            break
    #end for

    items = [ f for f in os.listdir(theme_dir)
              if f.endswith(".png") or f.endswith(".jpg") ]
    for i in items:
        name = os.path.splitext(i)[0]
        path = os.path.join(theme_dir, i)
        try:
            globals()[name] = gtk.gdk.pixbuf_new_from_file(path)
        except:
            pass
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
