def get_classes():

    from utils import maemo
    if (True or maemo.get_product_code() == "RX-34"):
        from FMRadioViewer import FMRadioViewer
        from Prefs import Prefs
        return [FMRadioViewer, Prefs]
    else:
        return []

