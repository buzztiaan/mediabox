from Widget import Widget


class VBox(Widget):

    HALIGN_LEFT = 0
    HALIGN_CENTER = 1
    HALIGN_RIGHT = 2
    
    VALIGN_TOP = 0
    VALIGN_CENTER = 1
    VALIGN_RIGHT = 2
    

    def __init__(self):
    
        self.__halign = self.HALIGN_LEFT
        self.__valign = self.VALIGN_TOP
        self.__spacing = 0
    
        Widget.__init__(self)


    def set_spacing(self, spacing):
    
        self.__spacing = spacing


    def set_halign(self, align):
    
        self.__halign = align
        
        
    def set_valign(self, align):
    
        self.__valign = align


    def render_this(self):
    
        w, h = self.get_size()
        children = [ c for c in self.get_children() if c.is_visible() ]
    
        total_height = reduce(lambda a,b:a+b,
                             [ c.get_physical_size()[1] + self.__spacing
                               for c in children ], 0)
        total_height = min(h, total_height)
        
        if (self.__valign == self.VALIGN_TOP):
            y = 0
        elif ( self.__valign == self.VALIGN_CENTER):
            y = (h - total_height) / 2
        else:
            y = h - total_height

        for c in children:
            width, height = c.get_physical_size()

            if (self.__halign == self.HALIGN_LEFT):
                c.set_pos(0, y)
            elif (self.__halign == self.HALIGN_CENTER):
                c.set_pos((w - width) / 2, y)
            else:
                c.set_pos(w - width, y)
            y += height + self.__spacing
        #end for

