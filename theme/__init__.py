"""
Theming
=======

Package for theming.
Themes are subdirectories in this package and are detected automatically.

Import the C{theme} object from this package for accessing the elements of
the current theme by name::

  from theme import theme
  
  ...
  
  icon = theme.foo_icon

@since: 0.96
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
    info = {
       "name": os.path.basename(themepath),
       "description": "",
       "author": "",
       "inherits": "default"
    }

    try:
        lines = open(os.path.join(themepath, "info")).readlines()
    except:
        import traceback; traceback.print_exc()
        return info
        
    for line in lines:
        line = line.strip()
        if (not line or line.startswith("#")):
            continue
            
        idx = line.find(":")
        key = line[:idx].strip()
        value = line[idx + 1:].strip()
        info[key] = value
    #end for
    
    return info




class _Theme(object):
    """
    Singleton class for loading themes.
    @since: 0.96
    """

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
        @since: 0.96
        
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
                    info = _get_info(path)
                    themes.append((d, preview, info["name"],
                                               info["description"],
                                               info["author"]))
            #end for
        #end for
            
        themes.sort(lambda a,b:cmp(a[2],b[2]))
        return themes



    def set_theme(self, name):
        """
        Changes the current theme.
        @since: 0.96
        
        @param name: name of new theme
        """

        self.__set_theme(name)


    def __set_theme(self, name):

        theme_dir = _DEFAULT_THEME_DIR
        for themes_dir in [_THEMES_DIR, _USER_THEMES_DIR]:
            theme_dir = os.path.join(themes_dir, name)            
            if (os.path.exists(theme_dir)):
                break
        #end for
        
        info = _get_info(theme_dir)
        if (name != "default"):
            self.__set_theme(info["inherits"])
        
        self.__load_recursively(theme_dir)
        

    def __load_recursively(self, theme_dir):
    
        for i in os.listdir(theme_dir):
            name = os.path.splitext(i)[0]
            path = os.path.join(theme_dir, i)

            if (os.path.isdir(path)):
                self.__load_recursively(path)

            elif (i.endswith(".def")):
                self.__read_def_file(path)
                
            elif (i.endswith(".png") or i.endswith(".jpg")):
                self.__read_image(name, path)
        #end for                


    def __read_image(self, name, path):
    
        if (name in self.__objects):
            nil, nil, obj = self.__objects[name]
        else:
            obj = None

        #obj = None
        self.__objects[name] = (_TYPE_PBUF, path, obj)
        if (obj): obj.set_objdef(path)


    def __read_def_file(self, f):

        import time
        t1 = time.time()
        #lines = open(f).readlines()
        lines = [l for l in open(f).readlines()
                 if l.strip() and not l.startswith("#") ]
            
        for line in lines:
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
        #end for
        #print "reading def file %s took %s seconds" % (f, time.time() - t1)
            

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
"""the theme singleton object"""
theme.set_theme("default")

