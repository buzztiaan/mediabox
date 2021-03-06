def get_classes():

    from Initialiser import Initialiser
    from IdleDetector import IdleDetector
    from BookmarkService import BookmarkService
    from DirectoryService import DirectoryService
    from MediaOutputService import MediaOutputService
    from ThumbnailService import ThumbnailService
    from AboutDialog import AboutDialog

    return [Initialiser,
            IdleDetector,
            BookmarkService,
            DirectoryService,
            MediaOutputService,
            ThumbnailService,
            AboutDialog]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

