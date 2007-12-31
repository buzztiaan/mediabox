from viewers.Viewer import Viewer
from ui.KineticScroller import KineticScroller
from ImageItem import ImageItem
from ImageThumbnail import ImageThumbnail
from Image import Image
import theme

import gtk
import gobject
import os


_IMAGE_EXT = (".bmp", ".gif", ".jpg", ".jpeg", ".png", ".svg", ".xpm")


class ImageViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_image
    ICON_ACTIVE = theme.viewer_image_active
    PRIORITY = 30


    def __init__(self, esens):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
        self.__items = []
    
        Viewer.__init__(self, esens)
        
        self.__layout = esens
        
        # image
        self.__image = Image(esens)
        self.__image.add_observer(self.__on_observe_image)
        self.__image.set_pos(10, 10)
        self.__image.set_size(600, 380)
        self.add(self.__image)

        kscr = KineticScroller(self.__image)

        # not supported on maemo but nice to have elsewhere
        #kscr.connect("scroll-event", self.__on_mouse_wheel)


    def render_this(self):
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (not self.__is_fullscreen):
            screen.draw_rect(x + 8, y + 8, 600 + 4, 380 + 4, "#000000")
        

    def __on_mouse_wheel(self, src, ev):        
    
        if (ev.direction == gtk.gdk.SCROLL_UP):
            self.increment()
        elif (ev.direction == gtk.gdk.SCROLL_DOWN):
            self.decrement()


    def __on_observe_image(self, src, cmd, *args):
    
        if (cmd == src.OBS_BEGIN_LOADING):
            self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")                    
            
        elif (cmd == src.OBS_END_LOADING):
            self.update_observer(self.OBS_SHOW_PANEL)
           
        elif (cmd == src.OBS_PROGRESS):
            #self.update_observer(self.OBS_SHOW_PROGRESS, *args)
            pass
            

    def __is_image(self, uri):
        
        # ignore hidden files and 'cover.jpg'
        basename = os.path.basename(uri)
        if (basename.startswith(".") or basename == "cover.jpg"):
            return False
                
        ext = os.path.splitext(uri)[1].lower()
        return (ext in _IMAGE_EXT)


    def clear_items(self):
    
        self.__items = []


    def make_item_for(self, uri, thumbnailer):
    
        if (os.path.isdir(uri)): return
        if (not self.__is_image(uri)): return

        item = ImageItem(uri)
        if (not thumbnailer.has_thumbnail(uri)):
            thumbnailer.set_thumbnail_for_uri(uri, uri)
        
        tn = ImageThumbnail(thumbnailer.get_thumbnail(uri))
        item.set_thumbnail(tn)
        self.__items.append(item)
                        
        
    def load(self, item):

        self.__image.load(item.get_uri())
        self.set_title(os.path.basename(item.get_uri()))


    def do_increment(self):
    
        self.__image.zoom_in()
        
        
    def do_decrement(self):
    
        self.__image.zoom_out()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        

    def do_fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            self.__image.set_pos(0, 0)
            self.__image.set_size(800, 480)
            self.update_observer(self.OBS_FULLSCREEN)
        else:
            self.__image.set_pos(10, 10)
            self.__image.set_size(600, 380)
            self.update_observer(self.OBS_UNFULLSCREEN)            

