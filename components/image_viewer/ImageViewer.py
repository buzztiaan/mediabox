from com import Viewer, msgs

from ui.ImageButton import ImageButton
from mediabox import viewmodes
from ImageThumbnail import ImageThumbnail
import theme

import gtk
import gobject
import os


class ImageViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.mb_viewer_image
    ICON_ACTIVE = theme.mb_viewer_image_active
    PRIORITY = 30


    def __init__(self):
            
        self.__is_fullscreen = False
            
        self.__uri = ""
        self.__thumbnails_needed = []
        self.__items = []
        self.__current_item = -1
    
        Viewer.__init__(self)
        
        # image
        self.__image_widget = None
       

        # toolbar
        self.__tbset = []
        for icon1, icon2, action in [
          (theme.btn_previous_1, theme.btn_previous_2, self.__previous_image),
          (theme.btn_next_1, theme.btn_next_2, self.__next_image)]:
            btn = ImageButton(icon1, icon2)
            btn.connect_clicked(action)
            self.__tbset.append(btn)
        self.set_toolbar(self.__tbset)


    def render_this(self):
        
        if (not self.__image_widget):
            self.__image_widget = self.call_service(
                                      msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET,
                                      self, "image/*")
            self.add(self.__image_widget)
            self.set_toolbar(self.__image_widget.get_controls() + self.__tbset)
        
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        self.__image_widget.set_geometry(0, 0, w, h)


    def handle_event(self, event, *args):
               
        if (event == msgs.MEDIASCANNER_EV_SCANNING_FINISHED):
            self.__update_media()

        if (self.is_active()):
            if (event == msgs.CORE_ACT_LOAD_ITEM):
                idx = args[0]
                self.__load(self.__items[idx])
        
            if (event == msgs.HWKEY_EV_INCREMENT):
                self.__zoom_in()
                
            elif (event == msgs.HWKEY_EV_DECREMENT):
                self.__zoom_out()
                
            elif (event == msgs.HWKEY_EV_ENTER):
                self.__next_image()
                
            elif (event == msgs.HWKEY_EV_FULLSCREEN):
                self.__on_fullscreen()
                
        #end if        
          
            
    def __get_name(self, uri):
    
        basename = os.path.basename(uri)
        name = os.path.splitext(basename)[0]
        name = name.replace("_", " ")
        
        return name
            
            
    def __previous_image(self):

        if (not self.__items): return
        
        idx = self.__current_item
        if (idx == -1): idx = 0
        idx -= 1
        if (idx == -1): idx = len(self.__items) - 1
        #self.__image.slide_from_left()
        self.emit_event(msgs.CORE_ACT_SELECT_ITEM, idx)


    def __next_image(self):

        if (not self.__items): return
                    
        idx = self.__current_item       
        idx += 1
        idx %= len(self.__items)
        #self.__image.slide_from_right()
        self.emit_event(msgs.CORE_ACT_SELECT_ITEM, idx)
            

    def clear_items(self):
    
        self.__items = []



    def __load_thumbnails(self, tn_list):
    
        def on_thumbnail(thumb, tn, files):
            tn.set_thumbnail(thumb)
            tn.invalidate()
            self.emit_event(msgs.CORE_ACT_RENDER_ITEMS)
            
            if (tn_list):
                f, tn = tn_list.pop(0)
                self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                                  on_thumbnail, tn, tn_list)
        
        f, tn = tn_list.pop(0)
        self.call_service(msgs.MEDIASCANNER_SVC_SCAN_FILE, f,
                          on_thumbnail, tn, tn_list)


    def __update_media(self):
    
        media = self.call_service(msgs.MEDIASCANNER_SVC_GET_MEDIA,
                                  ["image/"])
        self.__items = []
        thumbnails = []
        self.__thumbnails_needed = []
        self.__current_item = -1
        for f in media:
            thumb = self.call_service(msgs.MEDIASCANNER_SVC_GET_THUMBNAIL, f)
            tn = ImageThumbnail(thumb)
            self.__items.append(f)
            thumbnails.append(tn)

            if (not os.path.exists(thumb)):
                self.__thumbnails_needed.append((f, tn))
        #end for
        self.set_collection(thumbnails)


    def __load(self, item):

        def f():
            self.__image_widget.load(item)        
            #self.__label.set_text(self.__get_name(uri))
            self.__current_item = self.__items.index(item)
            #self.__image.slide_from_right()
            self.set_title(self.__get_name(item.name))
            self.set_info("%d / %d" % (self.__current_item + 1, len(self.__items)))
            
        gobject.idle_add(f)


       
    
    def __zoom_in(self):
    
        self.__image_widget.increment()


    def __zoom_out(self):
    
        self.__image_widget.decrement()


    def __on_fullscreen(self):
        
        self.__is_fullscreen = not self.__is_fullscreen        
        
        if (self.__is_fullscreen):
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.FULLSCREEN)
            self.render()
        else:
            self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NORMAL)
            self.render()
            gobject.idle_add(self.emit_event, msgs.CORE_ACT_RENDER_ALL)



    def show(self):
    
        Viewer.show(self)
        if (self.__thumbnails_needed):
            self.__load_thumbnails(self.__thumbnails_needed)

