class InfoDialog(object):

    def __init__(self, msg, parent):
    
        self.__message = msg
        self.__parent = parent
        
        
    def run(self):
    
        try:
            import hildon
            hildon.hildon_banner_show_information(
                           self.__parent._get_window_impl(),
                           "stock-info", self.__message)
        except:
            print self.__message

