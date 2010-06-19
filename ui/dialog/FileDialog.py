import platforms

import os
import gtk
import gobject
if (platforms.MAEMO4 or platforms.MAEMO5):
    import hildon


if (platforms.MAEMO4 or platforms.MAEMO5):
    _MYDOCS = os.path.join(os.path.expanduser("~"), "MyDocs")
else:
    _MYDOCS = os.path.expanduser("~")


class FileDialog(object):

    TYPE_OPEN = 0
    TYPE_SAVE = 1
    TYPE_FOLDER = 2
    

    def __init__(self, dlg_type, title):
    
        self.__title = title
        self.__dlg_type = dlg_type
        self.__selection = ""
        self.__filename = ""
        
        
    def set_filename(self, filename):
    
        self.__filename = filename
        
        
    def get_filename(self):
    
        return self.__selection
        
        
    def run(self):

        if (self.__dlg_type == self.TYPE_OPEN):
            action = gtk.FILE_CHOOSER_ACTION_OPEN
        elif (self.__dlg_type == self.TYPE_SAVE):
            action = gtk.FILE_CHOOSER_ACTION_SAVE
        else:
            action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER

        if (platforms.MAEMO4 or platforms.MAEMO5):            
            dlg = gobject.new(hildon.FileChooserDialog, action = action)
        else:
            dlg = gtk.FileChooserDialog(parent = None, action = action,
                                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dlg.set_title(self.__title)
        
        #print dir(dlg)
        #print dlg.get_safe_folder_uri()
        if (self.__dlg_type == self.TYPE_SAVE):
            dlg.set_current_name(self.__filename)
        dlg.set_current_folder(_MYDOCS)
        
        response = dlg.run()
        if (response == gtk.RESPONSE_OK):
            self.__selection = dlg.get_filename()
        dlg.destroy()

