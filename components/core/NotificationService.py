from com import Widget, msgs
from utils import maemo
from ui import dialogs

import gtk


class NotificationService(Widget):
    """
    Service for sending notifications to the user.
    """

    def __init__(self):
    
        self.__progress_banner = None
       
        Widget.__init__(self)
        
        
    def handle_message(self, msg, *args):
    
        if (msg == msgs.NOTIFY_SVC_SHOW_INFO):
            text = args[0]
            try:
                img = gtk.Image()
                img.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
                self.__show_banner(gtk.STOCK_DIALOG_INFO, text)
            except:
                pass

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

