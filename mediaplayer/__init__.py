"""
This package contains the media player backends.
"""

from DummyPlayer import DummyPlayer
from MPlayer import MPlayer
from OSSOPlayer import OSSOPlayer

import os


_MPLAYER = MPlayer()
_OMS = OSSOPlayer()
_DUMMY = DummyPlayer()

_PLAYERS = [_MPLAYER, _OMS, _DUMMY]

_current_player = _DUMMY


# map filetypes to player backends
# TODO: make this configurable
_MAPPING = {".3gp":           _OMS,
            ".aac":           _OMS,
            ".asf":           _MPLAYER,
            ".avi":           _MPLAYER,
            ".flac":          _MPLAYER,
            ".flv":           _MPLAYER,
            ".m3u":           _OMS,
            ".m4a":           _OMS,
            ".m4v":           _OMS,
            ".mov":           _MPLAYER,
            ".mp3":           _OMS,
            ".mp4":           _OMS,
            ".mpeg":          _MPLAYER,
            ".mpg":           _MPLAYER,
            ".ogg":           _MPLAYER,
            ".pls":           _OMS,
            ".ram":           _OMS,
            ".rm":            _OMS,
            ".rmvb":          _OMS,
            ".wav":           _OMS,
            ".wma":           _OMS,
            ".wmv":           _MPLAYER,
            ".wpl":           _OMS,
            "unknown-stream": _MPLAYER}
         


def get_player_for_uri(uri):
    """
    Returns the appropriate player for the given uri or returns None
    if no appropriate player was found.
    """
    
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
        
    player = _MAPPING.get(filetype, _DUMMY)
    print filetype, "... handled by", player
    _switch_player(player)
    
    return player


def add_observer(observer):

    for player in _PLAYERS:
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

