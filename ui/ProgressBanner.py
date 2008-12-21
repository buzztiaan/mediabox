from utils import threads

import gtk
import hildon


class ProgressBanner(object):

    def __init__(self, parent, label, total):

        self.__amount = 0
        self.__total = total
        self.__progress = gtk.ProgressBar()
        self.__banner = hildon.hildon_banner_show_progress(
            parent, self.__progress, label)


    def close(self):

        self.__banner.destroy()


    def set(self, amount):

        self.__amount = min(self.__total, amount)
        fraction = self.__amount / float(self.__total)
        self.__progress.set_fraction(fraction)
        threads.wait_for(lambda :not gtk.events_pending())


    def get(self):

        return self.__amount
        
        
    def get_total(self):
    
        return self.__total


    def progress(self, amount):

        self.set(self.__amount + amount)
