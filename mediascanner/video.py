import os
import shutil


_VIDEO_EXT = (".avi", ".flv", ".mov", ".mpeg",
              ".mpg", ".rm", ".wmv", ".asf",
              ".m4v", ".mp4", ".rmvb")


def is_media(uri):

    try:
        if (os.path.isdir(uri)):
            return False
        
        elif (os.path.splitext(uri)[1].lower() in _VIDEO_EXT):
            return True
            
    except:
        return False
        
        
def make_thumbnail(uri, dest):

    # quick and dirty way of getting a video thumbnail
    cmd = "mplayer -idx -really-quiet -zoom -ss 10 -nosound " \
            "-vo jpeg:outdir=\"%s\" -frames 2 -vf scale=134:-3  \"%s\"" \
            " >/dev/null 2>&1" \
            % ("/tmp", uri)
    os.system(cmd)
    
    thumbs = [ os.path.join("/tmp", f) for f in os.listdir("/tmp")
               if f.endswith("00002.jpg") ]

    if (not thumbs): return
    thumb = thumbs[0]
    
    try:    
        shutil.move(thumb, dest)
    except:
        pass
    os.system("rm -f /tmp/00000*.jpg")
    
