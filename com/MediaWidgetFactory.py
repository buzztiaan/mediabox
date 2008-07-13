from Component import Component
from ui.Widget import Widget


class MediaWidgetFactory(Component):
    """
    This component type is used by the MediaWidgetRegistry to create instances
    of media rendering widgets for handling MIME types.
    """

    def __init__(self):

        Component.__init__(self)

    
    def get_mimetypes(self):
        """
        Returns a list of supported mimetypes. '*' can be used as a wildcard
        in the forms: image/*, *
        """
    
        return []


    def get_widget_class(self, mimetype):
    
        pass
