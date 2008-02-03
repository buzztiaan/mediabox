"""
This package contains the media player backends.
"""

from DummyPlayer import DummyPlayer
from MPlayer import MPlayer
from OSSOPlayer import OSSOPlayer

import os


_PLAYERS = [ player for player in (MPlayer(), OSSOPlayer(), DummyPlayer())
             if player.is_available() ]

_current_player = DummyPlayer()


def get_player_for_uri(uri):
    """
    Returns the appropriate player for the given uri or returns None
    if no appropriate player was found.
    """

    filetype = os.path.splitext(uri)[-1].lower()
    print "FILETYPE:", filetype,

    candidates = [ player for player in _PLAYERS if player.handles(filetype) ]
    if (candidates):
        player = candidates[0]
        print "... handled by", player        
        _switch_player(player)
        return player
    else:
        print "... unhandled"
        return None


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

