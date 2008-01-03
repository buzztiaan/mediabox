from Widget import Widget
from Pixmap import Pixmap


class TabsBar(Widget):

    def __init__(self, esens):
    
        self.__tabs = []
        self.__callbacks = []
        
        self.__bg = Pixmap(None, 80, 80)
        self.__buffer = Pixmap(None, 80, 80)
        self.__current_tab = -1
    
        Widget.__init__(self, esens)
        self.connect(self.EVENT_BUTTON_PRESS, self.__on_select_tab)
        
        
    def __on_select_tab(self, px, py):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        cnt = 0
        for i in range(0, w, 90):
            if (i + 90 > px):
                if (cnt == self.__current_tab):
                    break
                else:
                    self.hilight_tab(cnt)
                    cb, args = self.__callbacks[cnt]
                    cb(*args)
                    break            
            cnt += 1
        #end for
        
        
        
    def add_tab(self, icon, icon_active, cb, *args):
    
        self.__tabs.append((icon, icon_active))
        self.__callbacks.append((cb, args))

        nil, h = self.get_size()
        w = 90 * len(self.__tabs)
        self.set_size(w, 80)
        
                
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        # save background
        self.__bg.copy_buffer(screen, x, y, 0, 0, 80, 80)
        
        cnt = 0
        for icon, icon_active in self.__tabs:
            pbuf = (cnt == self.__current_tab) and icon_active or icon
            x1 = x + 40 - pbuf.get_width() / 2
            y1 = y + 40 - pbuf.get_height() / 2
            screen.draw_pixbuf(pbuf, x1, y1)
            x += 90
            cnt += 1
        #end for
            
            
    def hilight_tab(self, idx):

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
                  
        if (self.__current_tab != -1):
            icon, icon_active = self.__tabs[self.__current_tab]
            x1 = 40 - icon.get_width() / 2            
            y1 = 40 - icon.get_height() / 2
            x2 = x + self.__current_tab * 90
            self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, 80, 80)
            self.__buffer.draw_pixbuf(icon, x1, y1)
            screen.copy_pixmap(self.__buffer, 0, 0, x2, y, 80, 80)
           
        icon, icon_active = self.__tabs[idx]
        x1 = 40 - icon_active.get_width() / 2            
        y1 = 40 - icon_active.get_height() / 2
        x2 = x + idx * 90
        self.__buffer.copy_pixmap(self.__bg, 0, 0, 0, 0, 80, 80)        
        self.__buffer.draw_pixbuf(icon_active, x1, y1)
        screen.copy_pixmap(self.__buffer, 0, 0, x2, y, 80, 80)
        self.__current_tab = idx
        
