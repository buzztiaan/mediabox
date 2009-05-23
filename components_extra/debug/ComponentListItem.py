from ui.ButtonListItem import ButtonListItem
from theme import theme


class ComponentListItem(ButtonListItem):
    """
    List item for components.
    """

    BUTTON_OPEN = "open"
    BUTTON_REMOVE = "remove"


    def __init__(self, component):

        self.__component = component
        self.__info = ""
        
        ButtonListItem.__init__(self)
        self.set_colors(theme.color_mb_listitem_text, theme.color_mb_listitem_subtext)
        self.set_font(theme.font_mb_micro)

        self.set_buttons((self.BUTTON_OPEN, theme.mb_item_btn_open))

        if (component.__doc__):
            lines = [ l.strip() for l in component.__doc__.splitlines()
                      if l.strip() ]
            self.__info = "\n".join(lines)
        else:
            self.__info = "- no description available -"


    def render_this(self, cnv):
    
        self.render_bg(cnv)

        w, h = self.get_size()
        try:
            icon = self.__component.ICON
        except:
            icon = None
            
        if (icon):
            cnv.fit_pixbuf(icon, 8, (h - 80) / 2, 80, 80)

        self.render_label(cnv, 112,
                          self.__component.__class__.__module__,
                          self.__info)
        self.render_buttons(cnv)

