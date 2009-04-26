from com import Component
from mediabox import values
import config

import os
import time
import gobject


# unicode ranges of non-latin characters for detecting language
_UNICODE_RANGES = [
    (0x4e00, 0x9fc3, "zh"),
    (0x0400, 0x04ff, "ru"),
]


# timeout for the activation button in seconds
_ACTIVATION_TIMEOUT = 0.5


class TalkNavigator(Component):
    """
    Component for voice navigation. This way I don't have to switch on the
    TV anymore when I want to play some music on my HTPC. :)
    
    It detects and reads English, Russian, and Mandarin Chinese by using the
    espeak engine.
    """

    def __init__(self):
    
        self.__menu_button_times = []
        self.__is_active = False
        self.__stop_handler = None
    
        Component.__init__(self)


    def __toggle_activation(self):
    
        self.__is_active = not self.__is_active
        if (self.__is_active):
            self.__say("activated Talk Navigation")
        else:
            self.__say("dee-activated Talk Navigation")


    def __say(self, text):

        if (not text): return
        
        text = text.replace("_", " ") \
                    .replace("`", "'") \
                    .replace("$", "\\$") \
                    .replace("\"", "\\\"") \
                    .replace("&", " and ") \
                    .replace("w/ ", "with ") \
                    .replace("w/o ", "without ") \
                    .replace("- ", ": ") \
                    .replace(".jpg", ".jaypeg") \
                    .replace(".mpg", ".empeg") \
                    .replace(" feat. ", " featuring ") \
                    .replace("EP", "eehpeeh") \
                    .replace("km/h", "kilometres per hour") \
                    .replace("/", ": ")
                
        lang = self.__find_language_speaker(text)
        os.system("killall espeak 2>/dev/null")
        os.system("aoss espeak -a200 -v%s+%s -p%d -s%d \"%s\" &" \
                    % (lang, config.get_voice(),
                        config.get_pitch(),
                        config.get_speed(),
                        text))
    
                
        
    def __find_language_speaker(self, text):
    
        for c in unicode(text):
            code = ord(c)
            for a, b, cc in _UNICODE_RANGES:
                if (a <= code <= b):
                    return cc
            #end for
        #end for
        
        return "en"


    def handle_CORE_EV_APP_STARTED(self):
    
        self.__say("Welcome to %s With Talk Navigation! " \
                   "Press Menu button three times for Talk Navigation!" \
                   % values.NAME)


    def handle_TALKNAV_ACT_SAY(self, text):
    
        self.__say(text)


    def handle_UI_ACT_TALK(self, text):
    
        def f(text):
            self.__say(text)
            self.__stop_handler = None
    
        if (self.__is_active and text):
            if (not self.__stop_handler):
                self.__say(text)
                self.__stop_handler = gobject.timeout_add(500, f, "")
                
            else:
                if (int(time.time() * 10) % 10 == 0): self.__say(text[0])
                gobject.source_remove(self.__stop_handler)

                self.__stop_handler = gobject.timeout_add(500, f, text)


    def handle_INPUT_EV_SWITCH_TAB(self):
    
        now = time.time()
        
        if (not self.__menu_button_times):
            self.__menu_button_times.append(now)
            
        elif (now < self.__menu_button_times[-1] + _ACTIVATION_TIMEOUT):
            self.__menu_button_times.append(now)
            
        else:
            self.__menu_button_times = [now]
            
        if (len(self.__menu_button_times) == 3):
            self.__toggle_activation()
            self.__menu_button_times = []

