from utils import maemo

def get_classes():
    from System import System
    from BatteryMonitor import BatteryMonitor

    classes = []
    classes.append(System)
    if (maemo.IS_MAEMO): classes.append(BatteryMonitor)

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
