from utils import maemo
import platforms

def get_classes():
    from VolumeMount import VolumeMount
    from Prefs import Prefs

    classes = [VolumeMount, Prefs]
    if (platforms.PLATFORM in [platforms.MAEMO4, platforms.MAEMO5]):
        from Headset import Headset
        from DisplayLight import DisplayLight
        classes += [Headset, DisplayLight]

    return classes



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

