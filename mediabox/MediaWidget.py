from ui.Widget import Widget
from mediabox.ToolbarSet import ToolbarSet


class MediaWidget(Widget):

    EVENT_MEDIA_POSITION = "media-position"
    EVENT_FULLSCREEN_TOGGLED = "fullscreen-toggled"
    

    def __init__(self):
    
        self.__tbset = None
        
        Widget.__init__(self)
        
        
    def destroy(self):
    
        pass
        
        
    def load(self, uri):
    
        raise NotImplementedError
        
        
    def _set_controls(self, *widgets):
        """
        Creates a new toolbar set.
        """
        
        self.__tbset = ToolbarSet()
        for w in widgets:
            self.__tbset.add_widget(w)


    def get_controls(self):
        """
        Returns the controls of this widget.
        """
        
        return self.__tbset
        
        
    def connect_media_position(self, cb, *args):
    
        self._connect(self.EVENT_MEDIA_POSITION, cb, *args)
        

    def connect_fullscreen_toggled(self, cb, *args):
    
        self._connect(self.EVENT_FULLSCREEN_TOGGLED, cb, *args)

