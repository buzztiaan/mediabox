from com import Component, msgs
from mediabox import config
from theme import theme
import platforms
from mediabox import values


class Initialiser(Component):
    """
    Performs initialisation tasks such as setting the theme.
    """

    def __init__(self):
    
        Component.__init__(self)
        
        # set theme
        try:
            theme.set_theme(config.theme())
        except:
            # theme could not be loaded; using default theme
            pass

        # satisfy maemo activation framework
        if (platforms.PLATFORM == platforms.MAEMO4):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)
            
        elif (platforms.PLATFORM == platforms.MAEMO5):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)
