def get_classes():

    from Downloader import Downloader
    from DownloadManager import DownloadManager
    return [Downloader,
            DownloadManager]


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

