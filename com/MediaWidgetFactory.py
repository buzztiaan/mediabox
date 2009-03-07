"""
Base class for media widget factory components.
"""

from Component import Component
from ui.Widget import Widget


class MediaWidgetFactory(Component):
    """
    Base class for media widget factory components.
    This component type is used by the MediaWidgetRegistry to create instances
    of media rendering widgets for handling MIME types.
    
    The MediaWidgetRegistry queries all registered MediaWidgetFactories to find
    one that handles a certain MIME type. This factory will then produce the
    appropriate MediaWidget.

    @since: 0.96
    """

    def __init__(self):

        Component.__init__(self)

    
    def get_mimetypes(self):
        """
        Returns a list of supported mimetypes. 'C{*}' can be used as a wildcard
        in the form: C{image/*}
        @since: 0.96
        
        @return: list of supported mimetypes
        """
    
        return []


    def get_widget_class(self, mimetype):
        """
        Returns the class of a MediaWidget handling the given MIME type.
        @since: 0.96
        
        @param mimetype: MIME type
        @return: class of appropriate MediaWidget
        """
    
        pass
