"""
This package contains the media player backends.
"""

from DummyPlayer import DummyPlayer
from MPlayer import MPlayer
from OSSOPlayer import OSSOPlayer
#from utils import maemo
from utils import mimetypes
from utils import logging

import os


_MPLAYER = MPlayer()
_OMS = OSSOPlayer()
_DUMMY = DummyPlayer()

_PLAYERS = [_MPLAYER, _OMS, _DUMMY]
_PLAYER_NAMES = {"mplayer": _MPLAYER, "oms": _OMS, "dummy": _DUMMY}

_current_player = _DUMMY

_MAPPING_TABLE = {}

_PLAYERS_MAPPING_FILE1 = os.path.join(os.path.dirname(__file__), "players.mapping")
_PLAYERS_MAPPING_FILE2 = os.path.expanduser("~/.mediabox/players.mapping")




def _read_mapping_table(mappingfile):
    """
    Reads the mapping table.
    """

    mapping = {}
    lines = None    
    try:
        fd = open(mappingfile, "r")
        lines = fd.readlines()
        fd.close()
    except:
        logging.error("could not read players.mapping file:\n%s" % mappingfile)
        return

    cnt = 0
    for line in lines:
        cnt += 1
        if (not line.strip() or line.startswith("#")):
            continue
            
        parts = line.split()
        try:
            mediatype = parts[0]
            playername = parts[1]
        except:
            logging.error("syntax error in players.mapping in line %d:\n%s" \
                          % (cnt, line.strip()))
            continue

        player = _PLAYER_NAMES.get(playername, _DUMMY)
        _MAPPING_TABLE[mediatype] = player
    #end for
   


def get_player_for_mimetype(mimetype):
    """
    Returns the appropriate player for the given MIME type or returns the
    DUMMY player if no appropriate player was found.
    """

    mediatype = mimetypes.mimetype_to_name(mimetype)
    
    player = _MAPPING_TABLE.get(mediatype, _DUMMY)
    logging.info("'%s' handled by %s", mediatype, `player`)
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



_read_mapping_table(_PLAYERS_MAPPING_FILE1)
if (os.path.exists(_PLAYERS_MAPPING_FILE2)):
    _read_mapping_table(_PLAYERS_MAPPING_FILE2)

