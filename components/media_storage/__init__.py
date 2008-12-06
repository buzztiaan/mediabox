def get_devices():

    from AudioAlbumStorage import AudioAlbumStorage
    from AudioArtistStorage import AudioArtistStorage
    from VideoStorage import VideoStorage
    from ImageStorage import ImageStorage
    return [AudioAlbumStorage, AudioArtistStorage,
            VideoStorage, ImageStorage]
