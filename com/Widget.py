"""
Base class for widget components.
"""

from Component import Component
from ui.Widget import Widget as _Widget


class Widget(Component, _Widget):
    """
    Base class for widget components.
    Widget components are put directly on the main window, hidden.
    
    @since: 0.96.4
    """


    def __init__(self):

        Component.__init__(self)
        _Widget.__init__(self)
        self.set_visible(False)
