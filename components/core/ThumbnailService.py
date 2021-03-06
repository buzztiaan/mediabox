from com import Component, msgs
from utils import logging


class ThumbnailService(Component):
    """
    Component for creating and looking up thumbnail previews, delegating
    thumbnail creation to Thumbnailer components.
    """

    def __init__(self):

        # table: MIME type -> [handlers]
        self.__mime_handlers = {}

        # table: name -> handler
        self.__thumbnailers = {}

    
        Component.__init__(self)
    

    def __register_thumbnailer(self, thumbnailer):
        """
        Registers the given Thumbnailer component.
        """
    
        # ask thumbnailer for MIME types
        for mt in thumbnailer.get_mime_types():
            l = self.__mime_handlers.get(mt, [])
            l.append(thumbnailer)
            self.__mime_handlers[mt] = l
        #end for
        self.__thumbnailers[str(thumbnailer)] = thumbnailer


    def handle_COM_EV_COMPONENT_LOADED(self, comp):

        from com import Thumbnailer as _Thumbnailer
        if (isinstance(comp, _Thumbnailer)):
            self.__register_thumbnailer(comp)


    def handle_THUMBNAIL_SVC_LOOKUP_THUMBNAIL(self, f):
        """
        Looks up and returns a quick thumbnail, generated by one of the
        Thumbnailer components.
        """

        handlers = []

        # the file object may state the desired thumbnailer
        if (f.thumbnailer):
            handlers = [ self.__thumbnailers.get(f.thumbnailer) ]
            #print handlers, self.__thumbnailers
            
        if (not handlers):
            mimetype = f.mimetype
            handlers = self.__mime_handlers.get(mimetype)

        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            return ("", True)

        try:
            return handlers[0].make_quick_thumbnail(f)
        except:
            return ("", True)


    def handle_THUMBNAIL_SVC_LOAD_THUMBNAIL(self, f, cb, *cb_args):
        """
        Generates a thumbnail asynchronously by one of the Thumbnailer
        components.
        """

        handlers = []

        # the file object may state the desired thumbnailer
        if (f.thumbnailer):
            handlers = [ self.__thumbnailers.get(f.thumbnailer) ]
            #print handlers, f

        if (not handlers):
            mimetype = f.mimetype
            handlers = self.__mime_handlers.get(mimetype)

        if (not handlers):
            m1, m2 = mimetype.split("/")
            handlers = self.__mime_handlers.get(m1 + "/*")

        if (not handlers):
            cb("", *args)
            return ""

        self.emit_message(msgs.THUMBNAIL_EV_LOADING)

        try:
            handlers[0].make_thumbnail(f, cb, *cb_args)
        except:
            import traceback; traceback.print_exc()
            cb("", *cb_args)
            return ""

        return 0

