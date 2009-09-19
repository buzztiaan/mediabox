import logging

import gobject


class ItemScheduler(object):
    """
    Class for scheduling item tasks, such as thumbnailing.
    @since: 0.97
    """
    
    def __init__(self):
    
        self.__scheduler = None
    
        self.__interval = 100
        self.__handler = None
        self.__items = []
        
        self.__priorized_pos = 0
        
        
    def __iteration(self):

        if (self.__items):
            self.__priorized_pos = min(self.__priorized_pos, 
                                       len(self.__items) - 1)
            item, args = self.__items.pop(self.__priorized_pos)

            try:
                self.__handler(item, *args)
            except:
                logging.error("error in item scheduler:\n%s", logging.stacktrace())

            return True
            
        else:
            self.__scheduler = None
            return False

        
    def new_schedule(self, interval, handler):
        """
        Clears the current schedule and starts a new one.
        
        @param interval: interval between iterations in milliseconds
        @param handler: handler function that gets called each iteration
        """
    
        self.__items = []
        self.__handler = handler
        self.__interval = interval
        self.__priorized_pos = 0

        self.resume()
        
        
    def is_halted(self):
        """
        Returns whether the current schedule is halted.
        
        @return: whether the schedule is halted
        """
        
        if (self.__scheduler):
            return True
        else:
            return False
        
        
    def halt(self):
        """
        Halts the current schedule.
        """

        if (self.__scheduler):
            gobject.source_remove(self.__scheduler)
            self.__scheduler = None
        
        
    def resume(self):
        """
        Resumes the current schedule.
        """

        if (self.__scheduler):
            gobject.source_remove(self.__scheduler)

        self.__scheduler = gobject.timeout_add(self.__interval, self.__iteration)
        
        
    def add(self, item, *args):
        """
        Adds the given item to the current schedule.
        @param item: object
        @param args: variable list of user arguments to the handler function
        """
        
        self.__items.append((item, args))

        
    def priorize(self, item):
        """
        Priorizes the given item. The next iteration will handle the given
        item.
        
        @param item: object
        """
        
        pos = 0
        for i in self.__items:
            if (i[0] is item):
                self.__priorized_pos = pos
                break
            else:
                pos += 1
        #end for

