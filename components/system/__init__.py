def get_classes():
    from VolumeMount import VolumeMount
    from utils import maemo
    import platforms

    classes = [VolumeMount]
    
    if (platforms.MAEMO4 or platforms.MAEMO5):
        from Headset import Headset
        from DisplayLight import DisplayLight
        from DisplayLightPrefs import DisplayLightPrefs
        classes += [Headset,
                    DisplayLight,
                    DisplayLightPrefs]

    if (platforms.MAEMO5):
        from PhoneMonitor import PhoneMonitor
        from PhonePolicy import PhonePolicy
        classes += [PhoneMonitor,
                    PhonePolicy]

    return classes



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

