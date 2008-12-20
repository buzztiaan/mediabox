"""
Theming
=======

This package contains the built-in graphics themes. Valid themes are detected
automatically.
"""

from Color import Color
from Font import Font
from Pixbuf import Pixbuf
from mediabox import values
from utils import logging

import gtk
import pango
import os


_THEMES_DIR = os.path.dirname(__file__)
_USER_THEMES_DIR = os.path.join(values.USER_DIR, "themes")
_DEFAULT_THEME_DIR = os.path.join(_THEMES_DIR, "default")
os.system("mkdir -p " + _USER_THEMES_DIR)


_TYPE_PBUF = 0
_TYPE_COLOR = 1
_TYPE_FONT = 2


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




class _Theme(object):

    def __init__(self):

        # table: name -> (type, definition, obj)
        self.__objects = {}


    def __getattr__(self, name):
    
        if (name in self.__objects):
            objtype, objdef, obj = self.__objects[name]
            if (not obj):
                obj = self.__load_object(objtype, objdef)
                self.__objects[name] = (objtype, objdef, obj)
            #end if
            return obj

        else:
            logging.error("theme item not found: %s", name)
            raise AttributeError(name)


    def list_themes(self):
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



    def set_theme(self, name):
        """
        Changes the current theme.
        
        @param name: name of new theme
        """

        self.__set_theme("default")
        if (name != "default"):
            self.__set_theme(name)



    def __set_theme(self, name):

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

            if (name in self.__objects):
                nil, nil, obj = self.__objects[name]
            else:
                obj = None

            self.__objects[name] = (_TYPE_PBUF, path, obj)
            if (obj): obj.set_objdef(path)
        #end for
        
        self.__read_definitions(theme_dir)


    def __read_definitions(self, themepath):

        def_files = [ f for f in os.listdir(themepath) if f.endswith(".def") ]
        for f in def_files:
            try:
                self.__read_def_file(os.path.join(themepath, f))
            except:
                pass
        #end for



    def __read_def_file(self, f):

        lines = open(f).readlines()
            
        for line in lines:
            line = line.strip()
            if (not line or line.startswith("#")):
                continue

            idx = line.find(":")
            name = line[:idx].strip()

            if (name in self.__objects):
                nil, nil, obj = self.__objects[name]
            else:
                obj = None
            
            if (name.startswith("color_")):
                colorname = line[idx + 1:].strip()
                self.__objects[name] = (_TYPE_COLOR, colorname, obj)
                if (obj): obj.set_objdef(colorname)

            elif (name.startswith("font_")):
                fontname = line[idx + 1:].strip()
                self.__objects[name] = (_TYPE_FONT, fontname, obj)        
                if (obj): obj.set_objdef(fontname)
            

    def __load_object(self, objtype, objdef):
    
        logging.debug("loading theme item: %s", objdef)
        
        if (objtype == _TYPE_PBUF):
            obj = Pixbuf(objdef)
                           
        elif (objtype == _TYPE_COLOR):
            obj = Color(objdef)

        elif (objtype == _TYPE_FONT):
            obj = Font(objdef)
            
        else:
            obj = None
        
        return obj



theme = _Theme()
theme.set_theme("default")

