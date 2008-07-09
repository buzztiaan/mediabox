from Mediator import Mediator
import msgs

class Component(Mediator):
    """
    Base class for components.
    """

    def __init__(self):
    
        Mediator.__init__(self)

