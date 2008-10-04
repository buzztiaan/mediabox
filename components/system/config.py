from utils.Config import Config

_cfg = Config("system", [
              ("max-battery", Config.INTEGER, 15000),
              ])


def set_max_battery(v):

    _cfg["max-battery"] = v
    
    
def get_max_battery():

    return _cfg["max-battery"]

