from ui.itemview import Item
from theme import theme


class ComponentListItem(Item):
    """
    List item for components.
    """

    def __init__(self, component):

        self.__component = component
        self.__info = ""
        
        Item.__init__(self)

        if (component.__doc__):
            lines = [ l.strip() for l in component.__doc__.splitlines()
                      if l.strip() ]
            self.__info = "\n".join(lines)
        else:
            self.__info = "- no description available -"


    def get_component(self):
    
        return self.__component


    def render_at(self, cnv, x, y):

        w, h = self.get_size()
        
        pmap, is_new = self._get_cached_pixmap()
        
        if (is_new):
            pmap.fill_area(0, 0, w, h, theme.color_mb_background)
        
            # render selection frame
            if (self.is_marked() or self.is_hilighted()):
                pmap.draw_frame(theme.mb_selection_frame, 0, 0, w, h, True,
                                pmap.TOP | pmap.BOTTOM | pmap.LEFT | pmap.RIGHT)
                       
            try:
                icon = self.__component.ICON
            except:
                icon = None
                
            if (icon):
                pmap.fit_pixbuf(icon, 8, (h - 80) / 2, 80, 80)

            pmap.set_clip_rect(0, 0, w, h)
            pmap.draw_text(self.__component.__class__.__module__,
                           theme.font_mb_plain,
                           96, 4,
                           theme.color_list_item_text)
            pmap.draw_text(self.__info,
                           theme.font_mb_tiny,
                           96, 30,
                           theme.color_list_item_subtext)
            pmap.set_clip_rect()
        #end if

        # copy to the given canvas
        cnv.copy_buffer(pmap, 0, 0, x, y, w, h)

