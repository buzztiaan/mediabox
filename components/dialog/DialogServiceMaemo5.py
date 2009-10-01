from com import Widget, msgs
from ui.Pixmap import Pixmap, TEMPORARY_PIXMAP, text_extents
from ui.Button import Button
from Dialog import Dialog
from theme import theme

import gtk
import hildon


class DialogService(Widget):
    """
    Service for showing dialog windows to the user.
    """

    def __init__(self):
           
        Widget.__init__(self)
        


    def handle_DIALOG_SVC_OPTIONS(self, *options):
    
        dlg = OptionDialog()
        for icon, label in options:
            dlg.add_option(icon, label)
        dlg.run()
        
        return dlg.get_choice()


    def handle_DIALOG_SVC_QUESTION(self, header, text):
    
        import hildon
        win = self.get_window().get_gtk_window()
        note = hildon.Note("confirmation", win, text)
        note.set_button_texts("Yes", "No")
        ret = note.run()
        note.destroy()

        if (ret == gtk.RESPONSE_OK):
            return 0
        else:
            return 1

               

    def handle_DIALOG_SVC_ERROR(self, header, text):
    
        return 0
        
        
    def handle_DIALOG_SVC_WARNING(self, header, text):

        return 0    
        
        
    def handle_DIALOG_SVC_INFO(self, header, text):

        return 0    


    def handle_DIALOG_SVC_TEXT_INPUT(self, header, text):

        return (0, "")
        
        
    def handle_DIALOG_SVC_CUSTOM(self, icon, header, custom):

        return 0    

