import threads
import logging

from Queue import Queue
import threading
import urllib2
import time



# maximum number of worker threads
_MAX_WORKERS = 4


class _Downloader(object):
    """
    Singleton object for an asynchronous HTTP downloader.
    """

    CONNECTING = 0
    SIZE_AVAILABLE = 1
    DOWNLOAD_STARTED = 2
    DOWNLOAD_FINISHED = 3
    DOWNLOAD_STATUS = 4
    DOWNLOAD_CANCELLED = 5
    TIMEOUT = 6
    ERROR = 7
    

    def __init__(self):
    
        # queue for download requests
        self.__queue = Queue()
        
        # number of currently active worker threads
        self.__number_of_workers = 0



    def __worker_thread(self):
        """
        Worker thread.
        A worker thread retrieves download requests from the queue and handles
        them. Once the queue gets empty, it dies.
        """
        
        logging.debug("creating download worker")
        
        while (True):
            # read request from queue
            try:
                url, cb, timeout = self.__queue.get_nowait()
            except:
                # queue is empty, kill worker
                break

            # connect
            threads.run_unthreaded(cb, self.CONNECTING, url)
            try:
                fd = urllib2.urlopen(url)
            except:
                import traceback; traceback.print_exc()
                threads.run_unthreaded(cb, self.ERROR, url)
                continue
          
            # retrieve Content-Length
            threads.run_unthreaded(cb, self.DOWNLOAD_STARTED, url)
            total_size = fd.info().get("Content-Length", 0)
            if (total_size):
                threads.run_unthreaded(cb, self.SIZE_AVAILABLE, url, total_size)
    
            # read data    
            data = ""
            bytes_read = 0
            aborted = False
            now = time.time()
            while (True):
                # TODO: we should use non-blocking IO for detecting timeouts
                new_data = fd.read(4096)
                if (not new_data):
                    # reached EOF
                    break
                elif (timeout and time.time() > now + timeout):
                    # timeout
                    aborted = True
                    break 
            
                data += new_data
                bytes_read += len(new_data)
                percentage = (100 * bytes_read / max(0.1, float(total_size)))
                threads.run_unthreaded(cb, self.DOWNLOAD_STATUS, url,
                                       bytes_read, total_size, percentage)
                threads.keep_alive()
            #end while

            fd.close()
            if (aborted):
                threads.run_unthreaded(cb, self.TIMEOUT, url)
            else:
                threads.run_unthreaded(cb, self.DOWNLOAD_FINISHED, url, data)

        #end while

        self.__number_of_workers -= 1
        logging.debug("killing download worker, %d left" \
                      % self.__number_of_workers)


    def __create_worker(self):
        """
        Creates a new worker thread if the number of workers is less than the
        maximum number.
        """
        
        if (self.__number_of_workers >= _MAX_WORKERS): return
        
        self.__number_of_workers += 1
        threads.run_threaded(self.__worker_thread)
        



    def get_async(self, url, cb, timeout = 0):
        """
        Retrieves the given URL asynchronous and invokes the given callback
        handler. If timeout is non-zero, the download is cancelled if the
        host doesn't respond within the given time frame.
        """

        self.__create_worker()
        
        self.__queue.put((url, cb, timeout))
        
        
    def get(self, url):
        """
        Convenience method for downloading a file synchronous.
        Returns None if an error occured during download.
        """

        finished = threading.Event()
        data = [None]
        
        def f(cmd, *args):
            if (cmd == self.DOWNLOAD_FINISHED):
                data[0] = args[1]
                finished.set()
            elif (cmd == self.ERROR):
                finished.set()
            elif (cmd == self.TIMEOUT):
                finished.set()

        self.get_async(url, f)
        while (not finished.isSet()): gtk.main_iteration()

        return data[0]    



_singleton = _Downloader()
def Downloader(): return _singleton
