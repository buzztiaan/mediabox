from ui.layout import HBox
from ui.SequenceButton import SequenceButton
import config
from theme import theme


class ShuffleBar(HBox):

    def __init__(self):
    
        HBox.__init__(self)
        self.set_spacing(32)

        self.__btn_repeat = SequenceButton(
             [(theme.mb_repeat_none, config.REPEAT_MODE_NONE),
              (theme.mb_repeat_one, config.REPEAT_MODE_ONE),
              (theme.mb_repeat_all, config.REPEAT_MODE_ALL)])
        self.__btn_repeat.connect_changed(self.__on_change_repeat_mode)
        self.__btn_repeat.set_size(48, 48)
        self.add(self.__btn_repeat)

        self.__btn_shuffle = SequenceButton(
             [(theme.mb_shuffle_none, config.SHUFFLE_MODE_NONE),
              (theme.mb_shuffle_one, config.SHUFFLE_MODE_ONE)])
        self.__btn_shuffle.connect_changed(self.__on_change_shuffle_mode)
        self.__btn_shuffle.set_size(48, 48)
        self.add(self.__btn_shuffle)
        
        
    def __on_change_repeat_mode(self, mode):
    
        config.set_repeat_mode(mode)


    def __on_change_shuffle_mode(self, mode):
    
        config.set_shuffle_mode(mode)


    def render_this(self):
    
        HBox.render_this(self)
    
        repeat_mode = config.repeat_mode()
        self.__btn_repeat.set_value(repeat_mode)

        shuffle_mode = config.shuffle_mode()
        self.__btn_shuffle.set_value(shuffle_mode)

