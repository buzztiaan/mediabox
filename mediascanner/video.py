import thief

import os
import commands
import shutil
import time


_VIDEO_EXT = (".avi", ".flv", ".mov", ".mpeg",
              ".mpg", ".rm", ".wmv", ".asf",
              ".m4v", ".mp4", ".rmvb")

_SIGKILL = 9



def _has_pid(pid):
    """
    Returns whether a process with the given PID exists.
    """

    return os.path.exists("/proc/%s" % pid)


def is_media(uri):

    try:
        if (os.path.isdir(uri)):
            return False
        
        elif (os.path.splitext(uri)[1].lower() in _VIDEO_EXT):
            return True
            
    except:
        return False
        
        
def make_thumbnail(uri, dest):

    thumb = thief.steal_video(uri)
    
    if (thumb):
        shutil.copy(thumb, dest)
        
    else:
        # quick and dirty way of getting a video thumbnail
        cmd = "mplayer -idx -really-quiet -zoom -ss 10 -nosound " \
              "-vo jpeg:outdir=\"%s\" -frames 2 -vf scale=134:-3  \"%s\"" \
              " >/dev/null 2>&1 &\necho $!" \
              % ("/tmp", uri)
        mplayer_pid = commands.getoutput(cmd)

        print "thumbnailing", uri,
        now = time.time()
        while (time.time() - now < 8 and _has_pid(mplayer_pid)):
            time.sleep(0.005)
        #end while

        # if mplayer is hanging or taking a loooong time, kill it
        if (_has_pid(mplayer_pid)):
            try:
                os.kill(int(mplayer_pid), _SIGKILL)
            except:
                pass
        #end if

        thumbs = [ os.path.join("/tmp", f) for f in os.listdir("/tmp")
                   if f.endswith("00002.jpg") ]

        if (thumbs):
            thumb = thumbs[0]
            try:    
                shutil.move(thumb, dest)
            except:
                pass
            os.system("rm -f /tmp/00000*.jpg")
            
            print "... OK"
            
        else:
            print "... failed"
        #end if
    #end if
