from VideoViewer import VideoViewer


def is_available():
    
    # currently not supported on the Nokia 770 (SU-18)
    from utils import maemo
    if (maemo.get_product_code() in ["SU-18"]):
        return False
    else:
        return True

def get_viewer(): return VideoViewer

