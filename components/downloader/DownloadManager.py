from com import Dialog, msgs
from DownloadItem import DownloadItem
from ui.itemview import ThumbableGridView
from ui.dialog import OptionDialog


class DownloadManager(Dialog):
    """
    Dialog for managing active downloads.
    """

    def __init__(self):

        # table: download ID -> item
        self.__items = {}

        Dialog.__init__(self)
        self.set_title("Active Downloads")
        
        self.__list = ThumbableGridView()
        self.add(self.__list)


    def __on_click_item(self, download_id):
    
        dlg = OptionDialog("Abort this download?")
        dlg.add_option(None, "Yes, abort")
        dlg.add_option(None, "No, continue")
        
        if (dlg.run() == dlg.RETURN_OK):
            choice = dlg.get_choice()
            if (choice == 0):
                self.emit_message(msgs.DOWNLOADER_ACT_ABORT, download_id)
        #end if
        
        
    def handle_DOWNLOADER_EV_STARTED(self, download_id, url, destination):
    
        item = DownloadItem(url, destination)
        self.__items[download_id] = item
        self.__list.append_item(item)
        
        item.connect_clicked(self.__on_click_item, download_id)
        
        
    def handle_DOWNLOADER_EV_FINISHED(self, download_id):
    
        item = self.__items.get(download_id)
        if (item):
            del self.__items[download_id]
            pos = self.__list.get_items().index(item)
            self.__list.remove_item(pos)
            self.__list.invalidate()
            self.__list.render()
        
        
    def handle_DOWNLOADER_EV_ABORTED(self, download_id):
    
        item = self.__items.get(download_id)
        if (item):
            del self.__items[download_id]
            pos = self.__list.get_items().index(item)
            self.__list.remove_item(pos)
            self.__list.invalidate()
            self.__list.render()


    def handle_DOWNLOADER_EV_PROGRESS(self, download_id, amount, total):
    
        item = self.__items.get(download_id)
        if (item):
            item.set_amount(amount, total)
            idx = self.__list.get_items().index(item)
            self.__list.invalidate_item(idx)

