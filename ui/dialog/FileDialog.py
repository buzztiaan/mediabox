import platforms

import gtk
if (platforms.MAEMO4 or platforms.MAEMO5):
    import gobject
    import hildon


class FileDialog(object):

    TYPE_OPEN = 0
    TYPE_SAVE = 1
    

    def __init__(self, dlg_type, title):
    
        self.__title = title
        self.__dlg_type = dlg_type
        self.__selection = ""
        
        
    def get_filename(self):
    
        return self.__selection
        
        
    def run(self):

        if (self.__dlg_type == self.TYPE_OPEN):
            action = gtk.FILE_CHOOSER_ACTION_OPEN
        else:
            action = gtk.FILE_CHOOSER_ACTION_SAVE
            
        dlg = gobject.new(hildon.FileChooserDialog, action = action)
        dlg.set_title(self.__title)
        
        response = dlg.run()
        self.__selection = dlg.get_filename()
        dlg.destroy()

