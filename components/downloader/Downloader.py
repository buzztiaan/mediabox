from com import Component, msgs
from io import FileDownloader
from utils import mimetypes

import os


class Downloader(Component):
    """
    Component for providing a download manager.
    """

    def __init__(self):

        # table: download id -> handler
        self.__downloaders = {}
    
        Component.__init__(self)


    def __retrieve_file(self, download_id, base_destination, queue):
        """
        Retrieves a queue of files recursively.
        """
        
        def on_data(data, amount, total):
            self.emit_message(msgs.DOWNLOADER_EV_PROGRESS,
                              download_id, amount, 0)
                
            if (not data):
                # continue downloading next file in queue
                self.__retrieve_file(download_id, base_destination, queue)


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
            # TODO: replace unsafe chars centrally by static method in File class
            newdir = os.path.join(destination, f.name)
            try:
                os.mkdir(newdir)
            except:
                pass
            
            if (os.path.exists(newdir)):
                f.get_contents(0, 0, child_collector, newdir, [])
            
        # if file, download
        else:
            url = f.resource
            ext = mimetypes.mimetype_to_ext(f.mimetype)
            print "EXTENSION", f.name, f.mimetype, ext
            destfile = os.path.join(destination, f.name + ext)
            dloader = FileDownloader(url, destfile, on_data)

        
    def handle_DOWNLOADER_SVC_GET(self, url, destination):
    
        def on_data(data, amount, total, destination):
            self.emit_message(msgs.DOWNLOADER_EV_PROGRESS,
                              download_id, amount, total)
        
            if (data == "" and download_id in self.__downloaders):
                del self.__downloaders[download_id]
                self.emit_message(msgs.DOWNLOADER_EV_FINISHED, download_id)
                self.emit_message(msgs.UI_ACT_SHOW_INFO,
                                  u"Finished downloading \xbb%s\xab" \
                                  % os.path.basename(destination))
                                  
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


        dloader = FileDownloader(url, destination, on_data, destination)
        download_id = hash(dloader)
        self.__downloaders[download_id] = dloader
        self.emit_message(msgs.DOWNLOADER_EV_STARTED,
                          download_id, url, destination)
        self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          u"Download started")
        
        return download_id
        

    def handle_DOWNLOADER_SVC_GET_RECURSIVE(self, f, destination):

        download_queue = [(f, destination)]
        download_id = hash(f)
        print "DOWNLOAD ID", download_id
        self.__downloaders[download_id] = download_queue
        self.__retrieve_file(download_id, destination, download_queue)
        self.emit_message(msgs.DOWNLOADER_EV_STARTED,
                          download_id, f.name, destination)
        self.emit_message(msgs.UI_ACT_SHOW_INFO,
                          u"Download started")
        
        return download_id
        
        
    def handle_DOWNLOADER_ACT_ABORT(self, download_id):
    
        dloader = self.__downloaders.get(download_id)
        if (dloader):
            dloader.cancel()
            del self.__downloaders[download_id]
            self.emit_message(msgs.DOWNLOADER_EV_ABORTED, download_id)

