from utils.Config import Config

_cfg = Config("talknavigator", [
              ("pitch", Config.INTEGER, 70),
              ("speed", Config.INTEGER, 160),
              ("voice", Config.STRING, "f3")
              ])


def set_pitch(p):

    _cfg["pitch"] = p
    
    
def get_pitch():

    return _cfg["pitch"]
    
    
def set_speed(s):

    _cfg["speed"] = s
    
    
def get_speed():

    return _cfg["speed"]
    
    
def set_voice(v):

    _cfg["voice"] = v
    
    
def get_voice():

    return _cfg["voice"]

