from com import Component, msgs
from io import FileDownloader

import os


class Downloader(Component):
    """
    Component for providing a download manager.
    """

    def __init__(self):

        # table: download id -> handler
        self.__downloaders = {}
    
        Component.__init__(self)
        
        
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
        
        
    def handle_DOWNLOADER_ACT_ABORT(self, download_id):
    
        dloader = self.__downloaders.get(download_id)
        if (dloader):
            dloader.cancel()
            del self.__downloaders[download_id]
            self.emit_message(msgs.DOWNLOADER_EV_ABORTED, download_id)

