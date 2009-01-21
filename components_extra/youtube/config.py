from utils.Config import Config

_cfg = Config("youtube", [
              ("cache-folder", Config.STRING, "/media/mmc1"),
              ])


def set_cache_folder(path):

    _cfg["cache-folder"] = path
    
    
def get_cache_folder():

    return _cfg["cache-folder"]

