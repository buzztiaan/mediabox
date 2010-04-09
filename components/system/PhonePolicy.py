from com import Component, msgs


class PhonePolicy(Component):
    """
    Component for pausing playback during a phone call.
    """

    def __init__(self):

        self.__is_playing = False
        self.__was_playing = False

        Component.__init__(self)


    def handle_MEDIA_EV_PLAY(self):

        self.__is_playing = True


    def handle_MEDIA_EV_PAUSE(self):

        self.__is_playing = False


    def handle_MEDIA_EV_EOF(self):

        self.__is_playing = False


    def handle_SYSTEM_EV_PHONE_RINGING(self):

        self.__was_playing = self.__is_playing
        if (self.__is_playing):
            self.emit_message(msgs.MEDIA_ACT_PAUSE)


    def handle_SYSTEM_EV_PHONE_DIALING(self):

        self.__was_playing = self.__is_playing
        if (self.__is_playing):
            self.emit_message(msgs.MEDIA_ACT_PAUSE)


    def handle_SYSTEM_EV_PHONE_HANGUP(self):

        if (self.__was_playing):
            self.emit_message(msgs.MEDIA_ACT_PLAY)

