import platforms

def get_classes():

    from DSPSemaphore import DSPSemaphore
    from VideoPlayer import VideoPlayer
    from VideoInspector import VideoInspector
    classes = [DSPSemaphore, VideoPlayer, VideoInspector]
    
    if (platforms.PLATFORM == platforms.MAEMO5):
        from OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
        classes.append(OrgFreeDesktopThumbnailer)
    else:
        from VideoThumbnailer import VideoThumbnailer
        classes.append(VideoThumbnailer)
        
    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

