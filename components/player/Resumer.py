from com import Component, msgs
from mediabox import values

import os


_RESUME_FILE = os.path.join(values.USER_DIR, "resume")


class Resumer(Component):
    """
    Component for handling resuming of playback after startup.
    """

    def __init__(self):
    
        self.__current_file = None
        self.__current_pos = 0
        self.__is_playing = False
        self.__to_seek = 0
        
    
        Component.__init__(self)
        
        
    def handle_MEDIA_EV_LOADED(self, player, f):
    
        if (f != self.__current_file):
            self.__current_file = f
        
        
    def handle_MEDIA_EV_POSITION(self, pos, total):
    
        self.__current_pos = pos


    def handle_MEDIA_EV_PLAY(self):
    
        self.__is_playing = True
        if (self.__to_seek > 0):
            pos = self.__to_seek
            self.__to_seek = 0
            self.emit_message(msgs.MEDIA_ACT_SEEK, pos)

        
    def handle_MEDIA_EV_PAUSE(self):
    
        self.__is_playing = False
        
        
    def handle_MEDIA_EV_EOF(self):
    
        self.__is_playing = False


    def handle_COM_EV_APP_STARTED(self):
    
        # resume
        if (os.path.exists(_RESUME_FILE)):
            try:
                data = open(_RESUME_FILE, "r").read()
            except:
                return
        
            try:
                os.unlink(_RESUME_FILE)
            except:
                pass
                
            try:
                path, pos = data.split("\n")
                f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
                if (f):
                    self.emit_message(msgs.MEDIA_ACT_PREPARE, f)
                    self.__to_seek = int(pos)
            except:
                pass
        
        #end if
                
        
    def handle_COM_EV_APP_SHUTDOWN(self):

        if (self.__current_file):
            data = "\n".join([self.__current_file.full_path,
                              str(int(self.__current_pos))])
    
            try:
                open(_RESUME_FILE, "w").write(data)
            except:
                pass
        #end if

