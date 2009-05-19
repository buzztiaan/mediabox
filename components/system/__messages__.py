def SYSTEM_EV_DRIVE_MOUNTED(path): pass
"""
Gets emitted when a drive is mounted.

@param path: path of mount point
"""

def SYSTEM_EV_DRIVE_UNMOUNTED(path): pass
"""
Gets emitted when a drive is unmounted.

@param path: path of mount point
"""

def SYSTEM_EV_HEADPHONES_INSERTED(): pass
"""
Gets emitted when headphones are plugged into the device.
"""

def SYSTEM_EV_HEADPHONES_REMOVED(): pass
"""
Gets emitted when headphones are unplugged from the device.
"""

def SYSTEM_ACT_FORCE_SPEAKER_ON(): pass
"""
Forces sound output through the internal speaker even if headphones are
connected.
"""

def SYSTEM_ACT_FORCE_SPEAKER_OFF(): pass
"""
Turns off forcing sound output through the internal speaker.
"""

def SYSTEM_EV_BATTERY_REMAINING(percent): pass
"""
Gets emitted when a new battery fill level is reported.
This is currently disabled on Maemo, because polling the battery brings
undesired side effects.

@param percent: fill level in percents
"""

