"""
Base class for configurator components.
"""

from Component import Component
from ui.Widget import Widget


class Configurator(Component, Widget):
    """
    Base class for configurator components.
    Components derived from this class are shown as pages in the
    preferences viewer.
    @since: 0.96
    """

    ICON = None
    """
    theme reference to the icon which appears in the preferences viewer
    @since: 0.96
    """

    TITLE = ""
    """
    title text of the configurator
    @since: 0.96
    """
    
    DESCRIPTION = ""
    """
    description text of the configurator
    @since: 0.96.5
    """
    

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)

