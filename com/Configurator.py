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
    
    The following properties have to be specified:
     - C{ICON} - theme reference to the icon which appears in the viewer
     - C{TITLE} - title text
     - C{DESCRIPTION} - a descriptive text (since 0.96.5) 

    Example::
    
      from com import Configurator, msgs
      from theme import theme
      
      
      class Prefs(Configurator):

          ICON = theme.myplugin_prefs
          TITLE = "Example Configurator"
          DESCRIPTION = "This example configurator is for didactic purpose"
      
          def __init__(self):
          
              Configurator.__init__(self)


    A configurator is a container widget where you add your widgets.

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

