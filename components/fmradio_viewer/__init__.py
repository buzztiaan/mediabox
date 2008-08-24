def get_classes():

    from utils import maemo
    if (maemo.get_product_code() in ("RX-34", "?")):
        from FMRadioViewer import FMRadioViewer
        from Prefs import Prefs
        return [FMRadioViewer, Prefs]
    else:
        return []

