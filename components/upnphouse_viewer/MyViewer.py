from com import Viewer, msgs
from mediabox import viewmodes
#from ui.KineticScroller import KineticScroller
#from SunClock import SunClock

#from ui.Image import Image
#from ui.VBox import VBox
#from ui.HBox import HBox
#from ui.ImageButton import ImageButton
#from ui.EventBox import EventBox
from GridList import GridList
from buttons.BinaryLight_Button import BinaryLight_Button
from buttons.DimmableLight_Button import DimmableLight_Button

import theme

import gtk
import gobject
import os
import time


_PATH = os.path.dirname(__file__)


class MyViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.upnphouse_viewer_house
    ICON_ACTIVE = theme.upnphouse_viewer_house_active
    PRIORITY = 100
   

    def __init__(self):
        
        self.__devices = {}

        self.__on = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "on.png"))

        #self.__on_picat = gtk.gdk.pixbuf_new_from_file(
        #    os.path.join(_PATH, "on_picat.png"))

        self.__off = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "off.png"))

        #self.__off_picat = gtk.gdk.pixbuf_new_from_file(
        #    os.path.join(_PATH, "off_picat.png"))

        Viewer.__init__(self)

        arrows = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "arrows.png"))

        arrows_off = gtk.gdk.pixbuf_new_from_file(
            os.path.join(_PATH, "arrows_off.png"))

        self.__Gridlist = GridList (arrows, arrows_off, items_per_row = 4)
        self.__Gridlist.set_visible(True)
        self.__Gridlist.set_geometry(10, 0, 780, 370)
        self.add(self.__Gridlist)


    def render_this(self):
        
        self.emit_event(msgs.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, "#FFFFFF")


    def handle_event(self, event, *args):
    
        #if (event == events.CORE_EV_APP_SHUTDOWN):
            #TODO unsubscribe from all devices
    
        if (event == msgs.SSDP_EV_DEVICE_DISCOVERED):
            uuid, device = args
            #if ( hasattr (device, 'hugos_attr') ):  #TODO better way to identify a upnp device
            self.__select_device(uuid, device)

        if (event == msgs.SSDP_EV_DEVICE_GONE ):
            uuid = args[0]
            self.__remove_device_button (uuid)

        
    def __select_device (self, uuid, device):

        if ( device.get_device_type() == "urn:schemas-upnp-org:device:BinaryLight:0.9" ) :
            self.__add_binary_light (uuid, device)
        elif ( device.get_device_type() == "urn:schemas-upnp-org:device:DimmableLight:1" ) :
            self.__add_dimmable_light (uuid, device)
        else:
            print 'None', device.get_device_type()


    def __add_binary_light (self, uuid, device):

        button = BinaryLight_Button ( device, self.__on, self.__off )
        self.__Gridlist.append_button (button)  #TODO put in place, database needed


    def __add_dimmable_light (self, uuid, device):

        button = DimmableLight_Button ( device, self.__on, self.__off, self.__Gridlist.open_dialog ) #TODO do async
        self.__Gridlist.append_button (button) #TODO put in place, database needed
        

    def __remove_device_button (self, uuid):

        index, position = self.__Gridlist.get_button_index_and_position_by_uuid ( uuid )

        if ( index >= 0 ) and ( position >= 0 ) :
            self.__Gridlist.remove_dialog_by_uuid (uuid)
            self.__Gridlist.remove_button_from_postion (index, position)


"""
    def __my_on_click (self, px, py, nothing):

        if (self.state1 == 0) :
            self.button1.set_images( self.__on, self.__on_picat )
            self.state1 = 1
        else :
            self.button1.set_images( self.__off, self.__off_picat )
            self.state1 = 0
"""
"""      
    def __tick(self):
    
        if (self.may_render()):
            today = time.strftime("%A - %x", time.localtime())
            self.update_observer(self.OBS_TITLE, today)
            self.update_observer(self.OBS_RENDER)
            return True
        else:
            self.__is_ticking = False
            return False
        
"""        
"""    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_HIDE_COLLECTION)"""
"""                   
        self.__tick()
        if (not self.__is_ticking):
            today = time.strftime("%A - %x", time.localtime())
            self.update_observer(self.OBS_TITLE, today)

            gobject.timeout_add(10000, self.__tick)
            self.__is_ticking = True
"""

