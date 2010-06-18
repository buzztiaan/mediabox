from com import Component, msgs
from storage import File
from io import FileDownloader
from utils import mimetypes

import os
import time


class Downloader(Component):
    """
    Component for providing a download manager.
    """

    def __init__(self):

        self.__last_progress_time = 0

        # table: download id -> handler
        self.__downloaders = {}
    
        Component.__init__(self)


    def __report_progress(self, download_id, destname, amount, total):

        now = time.time()
        if (now > self.__last_progress_time + 0.25):
            self.emit_message(msgs.DOWNLOADER_EV_PROGRESS, download_id,
                              destname, amount, total)
            self.__last_progress_time = now


    def __retrieve_file(self, download_id, base_destination, queue):
        """
        Retrieves a queue of files recursively.
        """
        
        def on_data(data, amount, total, destname, destfile):
            self.emit_message(msgs.DOWNLOADER_EV_PROGRESS, download_id,
                              destname, amount, 0)
           
            if (data == ""):
                # continue downloading next file in queue
                self.__retrieve_file(download_id, base_destination, queue)
            elif (data == None):
                # abort downloading
                try:
                    os.unlink(destfile)
                except:
                    pass
                self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                  u"Download aborted")

        def child_collector(f, newdir, collection):
            if (f):
                collection.append(f)
            else:
                for c in collection:
                    queue.append((c, newdir))
                self.__retrieve_file(download_id, base_destination, queue)
            return True
            
        
        # queue consists of (f, destination) tuples with destination being a local directory
        if (queue):
            f, destination = queue.pop(0)
        else:
            # nothing to pop, we're done
            self.emit_message(msgs.DOWNLOADER_EV_FINISHED, download_id)
            self.emit_message(msgs.UI_ACT_SHOW_INFO,
                              u"Finished downloading \xbb%s\xab" \
                              % os.path.basename(base_destination))

            if (download_id in self.__downloaders):
                del self.__downloaders[download_id]

            # add to file index
            self.emit_message(msgs.FILEINDEX_ACT_SCAN_FOLDER,
                              base_destination)
            return
    
        # if directory, recurse
        if (f.mimetype == f.DIRECTORY):
            # make directory for this
            name = File.make_safe_name(f.name)
            newdir = os.path.join(destination, name)
            try:
                os.mkdir(newdir)
            except:
                pass
            
            if (os.path.exists(newdir)):
                f.get_contents(0, 0, child_collector, newdir, [])
            
        # if file, download
        else:
            url = f.resource
            name = File.make_safe_name(f.name)
            ext = mimetypes.mimetype_to_ext(f.mimetype)
            destname = name + ext
            destfile = os.path.join(destination, destname)
            dloader = FileDownloader(url, destfile, on_data, destname, destfile)
            self.__downloaders[download_id] = dloader

        
    def handle_DOWNLOADER_SVC_GET(self, url, destination):
    
        def on_data(data, amount, total, destination, destname):
            self.emit_message(msgs.DOWNLOADER_EV_PROGRESS, download_id,
                              destname, amount, total)
        
            if (data == "" and download_id in self.__downloaders):
                del self.__downloaders[download_id]
                self.emit_message(msgs.DOWNLOADER_EV_FINISHED, download_id)
                self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                  u"Finished downloading \xbb%s\xab" \
                                  % destname)
                                  
                # add to file index
                self.call_service(msgs.FILEINDEX_SVC_DISCOVER,
                                  destination,
                                  os.path.getmtime(destination))

            elif (data == None):
                try:
                    os.unlink(destination)
                except:
                    pass
                self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                  u"Download aborted")
            #end if


        destname = os.path.basename(destination)
        dloader = FileDownloader(url, destination, on_data,
                                 destination, destname)
        download_id = hash(dloader)
        self.__downloaders[download_id] = dloader
        self.emit_message(msgs.DOWNLOADER_EV_STARTED,
                          download_id, url, destination)
        self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          u"Downloading")
        
        return download_id
        

    def handle_DOWNLOADER_SVC_GET_RECURSIVE(self, f, destination):

        download_queue = [(f, destination)]
        download_id = hash(f)
        print "DOWNLOAD ID", download_id
        self.__downloaders[download_id] = download_queue
        self.__retrieve_file(download_id, destination, download_queue)
        self.emit_message(msgs.DOWNLOADER_EV_STARTED, download_id,
                          f.get_children()[0].resource, destination)
        self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          u"Downloading Folder")
        
        return download_id
        
        
    def handle_DOWNLOADER_ACT_ABORT(self, download_id):
    
        dloader = self.__downloaders.get(download_id)
        if (dloader):
            dloader.cancel()
            del self.__downloaders[download_id]
            self.emit_message(msgs.DOWNLOADER_EV_ABORTED, download_id)

