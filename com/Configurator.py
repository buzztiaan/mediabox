from Component import Component
import events
from ui.Widget import Widget


class Configurator(Component, Widget):

    ICON = None
    TITLE = ""
    

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)

