from Mediator import Mediator
import events

class Component(Mediator):
    """
    Base class for components.
    """

    def __init__(self):
    
        Mediator.__init__(self)

