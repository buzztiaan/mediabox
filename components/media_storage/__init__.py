delayed = True

def get_devices():

    from utils import maemo
    from AudioStorage import AudioStorage
    from AudioAlbumStorage import AudioAlbumStorage
    from AudioArtistStorage import AudioArtistStorage
    from AudioGenreStorage import AudioGenreStorage
    from ImageStorage import ImageStorage
    from CameraStorage import CameraStorage
    
    from HistoryDevice import HistoryDevice
    from BookmarkDevice import GenericBookmarkDevice
    #from BookmarkDevice import AudioBookmarkDevice
    #from BookmarkDevice import VideoBookmarkDevice
    #from BookmarkDevice import ImageBookmarkDevice
    
    devices = [AudioStorage,
               AudioAlbumStorage,
               AudioArtistStorage,
               AudioGenreStorage,
               ImageStorage,
               CameraStorage,

               HistoryDevice,
               GenericBookmarkDevice]
               #AudioBookmarkDevice,
               #VideoBookmarkDevice,
               #ImageBookmarkDevice]
    
    # video still doesn't work well on the 770 :(
    if (maemo.get_product_code() != "SU-18"):
        from VideoStorage import VideoStorage
        devices.append(VideoStorage)

    return devices

