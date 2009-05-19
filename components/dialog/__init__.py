def get_classes():

    from DialogService import DialogService
    from NotificationService import NotificationService
    return [DialogService,
            NotificationService]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

