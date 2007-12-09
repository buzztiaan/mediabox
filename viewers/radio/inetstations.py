import os


_PLAYLIST = os.path.expanduser("~/.mediaplayer-engine/radiochannels.m3u")
   

    
def get_stations():
    """
    Returns the list of internet radio stations saved by the maemo mediaplayer.
    Returns an empty list if no stations are available.
    """
    
    stations = []
    
    try:
        lines = open(_PLAYLIST, "r").readlines()
    except:
        return []
        
    name = ""
    location = ""
    for line in lines:
        line = line.strip()
        if (not line): continue
        
        if (line.startswith("#EXTINF:")):
            idx = line.find(",")
            name = line[idx + 1:]
        elif (line.startswith("#")):
            pass
        else:
            location = line
            stations.append((location, name))
    #end for
    
    return stations

    
    
def save_stations(stations):

    out = ""
    out += "#EXTM3U\n"
    
    for location, name in stations:
        out += "#EXTINF:-1,%s\n" % name
        out += "%s\n" % location

    try:
        open(_PLAYLIST, "w").write(out)
    except:
        pass

