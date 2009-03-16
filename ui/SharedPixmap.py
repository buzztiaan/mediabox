"""
A shared pixmap for low memory consumption.
"""

from Pixmap import Pixmap


# increasing the cache size makes scrolling through items more fluent by
# sacrificing memory. decreasing the cache size makes scrolling more choppy.
_CACHE_SIZE = 5


class SharedPixmap(Pixmap):
    """
    A shared pixmap for implementing flyweight pattern stuff.
    """

    def __init__(self, w, h):
    
        self.__renderers = {}
        self.__cache = []
        self.__active = None
    
        Pixmap.__init__(self, None, w, h)
        
        
    def clear_all_renderers(self):
    
        self.__renderers.clear()
        
        
    def clear_renderer(self, ident):
    
        # 'if' is faster than 'try...except'
        if (ident in self.__renderers):
            del self.__renderers[ident]
            #print len(self.__renderers)
        
        
    def set_renderer(self, ident, renderer):
    
        self.__renderers[ident] = renderer
        
        
    def clear_cache(self):
    
        self.__cache = []
    
        
    def invalidate_cache(self, ident):
            
        self.__cache = [ (i, c) for i, c in self.__cache if i != ident ]
        self.__active = None            
        
        
    def prepare(self, ident):
    
        if (ident == self.__active): return
        
        from_cache = False
        # get from cache
        for c_ident, c_pmap in self.__cache:
            if (c_ident == ident):
                self.draw_pixmap(c_pmap, 0, 0)
                #print "from cache", ident
                from_cache = True
                break
        #end for

        # render if not in cache
        if (not from_cache):
            try:
                self.__renderers[ident]()

            except:
                import traceback; traceback.print_exc()

            else:                
                # put into cache
                self.__cache.append((ident, self.clone()))

                # prune cache                
                if (len(self.__cache) > _CACHE_SIZE):
                    self.__cache.pop(0)
        #end if
        
        self.__active = ident


    def swap(self, idx1, idx2):
    
        temp = self.__renderers[idx1]
        self.__renderers[idx1] = self.__renderers[idx2]
        self.__renderers[idx2] = temp
        
