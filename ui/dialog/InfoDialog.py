import platforms


class InfoDialog(object):

    def __init__(self, msg, parent):
    
        self.__message = msg
        self.__parent = parent
        
        
    def run(self):
    
        if (platforms.MAEMO4):
            import hildon
            hildon.hildon_banner_show_information(
                           self.__parent._get_window_impl(),
                           None, self.__message)

        elif (platforms.MAEMO5):
            import hildon
            hildon.hildon_banner_show_information(
                           self.__parent._get_window_impl(),
                           "", self.__message)

        else:
            print self.__message

