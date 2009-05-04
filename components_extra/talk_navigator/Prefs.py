from com import Configurator, msgs
from ui.Button import Button
from ui.Label import Label
from ui.ChoiceBox import ChoiceBox
from ui.Slider import Slider
from ui.HBox import HBox
from ui.VBox import VBox
import config
from theme import theme


class Prefs(Configurator):

    ICON = theme.youtube_device
    TITLE = "Talk Navigation"
    DESCRIPTION = "Configure the Talk Navigation plugin"


    def __init__(self):

        Configurator.__init__(self)
        
        self.__vbox = VBox()
        self.__vbox.set_spacing(12)
        self.add(self.__vbox)
        
        lbl = Label("Voice:",
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        hbox = HBox()
        hbox.set_size(600, 80)
        self.__vbox.add(hbox)

        current_voice = config.get_voice()
        chbox = ChoiceBox("Male A", "m1",
                          "Male B", "m2",
                          "Male C", "m3",
                          "Male D", "m4",
                          "Female A", "f1",
                          "Female B", "f2",
                          "Female C", "f3",
                          "Female D", "f4",
                          "Whisper", "whisper")
        chbox.select_by_value(current_voice)
        chbox.connect_changed(self.__on_select_voice)
        hbox.add(chbox)

        button = Button("Test Voice")
        button.connect_clicked(self.__on_test_voice)
        hbox.add(button)

        pitch = config.get_pitch()
        self.__lbl_pitch = Label("Pitch: %d" % pitch,
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(self.__lbl_pitch)
        
        slider = Slider(theme.mb_slider_gauge)
        slider.set_background_color(theme.color_mb_gauge)
        slider.connect_value_changed(self.__on_set_pitch)
        slider.set_value(pitch / 99.0)
        slider.set_size(600, 40)
        self.__vbox.add(slider)


        speed = config.get_speed()
        self.__lbl_speed = Label("Words per minute: %d" % speed,
                    theme.font_mb_plain, theme.color_mb_listitem_text)
        self.__vbox.add(self.__lbl_speed)
        
        slider = Slider(theme.mb_slider_gauge)
        slider.set_background_color(theme.color_mb_gauge)
        slider.connect_value_changed(self.__on_set_speed)
        slider.set_value((speed - 80) / 290.0)
        slider.set_size(600, 40)
        self.__vbox.add(slider)


        lbl = Label("Talk Navigation powered by espeak - http://espeak.sourceforge.net",
                    theme.font_mb_tiny, theme.color_mb_listitem_text)
        self.__vbox.add(lbl)

        



    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        self.__vbox.set_geometry(32, 32, w - 64, h - 64)
        screen.fill_area(x, y, w, h, theme.color_mb_background)
        
        
    def __on_select_voice(self, voice):
    
        config.set_voice(voice)


    def __on_set_pitch(self, v):
    
        pitch = int(v * 99)
        config.set_pitch(pitch)
        self.__lbl_pitch.set_text("Pitch: %d" % pitch)


    def __on_set_speed(self, v):
    
        speed = 80 + int (v * 290)
        config.set_speed(speed)
        self.__lbl_speed.set_text("Words per minute: %d" % speed)


    def __on_test_voice(self):
    
        self.emit_message(msgs.TALKNAV_ACT_SAY, "The quick brown fox jumped over the fence.")
