from VideoViewer import VideoViewer


def get_classes():

    # currently not supported on the Nokia 770 (SU-18)
    from utils import maemo
    if (maemo.get_product_code() in ["SU-18"]):
        return []
    else:
        return []#[VideoViewer]

