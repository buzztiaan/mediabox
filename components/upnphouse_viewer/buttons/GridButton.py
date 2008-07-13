
def _to_utf8(s):

    return s.decode("utf-8", "replace").encode("utf-8")
    
def _xml_escape(s):

    return s.replace("<", "&lt;") \
            .replace(">", "&gt;") \
            .replace("&", "&amp;")


class GridButton (object) :
    """
    Class with the information to render a button with RowItem
    """
    
    def __init__(self, button_label, button_on_image, button_off_image, my_button_state) :
         
         self.__container = None
         
         self.__on_image = button_on_image
         self.__off_image = button_off_image
         self.__state = my_button_state

         self.option_button_image = None
         
         label = button_label.decode("utf-8", "replace").encode("utf-8")
         self.__label = _xml_escape(_to_utf8(label))

         self.__active_image = self.__on_image

         if (self.__state == 0) :
             self.__active_image = self.__off_image
    
    def get_active_image (self):
        return ( self.__active_image )

    def get_label (self):
        return ( self.__label )

    def set_on_image (self, on_image) :
        
         self.__on_image = on_image
         
         if (self.__state > 0) :
             self.__active_image = self.__on_image
             if (self.__container) : self.__container.myrender ()

    def set_off_image (self, off_image) :
        
         self.__off_image = off_image
         
         if (self.__state == 0) :
             self.__active_image = self.__off_image
             if (self.__container) : self.__container.myrender ()

    def set_container (self, container):
        self.__container = container


    def get_state (self):

        return self.__state


    def set_state (self, state) :

        if (self.__state == state) : return

        self.__state = state

        if (self.__state == 0) :
             self.__active_image = self.__off_image
        else :
             self.__active_image = self.__on_image
        
        if (self.__container) : self.__container.myrender ()


