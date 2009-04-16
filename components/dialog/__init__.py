def get_classes():

    from DialogService import DialogService
    return [DialogService]
    
    
messages = [
    "DIALOG_SVC_INFO",          # (header, text: response)
    "DIALOG_SVC_WARNING",       # (header, text: response)
    "DIALOG_SVC_ERROR",         # (header, text: response)
    "DIALOG_SVC_QUESTION",      # (header, text: response)
    "DIALOG_SVC_TEXT_INPUT",    # (header, text: response, text)
    "DIALOG_SVC_CUSTOM",        # (icon, header, widget: response)
]

