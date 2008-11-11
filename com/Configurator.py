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
    """theme reference to the icon which appears in the preferences viewer"""
    TITLE = ""
    """title text of the configurator"""
    

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)

