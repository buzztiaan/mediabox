"""
This package contains the media player backends.
"""

from DummyPlayer import DummyPlayer
from MPlayer import MPlayer
from OSSOPlayer import OSSOPlayer
from utils import maemo
from utils import logging

import os


_MPLAYER = MPlayer()
_OMS = OSSOPlayer()
_DUMMY = DummyPlayer()

_PLAYERS = [_MPLAYER, _OMS, _DUMMY]

_current_player = _DUMMY



AUDIO_FORMATS = { ".aac":           _OMS,
                  ".flac":          _MPLAYER,
                  ".m3u":           _OMS,
                  ".m4a":           _OMS,
                  ".mp2":           _OMS,
                  ".mp3":           _OMS,
                  ".ogg":           _MPLAYER,
                  ".pls":           _OMS,
                  ".ram":           _OMS,
                  ".rm":            _OMS,
                  ".wav":           _OMS,
                  ".wma":           _OMS,
                  ".wpl":           _OMS,
                  "unknown-stream": _MPLAYER }

VIDEO_FORMATS = { ".3gp":           _OMS,
                  ".asf":           _MPLAYER,
                  ".avi":           _MPLAYER,
                  ".flv":           _MPLAYER,
                  ".m4v":           _OMS,
                  ".mov":           _MPLAYER,
                  ".mp4":           _OMS,
                  ".mpeg":          _MPLAYER,
                  ".mpg":           _MPLAYER,
                  ".rmvb":          _OMS,
                  ".theora":        _MPLAYER,
                  ".wmv":           _MPLAYER,
                  "unknown-stream": _MPLAYER }

if (not maemo.IS_MAEMO):
    for k in AUDIO_FORMATS: AUDIO_FORMATS[k] = _MPLAYER
    for k in VIDEO_FORMATS: VIDEO_FORMATS[k] = _MPLAYER    



def get_player_for_uri(uri):
    """
    Returns the appropriate player for the given uri or returns None
    if no appropriate player was found.
    """
    
    mapping = {}
    mapping.update(AUDIO_FORMATS)
    mapping.update(VIDEO_FORMATS)
    
    uri = uri.lower()
    if (uri.startswith("http:") or \
        uri.startswith("https:") or \
        uri.startswith("rtsp") or \
        uri.startswith("mms")):
        
        if (uri.endswith(".ram")):
            filetype = ".ram"
        elif (uri.endswith(".pls")):
            filetype = ".pls"
        elif (uri.endswith(".m3u")):
            filetype = ".m3u"
        elif (uri.endswith(".asf")):
            filetype = ".asf"
        else:
            filetype = "unknown-stream"
            
    else:
        filetype = os.path.splitext(uri)[-1]
        
    player = mapping.get(filetype, _DUMMY)
    logging.info("'%s' handled by %s", filetype, `player`)
    _switch_player(player)
    
    return player


def add_observer(observer):

    for player in _PLAYERS:
        logging.debug("loading player backend %s", `player`)
        player.add_observer(observer)
        

def close():
    """
    Closes the current media player.
    """
    
    _current_player.close()
        
        
def _switch_player(new_player):
    """
    Handles clean switching between the particular media players.
    """
    global _current_player
    
    if (new_player != _current_player):
        _current_player.close()
        _current_player = new_player

