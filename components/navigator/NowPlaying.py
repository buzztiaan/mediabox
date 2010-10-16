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
        self.__info = "- no media loaded -"
        self.__cover = theme.mb_logo
        
        self.__prepared_file = None
        
        
        Component.__init__(self)
        Widget.__init__(self)
        
        self.connect_clicked(self.__on_click)
        
        
    def __on_click(self):
    
        if (self.__prepared_file):
            self.__start_prepared()
            
        elif (self.__title):
            self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "player.PlayerWindow")


    def __start_prepared(self):

        self.emit_message(msgs.MEDIA_ACT_LOAD, self.__prepared_file)
        self.__prepared_file = None
        self.emit_message(msgs.UI_ACT_SHOW_DIALOG, "player.PlayerWindow")
        
        
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
            rpbuf = pbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
            del pbuf
            pbuf = rpbuf
  
            
        screen.draw_pixbuf(pbuf, x, y)
            

    def __render(self):

        w, h = self.get_size()
        if (w < h):
            w, h = h, w
            
        if (w == 0 or h == 0): return
            
        if (not self.__buffer):
            self.__buffer = Pixmap(None, w, h)

        self.__buffer.fill_area(0, 0, w, h, theme.color_mb_background)
        self.__buffer.draw_frame(theme.mb_selection_frame, 0, 0, w, h, True)

        if (self.__cover and h > 10):
            self.__buffer.fit_pixbuf(self.__cover, 8, 5, h - 10, h - 10)
            offset = h + 8
        else:
            offset = 8

        self.__buffer.set_clip_rect(offset, 0, w - offset, h)
        self.__buffer.draw_text(self.__title or "MediaBox",
                                theme.font_mb_plain,
                                offset, 4,
                                theme.color_list_item_text)

        self.__buffer.draw_text(self.__info,
                                theme.font_mb_tiny,
                                offset, 32,
                                theme.color_list_item_subtext)
        self.__buffer.set_clip_rect()
        
        #if (self.__title):
        #    self.__buffer.draw_pixbuf(theme.mb_now_playing,
        #                              w - 64, (h - 64) / 2)


    def handle_MEDIA_ACT_PLAY(self):
    
        if (self.__prepared_file):
            self.__start_prepared()


    def handle_MEDIA_ACT_PREPARE(self, f):

        def on_loaded(thumbpath):
            if (thumbpath):
                self.__cover = self.__load_pixbuf(f, thumbpath)
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", self.__cover)
                
                self.__render()
                self.render()
                
        self.__prepared_file = f
        self.__cover = None
        self.__title = f.name
        self.__info = f.info

        thumbpath, is_final = \
          self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
        if (thumbpath):
            self.__cover = self.__load_pixbuf(f, thumbpath)

        if (not is_final):
            self.call_service(msgs.THUMBNAIL_SVC_LOAD_THUMBNAIL, f, on_loaded)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        #buf = Pixmap(None, w, h)
        self.__render()
        #self.render_at(buf)
        #self.fx_slide_vertical(buf, x, y, w, h, self.SLIDE_UP)
        self.render()


    def handle_MEDIA_EV_LOADED(self, player, f):

        def on_loaded(thumbpath):
            if (thumbpath):
                self.__cover = self.__load_pixbuf(f, thumbpath)
                self.emit_message(msgs.MEDIA_EV_TAG, "PICTURE", self.__cover)
                
                self.__render()
                self.render()
                
        self.__prepared_file = None
        self.__cover = None
        self.__title = f.name
        self.__info = f.info

        thumbpath, is_final = \
          self.call_service(msgs.THUMBNAIL_SVC_LOOKUP_THUMBNAIL, f)
        if (thumbpath):
            self.__cover = self.__load_pixbuf(f, thumbpath)

        if (not is_final):
            self.call_service(msgs.THUMBNAIL_SVC_LOAD_THUMBNAIL, f, on_loaded)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        #buf = Pixmap(None, w, h)
        self.__render()
        #self.render_at(buf)
        #self.fx_slide_vertical(buf, x, y, w, h, self.SLIDE_UP)
        self.render()

            
    def handle_MEDIA_EV_TAG(self, tag, value):
    
        if (tag == "ARTIST"):
            self.__info = value
        elif (tag == "TITLE"):
            self.__title = value
        elif (tag == "PICTURE"):
            self.__cover = value
            
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

        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 160, 160)
        pbuf.fill(0x00000000)
        
        frm, x, y, w, h = f.frame
        if (not frm):
            x, y, w, h = 0, 0, 160, 160
        if (icon):            
            pixbuftools.fit_pbuf(pbuf, icon, 0, 0, 160, 160, True)#x, y, w, h)
            #pixbuftools.draw_pbuf(pbuf, icon, 0, 0)
            del icon
        if (frm):
            pixbuftools.draw_pbuf(pbuf, frm, 0, 0)

        return pbuf
        
