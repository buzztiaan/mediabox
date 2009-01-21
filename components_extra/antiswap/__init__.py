def get_classes():

    from utils import maemo
    
    if (maemo.get_product_code() == "SU-18"):
        from AntiSwap import AntiSwap
        from Prefs import Prefs
        return [AntiSwap, Prefs]
    else:
        return []

