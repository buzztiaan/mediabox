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


messages = [
    "SYSTEM_EV_DRIVE_MOUNTED",
    "SYSTEM_EV_DRIVE_UNMOUNTED",
    "SYSTEM_EV_HEADPHONES_INSERTED",
    "SYSTEM_EV_HEADPHONES_REMOVED",
    
    "SYSTEM_ACT_FORCE_SPEAKER_ON",
    "SYSTEM_ACT_FORCE_SPEAKER_OFF",
    
    "SYSTEM_EV_BATTERY_REMAINING", # (percent)
]
