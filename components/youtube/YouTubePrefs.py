from com import Configurator
from ui.itemview import ThumbableGridView
from ui.itemview import LabelItem
from ui.itemview import OptionItem
from theme import theme
import config


class YouTubePrefs(Configurator):

    ICON = theme.youtube_folder
    TITLE = "YouTube"
    DESCRIPTION = "Configure the YouTube browser"
    

    def __init__(self):
    
        Configurator.__init__(self)
        
        self.__list = ThumbableGridView()
        self.add(self.__list)
        
        lbl = LabelItem("What should MediaBox do if multiple versions of a " \
                        "video are available:")
        self.__list.append_item(lbl)
        
        chbox = OptionItem("let me choose", config.QUALITY_ASK,
                      "automatically choose high quality", config.QUALITY_HIGH,
                      "automatically choose low quality", config.QUALITY_LOW)
        chbox.connect_changed(self.__on_select_quality)
        chbox.select_by_value(config.get_quality())
        self.__list.append_item(chbox)


    def __on_select_quality(self, q):
    
        config.set_quality(q)
