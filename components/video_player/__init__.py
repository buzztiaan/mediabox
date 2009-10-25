import platforms

def get_classes():

    from VideoPlayer import VideoPlayer
    classes = [VideoPlayer]
    if (platforms.PLATFORM == platforms.MAEMO5):
        from OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
        classes.append(OrgFreeDesktopThumbnailer)
    else:
        from VideoThumbnailer import VideoThumbnailer
        classes.append(VideoThumbnailer)
        
    return classes

