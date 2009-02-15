from com import Configurator, msgs
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.CheckBox import CheckBox
from ui.VBox import VBox
from utils import maemo
from utils import logging
from mediabox import config
from mediabox import values
from theme import theme

import commands
import os
import time


_LOG_LEVELS = {
    logging.OFF: "Off",
    logging.ERROR: "Error",
    logging.WARNING: "Warning",
    logging.INFO: "Info",
    logging.DEBUG: "Debug"
}


class Prefs(Configurator):

    ICON = theme.mb_viewer_prefs
    TITLE = "Debugging"


    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)


        lbl = Label("Log Level:",
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        log_level = logging.get_level()
        chbox = ChoiceBox("Off", logging.OFF,
                          "Error", logging.ERROR,
                          "Warning", logging.WARNING,
                          "Info", logging.INFO,
                          "Debug", logging.DEBUG)
        chbox.select_by_value(log_level)
        chbox.connect_changed(self.__on_select_log_level)
        self.__vbox.add(chbox)


        lbl = Label("Running since: %s" % time.asctime(time.localtime(values.START_TIME)),
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        lbl = Label("Device: %s" % maemo.get_product_code(),
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        lbl = Label("OS: %s" % commands.getoutput("uname -a"),
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)
        lbl.set_size(560, 0)

        self.__lbl_mem_size = Label("",
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(self.__lbl_mem_size)



    def __get_mem_size(self):
    
        import os
        pid = os.getpid()
        size = int(open("/proc/%d/status" % pid, "r").read().splitlines()[15].split()[1])
        size /= 1024.0
        logging.debug("current Resident Set Size: %0.02f MB", size)
        return size


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__lbl_mem_size.set_text("Resident Set Size: %0.02f MB" \
                                     % self.__get_mem_size())
        
        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_log_level(self, level):
        
        logging.set_level(level)

