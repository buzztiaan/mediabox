from Panel import Panel
import theme

import gtk


class ProgressPanel(Panel):

    def __init__(self):
       
        Panel.__init__(self, False)
        
        self.__progress_label = gtk.Label("")
        self.__progress_label.modify_font(theme.font_headline)
        self.__progress_label.modify_fg(gtk.STATE_NORMAL, theme.panel_foreground)
        self.__progress_label.set_alignment(1.0, 0.5)
        self.__progress_label.show()
        self.box.add(self.__progress_label)


    def set_progress(self, value, total):
    
        if (total > 0):
            self.__progress_label.set_text("%d %%" % (100 * value / float(total)))

