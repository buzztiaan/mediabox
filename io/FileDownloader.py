from Downloader import Downloader
import os


class FileDownloader(Downloader):
    """
    Class for downloading to a file.

    The user callback is invoked repeatedly as data comes in.
    The transmission is finished when data = "" is passed to the callback.
    
    While the download is not yet finished, a .partial file signalizes this.
    """
    
    def __init__(self, url, dest, cb, *args):
    
        self.__fd = open(dest, "w")
        self.__partial = dest + ".partial"
    
        open(self.__partial, "w").write("")
        Downloader.__init__(self, url, self.__on_receive_data, cb, args)
        
        
        
    def __on_receive_data(self, data, amount, total, cb, args):
    
        if (data):
            # write data to file
            self.__fd.write(data)
           
        else:
            # finished downloading
            self.__fd.close()
            os.unlink(self.__partial)

        cb(data, amount, total, *args)



if (__name__ == "__main__"):
    import gtk
    import sys
    
    def f(data, amount, total):
        if (total):
            percentage = int(amount / float(total) * 100.0)
        else:
            percentage = -1

        print "%d %% " % percentage
        
        if (amount == total):
            gtk.main_quit()
    
    
    FileDownloader(sys.argv[1], sys.argv[2], f)
    gtk.main()

