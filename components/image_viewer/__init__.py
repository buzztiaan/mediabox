delayed = True

def get_classes():

    import platforms
    from ImageViewer import ImageViewer
    from ImageInspector import ImageInspector

    classes = [ImageViewer,
               ImageInspector]

    if (platforms.MAEMO5):
        from OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
        classes += [OrgFreeDesktopThumbnailer]
    else:
        from ImageThumbnailer import ImageThumbnailer
        classes += [ImageThumbnailer]
    
    
    return classes

