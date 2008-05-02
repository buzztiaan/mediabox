class Observable(object):
    """
    Base class for observable objects.
    """

    def __ensure_init(self):
        """
        Ensures that the observable is initialized.
        The user doesn't have to call the constructor explicitly.
        """

        try:
            self.__handlers
        except:
            self.__handlers = []



    def add_observer(self, observer):

        self.__ensure_init()
        self.__handlers.append(observer)



    def remove_observer(self, observer):

        self.__ensure_init()
        self.__handlers.remove(observer)



    def drop_observers(self):

        self.__ensure_init()
        self.__handlers = []



    def update_observer(self, *args):

        self.__ensure_init()

        handled = False
        for h in self.__handlers[:]:
            handled |= h(self, *args) or False
            
        return handled

