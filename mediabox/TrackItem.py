from ui.ButtonListItem import ButtonListItem
import thumbnail
import theme

import os


def _to_utf8(s):

    return s.decode("utf-8", "replace").encode("utf-8")
            

class TrackItem(ButtonListItem):
    """
    List item for track items.
    """

    def __init__(self, icon, mimetype, label, sublabel):
    
        self.__icon = icon
        self.__mimetype = mimetype
        self.__emblem = None
    
        label = label.decode("utf-8", "replace").encode("utf-8")
        sublabel = sublabel.decode("utf-8", "replace").encode("utf-8")
        self.__label = self.escape_xml(_to_utf8(label))
        self.__sublabel = self.escape_xml(_to_utf8(sublabel))
           
        ButtonListItem.__init__(self)
        
        
    def set_icon(self, icon):
    
        self.__icon = icon
        

    def set_emblem(self, emblem):
    
        self.__emblem = emblem

        
        
    def render_this(self, canvas):
    
        ButtonListItem.render_this(self, canvas)
        w, h = canvas.get_size()
          
        x = 8
        if (self.__icon):
            icon = thumbnail.draw_decorated(canvas, 4, 4, 120, 80,
                                            self.__icon, self.__mimetype)

            #canvas.fit_pixbuf(icon, 4, 4, 120, 70)
                               #x, (h - self.__icon.get_height()) / 2)
            x += 120 #self.__icon.get_width()
            x += 12
            
            if (self.__emblem):
                canvas.fit_pixbuf(self.__emblem, 70, 32, 48, 48)
        
        self.render_label(canvas, x, self.__label, self.__sublabel)
        self.render_selection_frame(canvas)
        self.render_buttons(canvas)
        
