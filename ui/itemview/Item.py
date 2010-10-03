from utils.EventEmitter import EventEmitter
from ui.Pixmap import Pixmap


# maximum cache size
_CACHE_SIZE = 140

# list of tuples (item, pixmap)
_CACHE = []



class Item(EventEmitter):
    """
    Abstract base class for items.
    """

    EVENT_CLICKED = "event-clicked"

    __cache_counter = 0
    

    def __init__(self):
    
        self.__size = (240, 80)
        
        # a hilighted item is active (typically only one at a time)
        self.__is_hilighted = False
        # a marked item is marked, e.g. to indicate a cursor
        self.__is_marked = False
        # a selected item is selected for some action to be performed on it
        self.__is_selected = False
        
        self.__is_draggable = False
        
        # user-definable payload
        self.__payload = None

        # caching accelerates list rendering. if we don't cache every item,
        # we can accelerate longer lists
        self.__is_cachable = (self.__cache_counter % 2 == 0)
        self.__cache_counter += 1

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


    def set_payload(self, payload):
    
        self.__payload = payload


    def get_payload(self):
    
        return self.__payload


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


    def set_selected(self, v):
    
        self.__is_selected = v
        self._invalidate_cached_pixmap()
        
        
    def is_selected(self):
    
        return self.__is_selected


    def set_draggable(self, v):
    
        self.__is_draggable = v
        self._invalidate_cached_pixmap()
        
        
    def is_draggable(self):
    
        return self.__is_draggable


    def is_button(self):
        """
        Override this method in your subclass if you want button-like behavior.
        """
    
        return False


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

        # cache some items to accelerate rendering
        if (self.__is_cachable):
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

