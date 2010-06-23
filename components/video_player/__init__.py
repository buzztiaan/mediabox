delayed = True

def get_classes():

    import platforms
    from DSPSemaphore import DSPSemaphore
    from VideoPlayer import VideoPlayer
    from VideoInspector import VideoInspector
    classes = [DSPSemaphore, VideoPlayer, VideoInspector]
    
    if (platforms.MAEMO5):
        from OrgFreeDesktopVideoThumbnailer import OrgFreeDesktopVideoThumbnailer
        classes.append(OrgFreeDesktopVideoThumbnailer)
    else:
        from VideoThumbnailer import VideoThumbnailer
        classes.append(VideoThumbnailer)
        
    return classes


import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

