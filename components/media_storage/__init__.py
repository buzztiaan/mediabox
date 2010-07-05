delayed = True

def get_devices():

    from utils import maemo
    from AdHocDevice import AdHocDevice
    from AudioStorage import AudioStorage
    from AudioAlbumStorage import AudioAlbumStorage
    from AudioArtistStorage import AudioArtistStorage
    from AudioGenreStorage import AudioGenreStorage
    from ImageStorage import ImageStorage
    #from CameraStorage import CameraStorage
    
    from HistoryDevice import HistoryDevice
    
    devices = [AdHocDevice,
               AudioStorage,
               AudioAlbumStorage,
               AudioArtistStorage,
               AudioGenreStorage,
               ImageStorage,
               #CameraStorage,
               HistoryDevice]
    
    # video still doesn't work well on the 770 :(
    if (maemo.get_product_code() != "SU-18"):
        from VideoStorage import VideoStorage
        devices.append(VideoStorage)

    return devices

