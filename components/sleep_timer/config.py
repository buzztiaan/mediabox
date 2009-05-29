from utils.Config import Config

_cfg = Config("sleep_timer", [
              ("sleep-time", Config.INTEGER_LIST, [0, 0]),
              ("wakeup-time", Config.INTEGER_LIST, [0, 0]),
              ("sleep", Config.BOOL, False),
              ("wakeup", Config.BOOL, False)
              ])


def set_sleep_time(h, m):

    _cfg["sleep-time"] = [h, m]
    
    
def get_sleep_time():

    return tuple(_cfg["sleep-time"])


def set_wakeup_time(h, m):

    _cfg["wakeup-time"] = [h, m]
    
    
def get_wakeup_time():

    return tuple(_cfg["wakeup-time"])


def set_sleep(v):

    _cfg["sleep"] = v
    
    
def get_sleep():

    return _cfg["sleep"]


def set_wakeup(v):

    _cfg["wakeup"] = v
    
    
def get_wakeup():

    return _cfg["wakeup"]


