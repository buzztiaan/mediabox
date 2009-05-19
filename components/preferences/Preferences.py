from com import Viewer, Configurator, msgs
from mediabox.TrackList import TrackList
from PrefsItem import PrefsItem
from ui.ImageButton import ImageButton
from ui.Pixmap import Pixmap
from mediabox import viewmodes
from theme import theme


class Preferences(Viewer):
    """
    Viewer for displaying the Configurator components.
    """

    PRIORITY = 9999
    ICON = theme.mb_viewer_prefs
    

    def __init__(self):
    
        self.__current_configurator = None
        self.__configurators = []
    
        Viewer.__init__(self)
        self.set_title("Preferences")
        
        self.__list = TrackList()
        self.__list.connect_button_clicked(self.__on_item_button)
        self.add(self.__list)

        # toolbar
        self.__btn_back = ImageButton(theme.mb_btn_dir_up_1,
                                      theme.mb_btn_dir_up_2)
        self.__btn_back.connect_clicked(self.__on_btn_back)
        
        
    def __on_item_button(self, item, idx, button):
    
        if (button == item.BUTTON_PLAY):
            self.__list.hilight(idx)
            self.__current_configurator = item.get_configurator()
            self.__list.set_visible(False)
            self.__current_configurator.set_visible(True)
            self.set_toolbar([self.__btn_back])
            self.set_title(u"Preferences \u00bb %s" \
                           % self.__current_configurator.TITLE)
            self.__fx_slide_left()
            self.emit_message(msgs.UI_ACT_RENDER)
            self.__list.hilight(-1)


    def __on_btn_back(self):
    
        self.__current_configurator.set_visible(False)
        self.__list.set_visible(True)
        self.__current_configurator = None
        self.set_toolbar([])
        self.set_title("Preferences")
        self.__fx_slide_right()
        self.emit_message(msgs.UI_ACT_RENDER)
        
        
    def render_this(self):
    
        w, h = self.get_size()
        
        self.__list.set_geometry(0, 0, w, h)

        if (self.__current_configurator):
            self.__current_configurator.set_size(w, h)
        
        
    def __register_configurator(self, comp):
    
        self.add(comp)
        comp.set_visible(False)
        
        item = PrefsItem(comp)
        self.__list.append_item(item)


    def __comparator(self, a, b):
    
        return cmp(a.TITLE, b.TITLE)        


    def handle_message(self, event, *args):

        if (event == msgs.COM_EV_COMPONENT_LOADED):
            comp = args[0]
            if (isinstance(comp, Configurator)):
                self.__configurators.append(comp)
                
        elif (event == msgs.CORE_EV_APP_STARTED):
            self.__configurators.sort(self.__comparator)
            while self.__configurators:
                self.__register_configurator(self.__configurators.pop(0))
            self.render()
            
        if (self.is_active()):
            if (event == msgs.INPUT_ACT_REPORT_CONTEXT):
                self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)


    def show(self):
    
        Viewer.show(self)
        self.emit_message(msgs.UI_ACT_VIEW_MODE, viewmodes.NO_STRIP)
        self.emit_message(msgs.INPUT_EV_CONTEXT_BROWSER)



    def __fx_slide_left(self):

        def fx(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 3
            
            if (dx > 0):
                screen.move_area(x + dx, y, w - dx, h, -dx, 0)
                screen.copy_pixmap(buf, from_x, 0, x + w - dx, y, dx, h)

                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x + dx, y, w - dx, h, -dx, 0)
                screen.copy_pixmap(buf, from_x, 0, x + w - dx, y, dx, h)
                
                return False


        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        #buf.fill_area(0, 0, w, h, self.__bg_color)
        self.render_at(buf)

        self.animate(50, fx, [0, w])



    def __fx_slide_right(self):

        def fx(params):
            from_x, to_x = params
            dx = (to_x - from_x) / 3
            
            if (dx > 0):
                screen.move_area(x, y, w - dx, h, dx, 0)
                screen.copy_pixmap(buf, w - from_x - dx, 0, x, y, dx, h)

                params[0] = from_x + dx
                params[1] = to_x
                return True

            else:
                dx = to_x - from_x
                screen.move_area(x, y, w - dx, h, dx, 0)
                screen.copy_pixmap(buf, w - from_x - dx, 0, x, y, dx, h)

                return False


        if (not self.may_render()): return

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()

        buf = Pixmap(None, w, h)
        #buf.fill_area(0, 0, w, h, self.__bg_color)
        self.render_at(buf)

        self.animate(50, fx, [0, w])
