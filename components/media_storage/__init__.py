def get_devices():

    from AudioStorage import AudioStorage
    from VideoStorage import VideoStorage
    from ImageStorage import ImageStorage
    return [AudioStorage, VideoStorage, ImageStorage]
