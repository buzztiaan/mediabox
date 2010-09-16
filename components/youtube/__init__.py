delayed = True

def get_classes():

    from YouTubeThumbnailer import YouTubeThumbnailer
    from YouTubePrefs import YouTubePrefs
    return [YouTubeThumbnailer,
            YouTubePrefs]


def get_devices():

    from YouTube import YouTube
    return [YouTube]

