from utils.Observable import Observable


class RadioBackend(Observable):
    """
    Abstract base class for radio backends.
    """
    
    OBS_TITLE = 0
    OBS_LOCATION = 1
    
    OBS_ERROR = 2
    OBS_PLAY = 3
    OBS_STOP = 4
    
    OBS_ADD_STATION = 5
    OBS_REMOVE_STATION = 6
    
    OBS_MESSAGE = 7
    OBS_WARNING = 8
    
