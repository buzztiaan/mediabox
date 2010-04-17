delayed = True

def get_classes():

    from ImageViewer import ImageViewer
    #from ImageThumbnailer import ImageThumbnailer
    from OrgFreeDesktopThumbnailer import OrgFreeDesktopThumbnailer
    from ImageInspector import ImageInspector
    
    return [ImageViewer,
            #ImageThumbnailer,
            OrgFreeDesktopThumbnailer,
            ImageInspector]

