from com import Component, msgs
from mediabox import config
from theme import theme


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

