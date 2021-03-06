"""
This package contains the media player backends.
"""

import platforms
from mediabox import values
from utils import mimetypes
from utils import logging

import os

_PLAYERS = {}

from DummyBackend import DummyBackend
_DUMMY = DummyBackend()

if (platforms.MER):
    try:
        from XineBackend import XineBackend
        _PLAYERS["xine"] = XineBackend()
    except:
        logging.info("failed to load xine backend")
#end if

if (os.path.exists("/usr/bin/mplayer")):
    try:
        from MPlayerBackend import MPlayerBackend
        _PLAYERS["mplayer"] = MPlayerBackend()
    except:
        logging.info("failed to load mplayer backend")
#end if

# GStreamer playbin is quite broken on Maemo4; e.g. does not stream MP3 reliably
if (True): #not platforms.MAEMO4):
    try:
        from GstBackend import GstBackend
        _PLAYERS["gst"] = GstBackend()
    except:
        logging.info("failed to load gstreamer backend:\n%s",
                     logging.stacktrace())
#end if

if (platforms.MAEMO4):
    try:
        from OSSOBackend import OSSOBackend
        _PLAYERS["oms"] = OSSOBackend()
    except:
        logging.info("failed to load osso-media-server backend")
#end if

if (platforms.MAEMO5):
    try:
        from MAFWBackend import MAFWBackend
        _PLAYERS["mafw"] = MAFWBackend()
    except:
        import traceback; traceback.print_exc()
        logging.info("failed to load mafw backend")
#end if

from SimulatedBackend import SimulatedBackend
_PLAYERS["simulated"] = SimulatedBackend()


if (platforms.MER):
    _SUFFIX = ".mer"

elif (platforms.MAEMO4):
    _SUFFIX = ".maemo"

elif (platforms.MAEMO5):
    _SUFFIX = ".maemo5"
                
else:
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

    # this operation is not time-critical, so we may read in the mapping table
    # every time
    _read_mapping_table(_PLAYERS_MAPPING_FILE1)
    if (os.path.exists(_PLAYERS_MAPPING_FILE2)):
        _read_mapping_table(_PLAYERS_MAPPING_FILE2)
    

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

