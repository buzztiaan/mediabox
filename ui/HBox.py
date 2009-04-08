from Widget import Widget


class HBox(Widget):

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
        self.__is_dynamic = {}
    
        Widget.__init__(self)


    def add(self, c, dynamic_size = False):
    
        Widget.add(self, c)
        self.__is_dynamic[c] = dynamic_size


    def set_spacing(self, spacing):
    
        self.__spacing = spacing


    def set_halign(self, align):
    
        self.__halign = align
        
        
    def set_valign(self, align):
    
        self.__valign = align


    def render_this(self):
    
        w, h = self.get_size()
        children = [ c for c in self.get_children() if c.is_visible() ]
        fixed_children = [ c for c in children
                           if not self.__is_dynamic[c] ]
        dynamic_children = [ c for c in children
                             if self.__is_dynamic[c] ]

        fixed_width = reduce(lambda a,b:a+b,
                             [ c.get_physical_size()[0]
                               for c in fixed_children ], 0)
        fixed_width += (len(children) - 1) * self.__spacing
        
        if (dynamic_children):
            dynamic_width = (w - fixed_width) / len(dynamic_children)
        else:
            dynamic_width = 0

        
        if (not dynamic_children):
            if (self.__halign == self.HALIGN_LEFT):
                x = 0
            elif ( self.__halign == self.HALIGN_CENTER):
                x = (w - fixed_width) / 2
            else:
                x = w - fixed_width
        else:
            x = 0
            
        for c in children:
            width, height = c.get_physical_size()
            if (self.__is_dynamic[c]):
                width = dynamic_width
                height = h
                c.set_size(width, height)

            if (self.__valign == self.VALIGN_TOP):
                c.set_pos(x, 0)
            elif (self.__valign == self.VALIGN_CENTER):
                c.set_pos(x, (h - height) / 2)
            else:
                c.set_pos(x, h - height)
            x += width + self.__spacing
        #end for

