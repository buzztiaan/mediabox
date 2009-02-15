from utils.Config import Config

_cfg = Config("youtube", [
              ("cache-folder", Config.STRING, "/media/mmc1"),
              ("hi-quality", Config.BOOL, False),
              ])


def set_cache_folder(path):

    _cfg["cache-folder"] = path
    
    
def get_cache_folder():

    return _cfg["cache-folder"]


def set_hi_quality(v):

    _cfg["hi-quality"] = v
    
    
def get_hi_quality():

    return _cfg["hi-quality"]

