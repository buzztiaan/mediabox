from com import Player, msgs
import mediaplayer
from utils import logging


class AudioPlayer(Player):

    def __init__(self):
    
        self.__player = None
        self.__context_id = 0
    
        Player.__init__(self)


    def get_mime_types(self):
    
        return ["audio/*"]

        
    def load(self, f):
    
        self.__player = mediaplayer.get_player_for_mimetype(f.mimetype)

        """
        uri = item.get_resource()
        if (not uri.startswith("/") and
            not "://localhost" in uri and
            not "://127.0.0.1" in uri):                    
            maemo.request_connection()
        #end if
        """
        
        uri = f.get_resource()
        try:
            self.__context_id = self.__player.load_audio(uri)
        except:
            logging.error("error loading media file: %s\n%s",
                          uri, logging.stacktrace())

