from Component import Component
from ui.Widget import Widget


class Configurator(Component, Widget):
    """
    The Configurator component is presented as a page in the preferences
    viewer.
    """

    ICON = None
    TITLE = ""
    

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)

