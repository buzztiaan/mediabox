from com import Component, msgs


class Initialiser(Component):
    """
    Performs initialisation tasks such as setting the theme.
    """

    def __init__(self):

        from mediabox import config
        from theme import theme
        import platforms
        from mediabox import values

    
        Component.__init__(self)
        
        # set theme
        try:
            theme.set_theme(config.theme())
        except:
            # theme could not be loaded; using default theme
            pass

        # utterly dirty hack no longer necessary when playing media through MAFW
        """
        # make MediaBox play sound in silent mode
        if (platforms.MAEMO5):
            import gobject
            gobject.set_application_name("FMRadio")
        """

        # satisfy maemo activation framework
        if (platforms.MAEMO4):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)
            
        elif (platforms.MAEMO5):
            platforms.create_osso_context(values.OSSO_NAME, "1.0", False)

