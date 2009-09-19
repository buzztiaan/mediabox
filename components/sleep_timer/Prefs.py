from com import Configurator, msgs
from ClockSetter import ClockSetter
from ui.layout import HBox
from ui.layout import VBox
from ui.Image import Image
from ui.Label import Label
from ui.CheckBox import CheckBox
from ui.Button import Button
from theme import theme
from utils import logging
import config

import gobject
import time


class Prefs(Configurator):
    """
    Configurator for setting sleep and wake up times.
    """

    ICON = theme.prefs_sleep_timer
    TITLE = "Sleep Timer"
    DESCRIPTION = "Fall asleep and wake up with music"


    def __init__(self):
    
        self.__sleep_handler = None
        self.__wakeup_handler = None
        
        self.__sleep_time = config.get_sleep_time()
        self.__wakeup_time = config.get_wakeup_time()
        
    
        Configurator.__init__(self)
        
        self.__clock_setter = ClockSetter()
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)
        
        hbox = HBox()
        hbox.set_spacing(36)
        self.__vbox.add(hbox, True)

        img = Image(theme.mb_sleep_timer_sleep)
        hbox.add(img, False)
        
        chk = CheckBox(config.get_sleep())
        chk.connect_checked(self.__on_check_sleep)
        hbox.add(chk, True)
        lbl = Label("Fall asleep and stop playing at",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        chk.add(lbl)

        btn = Button("%02d:%02d" % self.__sleep_time)
        btn.set_size(160, 80)
        btn.connect_clicked(self.__on_set_sleep, btn)
        hbox.add(btn, False)

        hbox = HBox()
        hbox.set_spacing(36)
        self.__vbox.add(hbox, True)

        img = Image(theme.mb_sleep_timer_wakeup)
        hbox.add(img, False)

        chk = CheckBox(config.get_wakeup())
        chk.connect_checked(self.__on_check_wakeup)
        hbox.add(chk, True)
        lbl = Label("Wake up and start playing at",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        chk.add(lbl)

        btn = Button("%02d:%02d" % self.__wakeup_time)
        btn.set_size(160, 80)
        btn.connect_clicked(self.__on_set_wakeup, btn)
        hbox.add(btn, False)

        lbl = Label("MediaBox will start playing the file that is selected " \
                    "at the moment of waking up.",
                    theme.font_mb_plain, theme.color_mb_listitem_text)        
        self.__vbox.add(lbl, True)


        # status icon
        self.__status_icon_sleep = Image(theme.mb_status_sleep)
        self.__status_icon_sleep.connect_clicked(self.__on_clicked_status_icon)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)


    def __update_status_icons(self):
    
        if (self.__sleep_handler or self.__wakeup_handler):
            self.emit_message(msgs.UI_ACT_SET_STATUS_ICON,
                              self.__status_icon_sleep)
        else:
            self.emit_message(msgs.UI_ACT_UNSET_STATUS_ICON,
                              self.__status_icon_sleep)


    def __on_clicked_status_icon(self):
    
        if (self.__sleep_handler):
            sleep_time = "%02d:%02d" % self.__sleep_time
        else:
            sleep_time = "- not set -"
        if (self.__wakeup_handler):
            wakeup_time = "%02d:%02d" % self.__wakeup_time
        else:
            wakeup_time = "- not set -"
            
        msg = "Fall asleep at:\t %s\n" \
              "\n" \
              "Wake up at:\t\t %s" % (sleep_time, wakeup_time)

        self.call_service(msgs.DIALOG_SVC_INFO, "Sleep and Wake Up Times", msg)

        
    def __on_check_sleep(self, value):
    
        if (self.__sleep_handler):
            gobject.source_remove(self.__sleep_handler)
            self.__sleep_handler = None

        if (value):
            now = time.time()
            then = self.__find_next_occurence(*self.__sleep_time)
            delta = int((then - now) * 1000)
            self.__sleep_handler = gobject.timeout_add(delta, self.__fall_asleep)
        
        config.set_sleep(value)
        self.__update_status_icons()    
        
        
    def __on_check_wakeup(self, value):
    
        if (self.__wakeup_handler):
            gobject.source_remove(self.__wakeup_handler)
            self.__wakeup_handler = None

        if (value):
            now = time.time()
            then = self.__find_next_occurence(*self.__wakeup_time)
            delta = int((then - now) * 1000)
            self.__wakeup_handler = gobject.timeout_add(delta, self.__wakeup)

        config.set_wakeup(value)
        self.__update_status_icons()


    def __on_set_sleep(self, btn):
    
        self.__clock_setter.set_time(*self.__sleep_time)
        self.call_service(msgs.DIALOG_SVC_CUSTOM, theme.mb_sleep_timer_sleep,
                          "Set Sleep Time", self.__clock_setter)
        self.__sleep_time = self.__clock_setter.get_time()
        config.set_sleep_time(*self.__sleep_time)
        btn.set_text("%02d:%02d" % self.__sleep_time)
        if (self.__sleep_handler):
            self.__on_check_sleep(True)


    def __on_set_wakeup(self, btn):
    
        self.__clock_setter.set_time(*self.__wakeup_time)
        self.call_service(msgs.DIALOG_SVC_CUSTOM, theme.mb_sleep_timer_wakeup,
                          "Set Wake Up Time", self.__clock_setter)
        self.__wakeup_time = self.__clock_setter.get_time()
        config.set_wakeup_time(*self.__wakeup_time)
        btn.set_text("%02d:%02d" % self.__wakeup_time)
        if (self.__wakeup_handler):
            self.__on_check_wakeup(True)


    def __fall_asleep(self):
    
        self.__sleep_handler = None
        logging.debug("sleep timer falling asleep")
        self.emit_message(msgs.MEDIA_ACT_STOP)
        self.__on_check_sleep(True)
        
        
    def __wakeup(self):
    
        self.__wakeup_handler = None
        logging.debug("wakeup timer waking up")
        self.emit_message(msgs.MEDIA_ACT_PLAY)
        self.__on_check_wakeup(True)


    def __find_next_occurence(self, h, m):
    
        now = time.time()
        now_tuple = list(time.localtime(now))
        now_tuple[3] = h
        now_tuple[4] = m
        now_tuple[5] = 0
        
        seconds = time.mktime(tuple(now_tuple))
        if (seconds <= now):
            seconds += 24 * 3600
            
        return seconds


    def handle_CORE_EV_APP_STARTED(self):
    
        self.__update_status_icons()
        self.__on_check_sleep(config.get_sleep())
        self.__on_check_wakeup(config.get_wakeup())

