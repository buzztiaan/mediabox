from utils import maemo
import platforms

def get_classes():
    from VolumeMount import VolumeMount

    classes = [VolumeMount]
    
    if (platforms.PLATFORM in [platforms.MAEMO4, platforms.MAEMO5]):
        from Headset import Headset
        from DisplayLight import DisplayLight
        from DisplayLightPrefs import DisplayLightPrefs
        classes += [Headset, DisplayLight, DisplayLightPrefs]

    return classes



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

