def get_devices():

    if (not platforms.MAEMO5):
        # not Maemo5-ready yet
        from WorldTV import WorldTV
        return [WorldTV]
    else:
        return []

