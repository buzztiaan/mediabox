"""
B{Used internally}
"""

import pango


class Font(pango.FontDescription):
    """
    Class for font theme elements.
    """

    def __init__(self, desc):
    
        self.__desc = desc
        self.__needs_reload = False
        
        pango.FontDescription.__init__(self, desc)
        
        
    def set_objdef(self, desc):
    
        self.__desc = desc
        self.__needs_reload = True
        
        
    def reload(self):
        
        if (self.__needs_reload):
            font = pango.FontDescription(self.__desc)
            self.merge(font, True)
            self.__needs_reload = False
