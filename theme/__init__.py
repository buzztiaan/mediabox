"""
Theming
=======

This package contains the built-in graphics themes. Valid themes are detected
automatically.
"""

from Color import Color
from mediabox import values

import gtk
import pango
import os


_THEMES_DIR = os.path.dirname(__file__)
_USER_THEMES_DIR = os.path.join(values.USER_DIR, "themes")
_DEFAULT_THEME_DIR = os.path.join(_THEMES_DIR, "default")
os.system("mkdir -p " + _USER_THEMES_DIR)



def list_themes():
    """
    Lists the available themes.
    
    @return: list of (theme_path, preview_icon_path, name, description, author)
             tuples
    """

    themes = []
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        try:        
            files = os.listdir(themes_dir)
        except:
            continue
        #files.sort()
        
        for d in files:
            path = os.path.join(themes_dir, d)
            if (os.path.isdir(path) and not d.startswith(".")):
                preview = os.path.join(path, "PREVIEW.png")
                name, description, author = _get_info(path)
                themes.append((d, preview, name, description, author))
        #end for
    #end for
        
    themes.sort(lambda a,b:cmp(a[2],b[2]))
    return themes



def _read_definitions(themepath):

    def_files = [ f for f in os.listdir(themepath) if f.endswith(".def") ]
    for f in def_files:
        try:
            _read_def_file(os.path.join(themepath, f))
        except:
            pass
            

def _read_def_file(f):

    lines = open(f).readlines()
        
    for line in lines:
        line = line.strip()
        if (not line or line.startswith("#")):
            continue

        idx = line.find(":")
        name = line[:idx].strip()
        
        if (name.startswith("color_")):
            colorname = line[idx + 1:].strip()

            if (name in globals()):
                globals()[name].set_color(colorname)
            else:
                globals()[name] = Color(colorname)
                
        elif (name.startswith("font_")):
            fontname = line[idx + 1:].strip()
            try:
                font = pango.FontDescription(fontname)
            except:
                pass
            else:
                if (name in globals()):
                    globals()[name].merge(font, True)
                else:
                    globals()[name] = font
    #end for            
            
    

def _get_info(themepath):

    name, description, author = (os.path.basename(themepath), "", "")

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
        elif (line.startswith("author:")):
            idx = line.find(":")
            author = line[idx + 1:].strip()
    #end for
    
    return (name, description, author)
        

def set_theme(name):
    """
    Changes the current theme.
    
    @param name: name of new theme
    """

    _set_theme("default")
    _set_theme(name)


def _set_theme(name):

    theme_dir = _DEFAULT_THEME_DIR
    for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
        theme_dir = os.path.join(themes_dir, name)
        name, description, author = _get_info(theme_dir)
        if (os.path.exists(theme_dir)):
            break
    #end for

    items = [ f for f in os.listdir(theme_dir)
              if f.endswith(".png") or f.endswith(".jpg") ]
    for i in items:
        name = os.path.splitext(i)[0]
        path = os.path.join(theme_dir, i)
        try:
            pbuf = gtk.gdk.pixbuf_new_from_file(path)
            #globals()[name] = gtk.gdk.pixbuf_new_from_file(path)
        except:
            continue
        else:
            if (name in globals()):
                globals()[name].fill(0x00000000)
                pbuf.scale(globals()[name], 0, 0,
                           pbuf.get_width(), pbuf.get_height(), 0, 0, 1, 1,
                           gtk.gdk.INTERP_NEAREST)
            else:
                globals()[name] = pbuf
            del pbuf
    #end for

    # read fonts and colors
    _read_definitions(theme_dir)


_set_theme("default")
