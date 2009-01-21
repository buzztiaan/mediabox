def get_classes():

    from utils import maemo
    
    if (maemo.get_product_code() == "SU-18"):
        # no webcam on the Nokia 770 :(
        return []
    
    else:
        # cheeeeeese!
        from CameraViewer import CameraViewer
        return [CameraViewer]

