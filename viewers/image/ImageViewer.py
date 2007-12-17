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
    IS_EXPERIMENTAL = False


    def __init__(self):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
        self.__items = []
    
        Viewer.__init__(self)
        
        box = gtk.VBox()        
        self.set_widget(box)
        
        # image
        self.__image = Image()
        self.__image.add_observer(self.__on_observe_image)
        self.__image.show()
        kscr = KineticScroller(self.__image)
        kscr.show()
        box.pack_start(kscr, True, True, 0)

        # not supported on maemo but nice to have elsewhere
        kscr.connect("scroll-event", self.__on_mouse_wheel)


    def __on_mouse_wheel(self, src, ev):        
    
        if (ev.direction == gtk.gdk.SCROLL_UP):
            self.increment()
        elif (ev.direction == gtk.gdk.SCROLL_DOWN):
            self.decrement()


    def __on_observe_image(self, src, cmd, *args):
    
        if (cmd == src.OBS_BEGIN_LOADING):
            #self.update_observer(self.OBS_SHOW_MESSAGE, "Loading...")                    
            pass
            
        elif (cmd == src.OBS_END_LOADING):
            #self.update_observer(self.OBS_SHOW_PANEL)
            pass
            
        elif (cmd == src.OBS_PROGRESS):
            self.update_observer(self.OBS_SHOW_PROGRESS, *args)
            

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


    def increment(self):
    
        self.__image.zoom_in()
        
        
    def decrement(self):
    
        self.__image.zoom_out()


    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, self.__items)
        

    def fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            self.update_observer(self.OBS_FULLSCREEN)
        else:
            self.update_observer(self.OBS_UNFULLSCREEN)
