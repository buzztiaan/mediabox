from com import Widget, msgs
from utils import maemo
from ui import dialogs
from ui.Label import Label
from ui.Window import Window
from ui.Pixmap import text_extents
from theme import theme

import gobject


class _Notifier(Window):

    def __init__(self, parent):
    
        self.__parent = parent
        self.__timeout_handler = None
        
        Window.__init__(self, False)
        
        self.__lbl_message = Label("", theme.font_mb_notification,
                                   theme.color_mb_notification_text)
        self.__lbl_message.set_pos(10, 0)
        self.add(self.__lbl_message)
        
        
    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        screen.fill_area(0, 0, w, h, theme.color_mb_notification_background)

        
    def show_message(self, message):
    
        def on_timeout():
            self.set_visible(False)
            self.__timeout_handler = None
            

        win = self.__parent.get_window()
        w, h = win.get_size()
        x, y = win.get_pos()
        tw, th = text_extents(message, theme.font_mb_notification)
        self.__lbl_message.set_text(message)
        
        self.set_size(w, th)
        if (not self.is_visible()):
            self.set_pos(x, y)
            self.__lbl_message.set_size(w - 20, 0)
            self.set_visible(True)
        #end if

        if (self.__timeout_handler):
            gobject.source_remove(self.__timeout_handler)
        self.__timeout_handler = gobject.timeout_add(1500, on_timeout)
    


class NotificationService(Widget):
    """
    Service for sending notifications to the user.
    """

    def __init__(self):
    
        self.__progress_banner = None
        self.__notify_window = _Notifier(self)
       
        Widget.__init__(self)
      
        
    def handle_NOTIFY_SVC_SHOW_INFO(self, text):
    
        self.__notify_window.show_message(text)

        return 0

        #elif (msg == msgs.NOTIFY_SVC_SHOW_PROGRESS):
        #    amount, total, text = args
        #    self.__show_progress(amount, total, text)
        #    return 0
            
            
    def __show_banner(self, icon, text):
    
        if (maemo.IS_MAEMO):
            import hildon
            hildon.hildon_banner_show_information(self.get_window(), icon, text)
        else:
            import dbus
            bus = maemo.get_session_bus()
            obj = bus.get_object("org.freedesktop.Notifications", 
                                 "/org/freedesktop/Notifications")
            notify = dbus.Interface(obj, "org.freedesktop.Notifications")
            notify.Notify("abc", 3, "", "", text, [], [], -1)
            print "\n\n\n%s\n\n\n" % text


    def __show_progress(self, amount, total, text):
    
        if (maemo.IS_MAEMO):
            from ui.ProgressBanner import ProgressBanner
        
            if (self.__progress_banner):
                if (self.__progress_banner.get_total() != total):
                    self.__progress_banner.close()
                    self.__progress_banner = None

            if (not self.__progress_banner):
                self.__progress_banner = ProgressBanner(self.get_window(),
                                                        text, total)

            self.__progress_banner.set(amount)
            if (amount == total):
                self.__progress_banner.close()

        else:
            print "\n\n\n%d / %d - %s\n\n\n" % (amount, total, text)

