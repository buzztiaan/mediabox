def get_classes():

    from utils import maemo
    from FolderViewer import FolderViewer
    from AudioViewer import AudioViewer
    from ImageViewer import ImageViewer
    
    classes = [FolderViewer, AudioViewer, ImageViewer]
    
    # video still doesn't work well on the 770 :(
    if (maemo.get_product_code() != "SU-18"):
        from VideoViewer import VideoViewer
        classes.append(VideoViewer)

    return classes

