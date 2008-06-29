from com import Viewer, events
from mediabox import viewmodes
#from ui.KineticScroller import KineticScroller
#from SunClock import SunClock

from ui.Image import Image
from ui.VBox import VBox
from ui.HBox import HBox
from ui.ImageButton import ImageButton
from ui.EventBox import EventBox
from GridList import GridList
from GridButton import GridButton

import theme

import gtk
import gobject
import os
import time


_PATH = os.path.dirname(__file__)


class MyViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_upnphouse
    ICON_ACTIVE = theme.viewer_upnphouse_active
    PRIORITY = 100
   

    def __init__(self):
        
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
        self.__Gridlist.set_geometry(10, 40, 780, 370)
        self.add(self.__Gridlist)

        button1 = GridButton ( 'Hola', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button1)

        button2 = GridButton ( 'Adeu', self.__on, self.__off, 1 )
        self.__Gridlist.add_button (button2,0,0)

        button3 = GridButton ( 'Que passa', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button3)

        button4 = GridButton ( 'Tio', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button4)

        button5 = GridButton ( 'Mola', self.__on, self.__off, 1 )
        self.__Gridlist.add_button (button5,0,1)

        button6 = GridButton ( 'Nen', self.__on, self.__off, 1 )
        self.__Gridlist.append_button (button6)

        button1 = GridButton ( 'A veure', self.__on, self.__off, 0 )
        self.__Gridlist.add_button (button1,1,0)

        button2 = GridButton ( 'que passa neng!', self.__on, self.__off, 1 )
        self.__Gridlist.append_button (button2)

        button3 = GridButton ( 'amb aixo', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button3)

        button4 = GridButton ( 'veurem', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button4)

        button1 = GridButton ( 'A veure', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button1)

        button2 = GridButton ( 'soc jo', self.__on, self.__off, 1 )
        self.__Gridlist.add_button (button2, 0, 10)

        button3 = GridButton ( 'amb aixo', self.__on, self.__off, 0 )
        self.__Gridlist.append_button (button3)

        button4 = GridButton ( 'es aquest 1-3', self.__on, self.__off, 0 )
        self.__Gridlist.add_button (button4,0,1)

    def render_this(self):
        
        self.emit_event(events.CORE_ACT_VIEW_MODE, viewmodes.NO_STRIP)

        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(x, y, w, h, "#FFFFFF")

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

