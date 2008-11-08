def get_devices():

    from AudioStorage import AudioStorage
    from AudioArtistsStorage import AudioArtistsStorage
    from VideoStorage import VideoStorage
    from ImageStorage import ImageStorage
    return [AudioStorage, AudioArtistsStorage, VideoStorage, ImageStorage]
