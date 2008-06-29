from ui.Item import Item
import theme
            

class RowItem(Item):
    """
    List item for track items.
    """

    def __init__(self, gridlist, spacing = 44, initial_offset = 10):

        self.__button_list = []
        
        self.__color_1 = "#000000"
        self.__color_2 = "#666666"
        self.__font = None
        self.__spacing = spacing
        self.__initial_offset = initial_offset
        self.__gridlist = gridlist        

        Item.__init__(self)
        
        
    def set_colors(self, col1, col2):
    
        self.__color_1 = col1
        self.__color_2 = col2
        
        
    def set_font(self, font):
    
        self.__font = font


    def set_spacing(self, spacing) :

        self.__spacing = spacing
        self.render ()


    def set_initial_offset(self, initial_offset) :

        self.__my_initial_row_offset = initial_offset
        self.render ()


    def append_button (self, grid_button) :

        grid_button.set_container (self)
        self.__button_list.append ( grid_button )
        self.render ()


    def add_button (self, grid_button, position):

        grid_button.set_container (self)
        self.__button_list.insert (position, grid_button)
        self.render ()


    def remove_button (self, position):

        removed_button = self.__button_list.pop (position)
        self.render ()
    
        if ( self.__button_list.__len__() < 1 ): empty = True
        else : empty = False

        return (removed_button, empty)
    

    def get_button_at(self, px):
        x = self.__initial_offset       

        if (px < x) : return None

        for button in self.__button_list:
            x += button.get_active_image().get_width()
            
            if (px < x):
                return button

            x += self.__spacing
            if (px < x): #if it hits between the buttons. Maybe it would be better to trigger a button from one half and the other from the other. Test with touchscreen.
                return None
        #end for
        
        return None
    

    def get_button_list (self):
        return ( self.__button_list )   
    

    def myrender (self):
        self.render()
        self.__gridlist.render_full()


    def render_this(self, canvas):
    
        Item.render_this(self, canvas)
        w, h = canvas.get_size()
        
        x = self.__initial_offset -10  #dont know why but theres a extra offset and so the -10
        
        for one_button in self.__button_list:
            image = one_button.get_active_image()

            canvas.draw_pixbuf(image,
                               x, (h - image.get_height()) / 4 )
            
            #missing to center the text
            label = one_button.get_label()
            canvas.draw_text("%s" \
                      % (label),
                         self.__font, x, (h / 2) + (image.get_height() / 1.89),
                         self.__color_1, use_markup = True)

            x += image.get_width()
            x += self.__spacing
        #end for

