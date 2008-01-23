# the thief module tries to get existing thumbnails from the desktop or
# other applications, so that we can skip making our own

from utils import urlquote
import os
import md5


def steal_image(uri):

    # try osso
    vfsuri = "file://" + urlquote.quote(uri) + ".png"
    name = md5.new(vfsuri).hexdigest()
    thumb_dir = os.path.expanduser("~/.thumbnails/osso")
    thumb_uri = os.path.join(thumb_dir, name)
    
    if (os.path.exists(thumb_uri)):
        return thumb_uri
    else:
        return None


def steal_cover(uri):

    # try UKMP
    basename = os.path.basename(uri)
    name = basename + "_thumb.jpg"
    thumb_dir = "/media/mmc1/covers"

        
    cover_uri = os.path.join(thumb_dir, name)
    if (os.path.exists(cover_uri)):
        return cover_uri
    else:
        return None
        
        
def steal_video(uri):
    
    # try UKMP
    basename = os.path.basename(uri)
    vid_name = basename + ".jpg"
    thumb_dir = "/media/mmc1/covers"
        
    video_uri = os.path.join(thumb_dir, vid_name)
    if (os.path.exists(video_uri)):
        return video_uri
    else:
        return None

