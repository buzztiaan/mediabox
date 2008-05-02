"""
This package contains the built-in graphics themes. Valid themes are detected
automatically.
"""

import gtk
import pango
import os

# versions of theme formats this release works with
_COMPATIBILITY = ["danube"]


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
                name, description, compat = _get_info(path)
                if (_is_compatible(compat)):
                    themes.append((d, preview, name, description))
        #end for
    #end for
        
    return themes


def _is_compatible(compat):

    for c in compat:
        if (c in _COMPATIBILITY):
            return True
    #end for
    return False


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

    name, description, compat = (os.path.basename(themepath), "", [])

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
        elif (line.startswith("compatible:")):
            idx = line.find(":")
            compat = line[idx + 1:].split()
    #end for
    
    return (name, description, compat)
        

    


def set_theme(name):

    theme_dir = _DEFAULT_THEME_DIR
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        theme_dir = os.path.join(themes_dir, name)
        name, description, compat = _get_info(theme_dir)
        if (os.path.exists(theme_dir) and _is_compatible(compat)):
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

    # read fonts and colors
    _read_fonts(theme_dir)
    _read_colors(theme_dir)


def _subregion(name, src, x, y, w, h):

    globals()[name] = src.subpixbuf(x, y, w, h)


set_theme("default")
