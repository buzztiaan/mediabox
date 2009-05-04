"""
B{Used internally}
"""

import pango


class Font(pango.FontDescription):
    """
    Wrapper class for font theme elements.
    @since: 0.96
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
