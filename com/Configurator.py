"""
Base class for configurator components.
"""

from Component import Component
from ui.Widget import Widget


class Configurator(Component, Widget):
    """
    Components derived from this class are presented as pages in the
    preferences viewer.
    """

    ICON = None
    TITLE = ""
    

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)

