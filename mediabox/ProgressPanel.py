from Panel import Panel
from ui.Label import Label
from ui.ProgressBar import ProgressBar
import theme


class ProgressPanel(Panel):

    def __init__(self, esens):
       
        Panel.__init__(self, esens, False)
        
        self.__progress = ProgressBar(esens, False)
        self.add(self.__progress)
        w, h = self.__progress.get_size()
        self.__progress.set_pos(800 - 20 - w, (80 - h) / 2)

        self.__progress_label = Label(esens, "", theme.font_headline,
                                                 theme.color_fg_panel_text)
        self.add(self.__progress_label)
        self.__progress_label.set_pos(20, 20)
        self.__progress_label.set_size(800 - 40 - w - 20, 0)


    def set_progress(self, text, value, total):
    
        if (total > 0):
            self.__progress_label.set_text(text)
            self.__progress.set_position(value, total)

