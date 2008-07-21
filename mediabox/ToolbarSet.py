from ui.ImageButton import ImageButton


class ToolbarSet(object):
    """
    Class for representing a set of toolbar widgets.
    """

    def __init__(self):

        # child widgets of the toolbar set
        self.__children = []
        
        
    def get_items(self):
    
        return self.__children[:]
        
        
    def add_button(self, icon1, icon2, cb):
        """
        Adds a new button with a callback to the toolbar. Returns the button.
        """

        btn = ImageButton(icon1, icon2)        
        btn.connect_clicked(lambda :cb())
        self.__children.append(btn)
        return btn
        
        
    def add_toogle_button(self, icon1, icon2, cb):
        """
        Adds a new toggle button with a callback to the toolbar. Returns the
        button.
        """

        btn = ImageButton(icon1, icon2)        
        btn.connect_clicked(lambda :cb())
        self.__children.append(btn)
        return btn
        
        
    def add_progress_bar(self):
        """
        Adds a new progress bar to the toolbar. Returns the progress bar.
        """
        
        pass
        
        
        
    def add_widget(self, widget):
        """
        Adds the given widget to the toolbar.
        """
        
        self.__children.append(widget)
        
