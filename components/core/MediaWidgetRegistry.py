from com import Component, MediaWidgetFactory, msgs
from utils import logging


class MediaWidgetRegistry(Component):
    """
    The MediaWidgetRegistry is a core service where components query for
    media rendering widgets handling certain MIME types.
    
    New media rendering widgets for new MIME types can be added as classes
    derived from the mediabox.MediaWidget class.
    """
    
    def __init__(self):
    
        self.__factories = []
        
        # table: (caller_id, clss) -> widget
        self.__widget_cache = {}
    
        Component.__init__(self)
    
    
    def __match_mimetypes(self, mimetype, mtlist):

        a1, a2 = mimetype.split("/")    
        for mt in mtlist:
            b1, b2 = mt.split("/")
    
            if (a1 == b1):
                match_1 = True
            elif (b1 == "*"):
                match_1 = True
            else:
                match_1 = False

            if (a2 == b2):
                match_2 = True
            elif (b2 == "*"):
                match_2 = True
            else:
                match_2 = False
                
            if (match_1 and match_2):
                if ("*" in (b1, b2)):
                    return 1
                else:
                    return 2
                
        #end for
        
        return 0
    
    
    
    def handle_event(self, ev, *args):
    
        if (ev == msgs.COM_EV_COMPONENT_LOADED):
            component = args[0]
            if (isinstance(component, MediaWidgetFactory)):
                logging.debug("found media widget factory: [%s]" % component)
                self.__factories.append(component)


        elif (ev == msgs.MEDIAWIDGETREGISTRY_SVC_GET_WIDGET):
            caller_id, mimetype = args
            
            # this is not time critical, so we simply iterate through a list
            factory = None
            for f in self.__factories:
                match_level = self.__match_mimetypes(mimetype,
                                                     f.get_mimetypes())
                #print "match level", match_level, f.get_mimetypes()
                if (match_level == 2):
                    factory = f
                    break
                elif (match_level == 1):
                    factory = f
            #end for
            
            if (factory):
                clss = factory.get_widget_class(mimetype)
                if (clss):
                    obj = self.__widget_cache.get((caller_id, clss)) or clss()
                    self.__widget_cache[(caller_id, clss)] = obj
                    return obj
                else:
                    return 0
            else:
                return 0

