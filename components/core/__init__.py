def get_classes():

    from Initialiser import Initialiser
    from IdleDetector import IdleDetector
    from AppletService import AppletService
    from BookmarkService import BookmarkService
    from DirectoryService import DirectoryService
    from MediaOutputService import MediaOutputService

    return [Initialiser,
            IdleDetector,
            AppletService,
            BookmarkService,
            DirectoryService,
            MediaOutputService]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

