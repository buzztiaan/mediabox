"""
Base class for observable objects.

@copyright: 2002 - 2008
@author: Martin Grimme  <martin.grimme@lintegra.de>

@license: This module is licensed under the terms of the GNU LGPL.
"""


class Observable(object):
    """
    Base class for observable objects.
    
    Classes derived from this class do not have to call
    C{Observable.__init__}.
    
    @since: 0.90
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
        """
        Registers the given observer function.
        @since: 0.90
        
        @param observer: callback function
        """

        self.__ensure_init()
        self.__handlers.append(observer)



    def remove_observer(self, observer):
        """
        Removes the given observer function.
        @since: 0.90
        
        @param observer: callback function
        """

        self.__ensure_init()
        self.__handlers.remove(observer)



    def drop_observers(self):
        """
        Drops (i.e. forgets about) all registered observers at once.
        @since: 0.90
        """

        self.__ensure_init()
        self.__handlers = []



    def update_observer(self, *args):
        """
        Notifes all registered observers about an update.
        @since: 0.90
        
        @param *args: variable list of arguments to the observer
        """

        self.__ensure_init()

        handled = False
        for h in self.__handlers[:]:
            handled |= h(self, *args) or False
            
        return handled

