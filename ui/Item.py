from Pixmap import Pixmap
import theme

import gtk
import gobject
import pango


class Item(gtk.gdk.Pixbuf):
    """
    Class for rendering a list item.
    """

    __defer_list = []   # this is a static variable shared by all instances


    def __init__(self, widget, width, height, icon, label, font, background = None):

        self.__canvas = Pixmap(None, width, height)
        

        self.__initialized = False
        self.__args = (widget, width, height, icon, label, font, background)
    
        gtk.gdk.Pixbuf.__init__(self, gtk.gdk.COLORSPACE_RGB, False, 8,
                                width, height)

        #if (not self.__defer_list):
        #    gobject.idle_add(self.__defer_handler)            
        #self.__defer_list.append(self)
        
        
    def __defer_handler(self):
    
        i = self.__defer_list.pop(0)
        i.get_width()
        if (self.__defer_list):
            return True
        else:
            return False


    def get_width(self):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.get_width(self)


    def subpixbuf(self, *args):
    
        if (not self.__initialized): self.__initialize()
        return gtk.gdk.Pixbuf.subpixbuf(self, *args)


    def __initialize(self):
    
        self.__initialized = True
        
        widget, width, height, icon, label, font, background = self.__args
    
        self.__canvas.fill_area(0, 0, width, height, "#ffffff")
    
        #cmap = widget.get_colormap()
        #gc = pmap.new_gc()

        #gc.set_foreground(cmap.alloc_color("#ffffff"))
        #pmap.draw_rectangle(gc, True, 0, 0, width, height)
                          
        x = 8

        if (background):
            self.__canvas.draw_subpixbuf(background, 0, 0, 0, 0, width, height)
            #pmap.draw_pixbuf(gc, background, 0, 0, 0, 0,
            #                 background.get_width(), background.get_height())
            
        if (icon):
            icon_y = (self.get_height() - icon.get_height()) / 2
            self.__canvas.draw_pixbuf(icon, 8, icon_y)
            #pmap.draw_pixbuf(gc, icon, 0, 0, 8, icon_y,
            #                 icon.get_width(), icon.get_height())
            x += icon.get_width()
        x += 8

        self.__canvas.draw_text(label, font, x, 8, theme.color_fg_item)

        #gc.set_foreground(cmap.alloc_color(theme.color_fg_item))

        #pc = widget.get_pango_context()
        #layout = pango.Layout(pc)
        #layout.set_font_description(font)
        #layout.set_text(label)
        #layout.set_width((width - 96) * pango.SCALE)
        #w, h = layout.get_pixel_size()
        #pmap.draw_layout(gc, x, (height - h) / 2, layout)
        
        #self.get_from_drawable(pmap, cmap, 0, 0, 0, 0, width, height)
        self.__canvas.render_on_pixbuf(self)
        
        #import gc; gc.collect()
