from utils import maemo

def get_classes():
    from VolumeMount import VolumeMount
    from Prefs import Prefs

    classes = [VolumeMount, Prefs]
    if (maemo.IS_MAEMO):
        from Headset import Headset
        from DisplayLight import DisplayLight
        classes += [Headset, DisplayLight]

    return classes



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

