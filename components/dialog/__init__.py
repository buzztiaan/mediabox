import platforms

def get_classes():

    if (platforms.PLATFORM in (platforms.MAEMO5, platforms.MER)):
        from DialogServiceMaemo5 import DialogService
    else:
        from DialogService import DialogService
    from NotificationService import NotificationService
    return [DialogService,
            NotificationService]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

