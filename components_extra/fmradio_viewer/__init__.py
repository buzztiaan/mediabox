def get_classes():

    from FMRadioPlayer import FMRadioPlayer
    from FMRadioView import FMRadioView
    return [FMRadioView]

    from utils import maemo
    if (maemo.get_product_code() in ("RX-34", "?")):
        from FMRadioViewer import FMRadioViewer
        from Prefs import Prefs
        return [FMRadioViewer, Prefs]
    else:
        return []


def get_devices():

    from FMRadioDevice import FMRadioDevice
    return [FMRadioDevice]

