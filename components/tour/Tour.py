from com import Configurator, msgs
from ui.Pixmap import Pixmap
from theme import theme

import gtk
import os


_PATH = os.path.dirname(__file__)

class Tour(Configurator):
    """
    Configurator providing a short tour through the application.
    """

    ICON = theme.prefs_icon_get_started
    TITLE = "Get Started"
    DESCRIPTION = "Learn how to use MediaBox"
    

    def __init__(self):
    
        self.__current_page = 0
        self.__pages = []
    
        data = open(os.path.join(_PATH, "tour_C.dat")).read()
        self.__parse_tour(data)
    
        Configurator.__init__(self)
        self.connect_button_released(self.__on_click)
        
        
    def __on_click(self, px, py):
    
        w, h = self.get_size()
        if (px < w / 2):
            self.__go_back()
        else:
            self.__go_forward()
            
            
    def __go_back(self):
    
        if (self.__current_page > 0):
            self.__current_page -= 1
            #self.render()
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            buf = Pixmap(None, w, h)
            self.render_at(buf)
            self.fx_slide_horizontal(buf, 0, 0, w, h, self.SLIDE_RIGHT)

    def __go_forward(self):
    
        if (self.__current_page < len(self.__pages) - 1):
            self.__current_page += 1
            #self.render()
            x, y = self.get_screen_pos()
            w, h = self.get_size()
            buf = Pixmap(None, w, h)
            self.render_at(buf)
            self.fx_slide_horizontal(buf, 0, 0, w, h, self.SLIDE_LEFT)
    
        
    def __parse_tour(self, data):
    
        self.__pages = []
        title = ""
        image = ""
        text = ""
        
        for line in data.splitlines():
            if (line.startswith("BEGIN")):
                title = line[6:].strip()
                image = ""
                text = ""
            elif (line.startswith("IMAGE ")):
                image = line[6:].strip()
            elif (line.startswith("END")):
                self.__pages.append((title, image, text))
            else:
                text += line + "\n"
        #end for
        
        
    def _visibility_changed(self):
    
        self.__current_page = 0
        Configurator._visibility_changed(self) 
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        title, image, text = self.__pages[self.__current_page]
        
        screen.fill_area(0, 0, w, h, theme.color_mb_background)
        
        screen.draw_text("%d/%d" % (self.__current_page + 1, len(self.__pages)),
                         theme.font_mb_tiny,
                         w - 42, h - 20,
                         theme.color_mb_text)
        
        if (w < h):
            # portrait mode
            title_x, title_y = 4, 4
            image_x, image_y = 90, 4
            if (image):
                text_x, text_y = 4, 320
                text_w, text_h = w - 8, 320
            else:
                text_x, text_y = 4, 4
                text_w, text_h = w - 8, 620

        else:
            # landscape mode
            title_x, title_y = 4, 4
            image_x, image_y = 40, 4
            if (image):
                text_x, text_y = 380, 4
                text_w, text_h = 400, 320
            else:
                text_x, text_y = 4, 4
                text_w, text_h = w - 8, 320
        
        if (title):
            self.set_title(title)
            #screen.draw_text(title, theme.font_mb_headline,
            #                 title_x, title_y, "#ffffff")

        if (image):
            pbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(_PATH, image))
            img_w, img_h = pbuf.get_width(), pbuf.get_height()
            image_x += (300 - img_w) / 2
            image_y += (300 - img_h) / 2
            screen.draw_pixbuf(pbuf, image_x, image_y)

        if (text):
            screen.draw_formatted_text(text, theme.font_mb_plain,
                                       text_x, text_y, text_w, text_h,
                                       theme.color_mb_text)

