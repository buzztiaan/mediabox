from ui.ListItem import ListItem
from theme import theme
            

class RowItem(ListItem):
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

        ListItem.__init__(self)
        
        
    def set_colors(self, col1, col2):
    
        self.__color_1 = col1
        self.__color_2 = col2
        
        
    def set_font(self, font):
    
        self.__font = font


    def set_spacing(self, spacing) :

        self.__spacing = spacing
        self.myrender ()


    def set_initial_offset(self, initial_offset) :

        self.__my_initial_row_offset = initial_offset
        self.myrender ()


    def append_button (self, grid_button) :

        grid_button.set_container (self)
        self.__button_list.append ( grid_button )
        self.myrender ()


    def add_button (self, grid_button, position):

        grid_button.set_container (self)
        self.__button_list.insert (position, grid_button)
        self.myrender ()


    def get_button_position_by_uuid (self, uuid):

        for index, button in enumerate(self.__button_list) :

            if ( button.upnp_uuid == uuid ):
                return index

        return (-1)


    def remove_button_from_position (self, position):

        removed_button = self.__button_list.pop (position)
        self.myrender ()
    
        if ( self.__button_list.__len__() < 1 ): empty = True
        else : empty = False

        return (removed_button, empty)
    

    def get_button_at(self, px):
        x = self.__initial_offset       

        if (px < x) : return None

        for button in self.__button_list:
            x += button.get_active_image().get_width()
            
            if (button.option_button_image == None):
                if (px < x):
                    return button, False
            else:
                if (px < x - 30):
                    return button, False
                if (px < x + 13):
                    return button, True

            x += self.__spacing
            if (px < x): #if it hits between the buttons. Maybe it would be better to trigger a button from one half and the other from the other. Test with touchscreen.
                return None, False
        #end for
        
        return None, False
    

    def get_button_list (self):
        return ( self.__button_list )   
    

    def myrender (self):
        self.render()
        self.__gridlist.render()


    def render_this(self, canvas):
    
        ListItem.render_this(self, canvas)
        w, h = canvas.get_size()
        
        x = self.__initial_offset -10  #dont know why but theres a extra offset and so the -10
        
        for one_button in self.__button_list:
            image = one_button.get_active_image()

            canvas.draw_pixbuf(image,
                               x, (h - image.get_height()) / 4 )

            if ( one_button.option_button_image ):
                canvas.draw_pixbuf(one_button.option_button_image, x + image.get_width() - 30, (h - 73) )
            
            #missing to center the text
            label = one_button.get_label()
            canvas.draw_text("%s" \
                      % (label),
                         self.__font, x, (h / 2) + (image.get_height() / 1.89),
                         self.__color_1, use_markup = True)

            x += image.get_width()
            x += self.__spacing
        #end for

