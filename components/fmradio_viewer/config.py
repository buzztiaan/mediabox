from utils.Config import Config


_cfg = Config("fmradio",
              [("region", Config.STRING, "EUR")])
              
              
def get_region():

    return _cfg["region"]
    
    
def set_region(region):
    assert region in ("EUR", "JPN")

    _cfg["region"] = region
