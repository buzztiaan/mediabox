def get_classes():

    from Input import Input
    return [Input]



import __messages__
messages = [ m for m in dir(__messages__) if not m.startswith("__") ]

