"""
This package contains the media player backends.
"""

from DummyBackend import DummyBackend
from utils import maemo
from mediabox import values
from utils import mimetypes
from utils import logging

import os


_DUMMY = DummyBackend()

if (maemo.IS_MER):
    from XineBackend import XineBackend
    _XINE = XineBackend()
    _PLAYERS = {"xine": _XINE}
    _SUFFIX = ".mer"
    
elif (maemo.IS_MAEMO):
    from GstBackend import GstBackend
    from MPlayerBackend import MPlayerBackend
    from OSSOBackend import OSSOBackend
    _GST = GstBackend()
    _MPLAYER = MPlayerBackend()
    _OMS = OSSOBackend()
    _PLAYERS = {"gst": _GST,
                "mplayer": _MPLAYER,
                "oms": _OMS}
    _SUFFIX = ".maemo"
                
else:
    from GstBackend import GstBackend
    from MPlayerBackend import MPlayerBackend
    from XineBackend import XineBackend
    _GST = GstBackend()
    _MPLAYER = MPlayerBackend()
    _XINE = XineBackend()
    _PLAYERS = {"gst": _GST,
                "mplayer": _MPLAYER,
                "xine": _XINE}
    _SUFFIX = ""


_current_player = _DUMMY

# table: mediatype -> backend name
_MAPPING_TABLE = {}

_PLAYERS_MAPPING_FILE1 = os.path.join(os.path.dirname(__file__), "players.mapping" + _SUFFIX)
_PLAYERS_MAPPING_FILE2 = os.path.join(values.USER_DIR, "players.mapping")




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

        player = _PLAYERS.get(playername, _DUMMY)
        _MAPPING_TABLE[mediatype] = playername
    #end for
   
   
def write_user_mapping():

    try:
        fd = open(_PLAYERS_MAPPING_FILE2, "w")
    except:
        logging.error("could not write players.mapping:\n%s",
                      logging.stacktrace())
        return

    for mt, backend in _MAPPING_TABLE.items():
        fd.write("%s %s\n" % (mt, backend))

    fd.close()    


def get_player_for_mimetype(mimetype):
    """
    Returns the appropriate player for the given MIME type or returns the
    DUMMY player if no appropriate player was found.
    """

    mediatype = mimetypes.mimetype_to_name(mimetype)
    
    backend = get_backend_for(mediatype)
    player = _PLAYERS.get(backend, _DUMMY)
    logging.info("'%s' handled by %s", mediatype, `player`)
    _switch_player(player)
    
    return player



def get_backends():

    return _PLAYERS.keys()
    
    
def get_media_types():

    return _MAPPING_TABLE.keys()


def get_backend_for(mediatype):

    return _MAPPING_TABLE.get(mediatype, "dummy")


def get_backend_icon(backend):

    return _PLAYERS.get(backend, _DUMMY).get_icon()
    

def set_backend_for(mediatype, backend):

    _MAPPING_TABLE[mediatype] = backend




def add_observer(observer):

    for player in _PLAYERS.values():
        logging.debug("loading player backend %s", `player`)
        player.add_observer(observer)
        

def close():
    """
    Closes the current media player.
    """
    
    try:
        _current_player.close()
    except:
        pass
        
        
def _switch_player(new_player):
    """
    Handles clean switching between the particular media players.
    """
    global _current_player
    
    if (new_player != _current_player):
        try:
            _current_player.close()
        except:
            pass
        _current_player = new_player



_read_mapping_table(_PLAYERS_MAPPING_FILE1)
if (os.path.exists(_PLAYERS_MAPPING_FILE2)):
    _read_mapping_table(_PLAYERS_MAPPING_FILE2)

