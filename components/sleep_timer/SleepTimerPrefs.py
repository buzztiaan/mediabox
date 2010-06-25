from com import Configurator, msgs
from ClockSetter import ClockSetter
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import ButtonItem
from ui.itemview import CheckBoxItem
from theme import theme
from utils import logging
import config

import gobject
import time


class SleepTimerPrefs(Configurator):
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
                
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        #img = Image(theme.mb_sleep_timer_sleep)
        #hbox.add(img, False)
        
        chk = CheckBoxItem("Fall asleep and stop playing at", config.get_sleep())
        chk.connect_checked(self.__on_check_sleep)
        self.__list.append_item(chk)

        btn = ButtonItem("%02d:%02d" % self.__sleep_time)
        btn.connect_clicked(self.__on_set_sleep, btn)
        self.__list.append_item(btn)

        #img = Image(theme.mb_sleep_timer_wakeup)
        #hbox.add(img, False)

        chk = CheckBoxItem("Wake up at and start playing at", config.get_wakeup())
        chk.connect_checked(self.__on_check_wakeup)
        self.__list.append_item(chk)

        btn = ButtonItem("%02d:%02d" % self.__wakeup_time)
        btn.connect_clicked(self.__on_set_wakeup, btn)
        self.__list.append_item(btn)

        lbl = LabelItem("MediaBox will start playing the file that is " \
                        "selected at the moment of waking up.")
        lbl.set_icon(theme.mb_sleep_timer_wakeup)
        self.__list.append_item(lbl)


        # status icon
        #self.__status_icon_sleep = Image(theme.mb_status_sleep)
        #self.__status_icon_sleep.connect_clicked(self.__on_clicked_status_icon)
    

    """
    def __update_status_icons(self):
    
        if (self.__sleep_handler or self.__wakeup_handler):
            self.emit_message(msgs.UI_ACT_SET_STATUS_ICON,
                              self.__status_icon_sleep)
        else:
            self.emit_message(msgs.UI_ACT_UNSET_STATUS_ICON,
                              self.__status_icon_sleep)
    """

    """
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
    """
        
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
        #self.__update_status_icons()    
        
        
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
        #self.__update_status_icons()


    def __on_set_sleep(self, btn):
    
        dlg = ClockSetter()
        dlg.set_time(*self.__sleep_time)
        dlg.run()
        self.__sleep_time = dlg.get_time()
        config.set_sleep_time(*self.__sleep_time)
        btn.set_text("%02d:%02d" % self.__sleep_time)

        idx = self.__list.get_items().index(btn)
        self.__list.invalidate_item(idx)

        if (self.__sleep_handler):
            self.__on_check_sleep(True)


    def __on_set_wakeup(self, btn):

        dlg = ClockSetter()
        dlg.set_time(*self.__wakeup_time)
        dlg.run()
        self.__wakeup_time = dlg.get_time()
        config.set_wakeup_time(*self.__wakeup_time)
        btn.set_text("%02d:%02d" % self.__wakeup_time)

        idx = self.__list.get_items().index(btn)
        self.__list.invalidate_item(idx)

        if (self.__wakeup_handler):
            self.__on_check_wakeup(True)
        

    def __fall_asleep(self):
    
        self.__sleep_handler = None
        logging.debug("sleep timer falling asleep")
        self.emit_message(msgs.MEDIA_ACT_PAUSE)
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


    def handle_COM_EV_APP_STARTED(self):
    
        #self.__update_status_icons()
        self.__on_check_sleep(config.get_sleep())
        self.__on_check_wakeup(config.get_wakeup())

