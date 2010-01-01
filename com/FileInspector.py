"""
Base class for FileInspector components.
"""


from Component import Component


class FileInspector(Component):

    def __init__(self):
    
        Component.__init__(self)


    def get_mime_types(self):
        """
        Returns supported MIME types as a list of strings. The Wild card '*'
        may be used in the form of 'audio/*'. Wildcard MIME types are consulted
        only as a last resort when looking for an appropriate inspector.
        
        @return: list of strings
        """    
        
        return []
        
        
    def inspect(self, entry):
    
        pass

