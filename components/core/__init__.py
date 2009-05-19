def get_classes():

    from Initialiser import Initialiser
    from IdleDetector import IdleDetector
    from BookmarkService import BookmarkService
    from DirectoryService import DirectoryService
    from MediaWidgetRegistry import MediaWidgetRegistry

    return [Initialiser,
            IdleDetector,
            BookmarkService,
            DirectoryService,
            MediaWidgetRegistry]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

