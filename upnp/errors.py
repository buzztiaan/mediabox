# UPnP errors as specified by the UPnP Forum

INVALID_ACTION = (401, "Invalid Action")
INVALID_ARGS = (402, "Invalid Args")
ACTION_FAILED = (501, "Action Failed")
ARGUMENT_VALUE_INVALID = (600, "Argument Value Invalid")
ARGUMENT_VALUE_OUT_OF_RANGE = (601, "Argument Value Out of Range")
OPTIONAL_ACTION_NOT_IMPLEMENTED = (602, "Optional Action Not Implemented")
OUT_OF_MEMORY = (603, "Out of Memory")
HUMAN_INTERVENTION_REQUIRED = (604, "Human Intervention Required")
STRING_ARGUMENT_TOO_LONG = (605, "String Argument Too Long")
ACTION_NOT_AUTHORIZED = (606, "Action not authorized")
SIGNATURE_FAILURE = (607, "Signature failure")
SIGNATURE_MISSING = (608, "Signature missing")
NOT_ENCRYPTED = (609, "Not encrypted")
INVALID_SEQUENCE = (610, "Invalid sequence")
INVALID_CONTROL_URL = (611, "Invalid control URL")
NO_SUCH_SESSION = (612, "No such session")


class UPnPError(StandardError):

    def __init__(self, error):
    
        self.__error = error
        
    def get_error(self):
    
        return self.__error

