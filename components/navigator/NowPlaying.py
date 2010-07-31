from com import Component, msgs
from ui import Widget
from ui import Pixmap
from ui import pixbuftools
from theme import theme

import gtk


class NowPlaying(Widget, Component):

    def __init__(self):
    
        self.__buffer = None
        
        self.__title = ""
        self.__info = ""
        self.__cover = None
        
        Component.__init__(self)
        Widget.__init__(self)
        
        
        
    def set_size(self, w, h):
    
        Widget.set_size(self, w, h)
        self.__buffer = None
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (not self.__buffer):
            self.__render()

        pbuf = self.__buffer.render_on_pixbuf()
        if (w < h):
            rpbuf = pbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)
            del pbuf
            pbuf = rpbuf
  
            
        screen.draw_pixbuf(pbuf, x, y)
            

    def __render(self):

        w, h = self.get_size()
        if (w < h):
            w, h = h, w
            
        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)

        self.__buffer.fill_area(0, 0, w, h, theme.color_mb_background)
        self.__buffer.draw_frame(theme.mb_button_1, 0, 0, w, h, True)

        if (self.__cover):
            self.__buffer.fit_pixbuf(self.__cover, 8, 4, 72, 56)
            offset = 96
        else:
            offset = 8

        self.__buffer.draw_text(self.__title,
                                theme.font_mb_tiny,
                                offset, 4,
                                theme.color_mb_text)

        self.__buffer.draw_text(self.__info,
                                theme.font_mb_micro,
                                offset, 26,
                                theme.color_mb_text)
        
        self.__buffer.draw_pixbuf(theme.mb_btn_play_1,
                                  w - 64, (h - 64) / 2)


    def handle_MEDIA_EV_LOADED(self, player, f):

        def on_loaded(thumbpath):
            if (thumbpath):
                self.__cover = self.__load_pixbuf(f, thumbpath)
                
                self.__render()
                self.render()
                
        self.__cover = None
        self.__title = f.name
        self.__info = f.info

        thumbpath, is_final = \
          self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
        if (thumbpath):
            self.__cover = self.__load_pixbuf(f, thumbpath)

        if (not is_final):
            self.call_service(msgs.THUMBNAIL_SVC_LOAD_THUMBNAIL, f, on_loaded)

        self.__render()
        self.render()

            
    def handle_MEDIA_EV_TAG(self, tag, value):
    
        if (tag == "ARTIST"):
            self.__info = value
        elif (tag == "TITLE"):
            self.__title = value
            
        self.__render()
        self.render()
        
        
    def __load_pixbuf(self, f, path):
        """
        Loads the icon pixbuf and its frame, if any.
        """

        if (path):
            try:
                if (path.startswith("data://")):
                    import base64
                    data = base64.b64decode(path[7:])
                    loader = gtk.gdk.PixbufLoader()
                    loader.write(data)
                    loader.close()
                    icon = loader.get_pixbuf()
                    del loader
            
                else:
                    icon = gtk.gdk.pixbuf_new_from_file(path)

            except:
                #import traceback; traceback.print_exc()
                logging.error("could not load thumbnail of (%s): %s",
                              self.__label, path)
                icon = None

        else:
            icon = None

        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 160, 120)
        pbuf.fill(0x00000000)
        
        frm, x, y, w, h = f.frame
        if (frm):
            pixbuftools.draw_pbuf(pbuf, frm, 0, 0)
        else:
            x, y, w, h = 0, 0, 160, 120
        if (icon):            
            pixbuftools.fit_pbuf(pbuf, icon, x, y, w, h)
            del icon

        return pbuf

