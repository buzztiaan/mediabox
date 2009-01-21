try:
    # GNOME
    import gconf
except:
    try:
        # Maemo    
        import gnome.gconf as gconf
    except:
        # last resort...
        from utils import gconftool as gconf
    

_CLIENT = gconf.client_get_default()
_PREFIX = "/apps/maemo/fmradio/frequency_key/"

    
def get_stations():
    """
    Returns the list of stations saved by the maemo FM radio application.
    Returns an empty list if no stations are available.
    """
    
    stations = []
    i = 0
    while (True):
        entry = _CLIENT.get_string(_PREFIX + `i`)
        print "E", entry
        if (not entry): break
        
        parts = entry.split(";Channel Name:")
        freq = parts[0]
        freq = freq[freq.rfind(":") + 1:]
        freq = int(float(freq) * 1000)
        name = parts[1]
        stations.append((freq, name))
        i += 1
    #end while
    
    return stations
    
    
def save_stations(stations):

    i = 0
    while (True):
        entry = _CLIENT.get_string(_PREFIX + `i`)
        if (entry): _CLIENT.unset(_PREFIX + `i`)
        else: break
        i += 1
    #end while
        
    i = 0
    for freq, name in stations:
        s_freq = ("%6.2f" % (freq / 1000.0)).replace(" ", "0")
        entry = "Frequency:%s;Channel Name:%s" % (s_freq, name)
        _CLIENT.set_string(_PREFIX + `i`, entry)
        i += 1
    #end for
    
