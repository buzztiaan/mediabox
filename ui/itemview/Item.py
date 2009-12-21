from utils.EventEmitter import EventEmitter
from ui.Pixmap import Pixmap


# maximum cache size
_CACHE_SIZE = 20

# list of tuples (item, pixmap)
_CACHE = []



class Item(EventEmitter):
    """
    Abstract base class for items.
    """

    EVENT_CLICKED = "event-clicked"
    

    def __init__(self):
    
        self.__size = (240, 80)
        self.__is_hilighted = False
        self.__is_marked = False
        self.__is_draggable = False

        EventEmitter.__init__(self)


    def connect_clicked(self, cb, *args):
    
        self._connect(self.EVENT_CLICKED, cb, *args)


    def get_letter(self):
    
        return ""
        

    def get_size(self):
    
        return self.__size
        
        
    def set_size(self, w, h):
    
        self.__size = (max(60, w), max(60, h))
        self._invalidate_cached_pixmap()


    def set_hilighted(self, v):
    
        self.__is_hilighted = v
        self._invalidate_cached_pixmap()
        
        
    def is_hilighted(self):
    
        return self.__is_hilighted


    def set_marked(self, v):
    
        self.__is_marked = v
        self._invalidate_cached_pixmap()
        
        
    def is_marked(self):
    
        return self.__is_marked


    def set_draggable(self, v):
    
        self.__is_draggable = v
        
        
    def is_draggable(self):
    
        return self.__is_draggable


    def render_at(self, cnv, x, y):

        w, h = self.get_size()
        if (self.is_marked()):
            color = "#ff0000"
        elif (self.is_hilighted()):
            color = "#0000ff"
        else:
            color = "#aaaaaa"
            
        cnv.fill_area(x, y, w, h, "#ffffff")
        cnv.fill_area(x + 4, y + 4, w - 8, h - 8, color)


    def click_at(self, px, py):
        """
        Override this method to handle clicks on the item.
        """
    
        self.emit_event(self.EVENT_CLICKED)


    def tap_and_hold(self, px, py):
        """
        Override this method to handle tap-and-hold on the item.
        """

        pass



    def _get_cached_pixmap(self):
        """
        Returns a cached pixmap object for this item, and whether it was newly
        created.
        
        @return: tuple of (pixmap, is_new)
        """
        
        w, h = self.get_size()
        
        cnt = 0
        for ident, pmap in _CACHE:
            if (ident == self):
                if ((w, h) == pmap.get_size()):
                    # cached pixmap is OK
                    return (pmap, False)

                else:
                    # remove pixmap from cache
                    del _CACHE[cnt]
                    break
            #end if
            cnt += 1
        #end for
        
        # pixmap is not cached yet; create a new one
        pmap = Pixmap(None, w, h)
        _CACHE.append((self, pmap))
        
        # remove old pixmaps from cache
        while (len(_CACHE) > _CACHE_SIZE):
            del _CACHE[0]

        return (pmap, True)


    def _invalidate_cached_pixmap(self):
        """
        Invalidates the cached pixmap for this item, if any.
        """
        
        cnt = 0
        for ident, pmap in _CACHE:
            if (ident == self):
                del _CACHE[cnt]
            cnt += 1
        #end for

