from com import View, Player, msgs


class MediaView(View):

    TITLE = "Player"
    PRIORITY = 10

    def __init__(self):
    
        # table: MIME type -> [handlers]
        self.__mime_handlers = {}
        
        self.__current_player = None
        
    
        View.__init__(self)


    def __register_player(self, player):
    
        # ask player for MIME types
        for mt in player.get_mime_types():
            l = self.__mime_handlers.get(mt, [])
            l.append(player)
            self.__mime_handlers[mt] = l
        #end for
        
        # add player widget
        player.set_visible(False)
        self.add(player)


    def render_this(self):
    
        x, y = self.get_screen_pos()
        w, h = self.get_size()
        screen = self.get_screen()
        
        if (self.__current_player):
            self.__current_player.set_geometry(0, 0, w, h)
        else:
            screen.fill_area(x, y, w, h, "#000000")


    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        # look for players
        if (isinstance(comp, Player)):
            self.__register_player(comp)


    def handle_MEDIA_ACT_LOAD(self, f):
    
        mimetype = f.mimetype
        handlers = self.__mime_handlers.get(mimetype)

        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            return

        if (self.__current_player):
            self.__current_player.set_visible(False)
            
        self.__current_player = handlers[0]
        self.__current_player.set_visible(True)
        self.__current_player.load(f)
        self.set_title(f.name)

