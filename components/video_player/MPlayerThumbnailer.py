from com import Thumbnailer
from theme import theme

from threading import Thread
import time
import os
import commands
import gtk
import gobject


_SIGKILL = 9


class MPlayerThumbnailer(Thumbnailer):
    """
    Thumbnailer for creating video thumbnails using mplayer.
    """

    def __init__(self):
    
        Thumbnailer.__init__(self)
        
        
    def get_mime_types(self):
    
        return ["video/*"]


    def make_quick_thumbnail(self, f):

        f.frame = (theme.mb_frame_video, 9, 5, 142, 150)

        thumb = self._get_thumbnail(f)
        if (thumb):
            return (thumb, True)
        else:
            is_final = not f.is_local
            return (theme.mb_default_video.get_path(), is_final)


    def make_thumbnail(self, f, cb, *args):

        t = Thread(target = self.__thumbnailer, args = (f, cb, args))
        t.start()


    def __thumbnailer(self, f, cb, args):

        cmd = "mplayer -idx -really-quiet -zoom -ss 10 -nosound " \
              "-vo jpeg:outdir=\"%s\" -frames 10 -vf scale=134:-3 \"%s\"" \
              " >/dev/null 2>&1 &\necho $!" \
              % ("/tmp", f.resource.replace("\"", "\\\"").replace("`", "\\`"))
        mplayer_pid = commands.getoutput(cmd)

        now = time.time()
        gobject.idle_add(self.__process_thumbnail, now, mplayer_pid, f, cb, args)


    def __process_thumbnail(self, begin, mplayer_pid, f, cb, args):

        has_pid = os.path.exists("/proc/%s" % mplayer_pid)
        # mplayer is still working
        if (time.time() - begin < 8 and has_pid):
            return True

        else:
            # if mplayer is hanging or taking a loooooong time, kill it
            if (has_pid):
                try:
                    os.kill(int(mplayer_pid), _SIGKILL)
                except:
                    pass
            #end if
            
            thumbs = [ os.path.join("/tmp", p) for p in os.listdir("/tmp")
                       if p.endswith("00002.jpg") ]
                       
            if (thumbs):
                thumb = thumbs[0]
                try:
                    pbuf = gtk.gdk.pixbuf_new_from_file(thumb)
                    os.system("rm -f %s" % thumb)
                    cb(self._set_thumbnail(f, pbuf), *args)
                    del pbuf
                except:
                    cb("", *args)
                
                os.system("rm -f /tmp/00000*.jpg")

            else:
                cb("", *args)

