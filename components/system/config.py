from utils.Config import Config

RESUME_AUTOMATIC = "automatic"
RESUME_MANUAL = "manual"


_cfg = Config("system", [
              ("keep-display-lit", Config.STRING, "no"),
              ("max-battery", Config.INTEGER, 15000),
              ("phonecall-resume", Config.STRING, RESUME_AUTOMATIC)
              ])



def set_display_lit(v):

    _cfg["keep-display-lit"] = v
    
    
def get_display_lit():

    return _cfg["keep-display-lit"]


def set_max_battery(v):

    _cfg["max-battery"] = v
    
    
def get_max_battery():

    return _cfg["max-battery"]


def set_phonecall_resume(v):

    _cfg["phonecall-resume"] = v
    

def get_phonecall_resume():

    return _cfg["phonecall-resume"]

