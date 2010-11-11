from com import Configurator, msgs
from ui.layout import Arrangement
from ui import ToolbarButton
from ui import Toolbar
from ui import Pixmap
from ui import Widget
from ui.dialog import ListDialog
from ui.itemview import LabelItem
from theme import theme

import gtk
import os


_PATH = os.path.dirname(__file__)


_LANDSCAPE_ARRANGEMENT = """
  <arrangement>
    <widget name="content" x1="0" y1="0" x2="-80" y2="100%"/>
    <widget name="toolbar" x1="-80" y1="0" x2="100%" y2="100%"/>
  </arrangement>
"""


_PORTRAIT_ARRANGEMENT = """
  <arrangement>
    <widget name="content" x1="0" y1="0" x2="100%" y2="-80"/>
    <widget name="toolbar" x1="0" y1="-80" x2="100%" y2="100%"/>
  </arrangement>
"""



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

        self.__tour_box = Widget()

        # toolbar elements
        btn_toc = ToolbarButton(theme.mb_btn_toc_1)
        btn_toc.connect_clicked(self.__on_btn_toc)

        btn_previous = ToolbarButton(theme.mb_btn_previous_1)
        btn_previous.connect_clicked(self.__on_btn_previous)

        btn_next = ToolbarButton(theme.mb_btn_next_1)
        btn_next.connect_clicked(self.__on_btn_next)
        
        # toolbar
        self.__toolbar = Toolbar()
        self.__toolbar.set_toolbar(btn_previous,
                                   btn_toc,
                                   btn_next)

        # arrangement
        self.__arr = Arrangement()
        self.__arr.connect_resized(self.__update_layout)
        self.__arr.add(self.__tour_box, "content")
        self.__arr.add(self.__toolbar, "toolbar")
        self.add(self.__arr)
        

    def __update_layout(self):
    
        w, h = self.get_size()
        if (w < h):
            self.__arr.set_xml(_PORTRAIT_ARRANGEMENT)           

        else:
            self.__arr.set_xml(_LANDSCAPE_ARRANGEMENT)


    def __on_btn_previous(self):
        
        self.__go_back()


    def __on_btn_toc(self):
    
        dlg = ListDialog("Table of Contents")
        cnt = 0
        for title, image, text in self.__pages:
            item = LabelItem(title)
            item.set_payload(cnt)
            dlg.add_item(item)
            cnt += 1
        #end for
        
        dlg.run()
        item = dlg.get_choice()
        if (item):
            idx = item.get_payload()
            self.__go_page(idx)


    def __on_btn_next(self):
        
        self.__go_forward()

        
    def __on_click(self, px, py):
    
        w, h = self.get_size()
        if (px < w / 2):
            self.__go_back()
        else:
            self.__go_forward()
            
            
    def __go_back(self):

        self.__go_page(self.__current_page - 1)    


    def __go_forward(self):
    
        self.__go_page(self.__current_page + 1)


    def __go_page(self, idx):

        if (0 <= idx < len(self.__pages)):
            if (idx < self.__current_page):
                slide_mode = self.SLIDE_RIGHT
            else:
                slide_mode = self.SLIDE_LEFT
                
            self.__current_page = idx
            
            title, image, text = self.__pages[self.__current_page]
            self.set_title(title.strip())
            
            w, h = self.get_size()
            buf = Pixmap(None, w, h)
            self.render_at(buf)

            box_x, box_y = self.__tour_box.get_screen_pos()
            box_w, box_h = self.__tour_box.get_size()
            self.fx_slide_horizontal(buf, box_x, box_y, box_w, box_h, slide_mode)
        #end if

        
    def __parse_tour(self, data):
    
        self.__pages = []
        title = ""
        image = ""
        text = ""

        section = 0
        subsection = 0        
        for line in data.splitlines():
            if (line.startswith("#")):
                continue

            elif (line.startswith("BEGIN")):
                section += 1
                subsection = 0
                title = "%d. %s" % (section, line[6:].strip())
                image = ""
                text = ""

            elif (line.startswith("SUBBEGIN")):
                subsection += 1
                title = "%d.%d %s" % (section, subsection, line[9:].strip())
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

        Configurator.render_this(self)
        self.__render_tour()
            
    
    def __render_tour(self):

        self.__arr.render()    
        x, y = self.__tour_box.get_screen_pos()
        w, h = self.__tour_box.get_size()
        screen = self.__tour_box.get_screen()
        
        title, image, text = self.__pages[self.__current_page]
        self.set_title(title.strip())


        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        #screen.draw_text("%d/%d" % (self.__current_page + 1, len(self.__pages)),
        #                 theme.font_mb_tiny,
        #                 x + w - 42, y + 4,
        #                 theme.color_mb_text)
        
        if (w < h):
            # portrait mode
            title_x, title_y = 4, 4
            image_x, image_y = 90, 4
            if (image):
                text_x, text_y = 4, 320
                text_w, text_h = w - 8, 240
            else:
                text_x, text_y = 4, 4
                text_w, text_h = w - 8, 540

        else:
            # landscape mode
            title_x, title_y = 4, 4
            image_x, image_y = 40, 4
            if (image):
                text_x, text_y = 380, 4
                text_w, text_h = 320, 320
            else:
                text_x, text_y = 4, 4
                text_w, text_h = w - 88, 320
        
        if (image):
            pbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(_PATH, image))
            img_w, img_h = pbuf.get_width(), pbuf.get_height()
            image_x += (300 - img_w) / 2
            image_y += (300 - img_h) / 2
            screen.draw_pixbuf(pbuf, x + image_x, y + image_y)

        if (text):
            screen.draw_formatted_text(text, theme.font_mb_plain,
                                       x + text_x, y + text_y, text_w, text_h,
                                       theme.color_mb_text)

