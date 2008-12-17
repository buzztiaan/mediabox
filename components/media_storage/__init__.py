def get_devices():

    from AudioStorage import AudioStorage
    from AudioAlbumStorage import AudioAlbumStorage
    from AudioArtistStorage import AudioArtistStorage
    from VideoStorage import VideoStorage
    from ImageStorage import ImageStorage
    return [AudioStorage, AudioAlbumStorage, AudioArtistStorage,
            VideoStorage, ImageStorage]
