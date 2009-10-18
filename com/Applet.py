"""
Base class for applets.
"""

from Component import Component
from ui.Widget import Widget

import base64


class Applet(Component, Widget):
    """
    Base class for applets.
    @since: 2009.10.18
    """

    ICON = None
    """
    theme reference to the icon
    """

    TITLE = ""
    """
    title text of the applet
    """
    
    DESCRIPTION = ""
    """
    description text of the applet
    """
      

    def __init__(self):

        Component.__init__(self)
        Widget.__init__(self)


    def get_applet_id(self):
    
        return base64.urlsafe_b64encode(self.TITLE)

