def load(path):
    """
    Loads the given M3U playlist and returns its contents as a list of
    (location, name) tuples.
    """

    items = []
    
    try:
        lines = open(path, "r").readlines()
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
            items.append((location, name))
    #end for
    
    return items
    
    
    
def save(path, items):
    """
    Saves the given playlist items to the given file.
    Items is a list of (location, name) tuples.
    """

    out = ""
    out += "#EXTM3U\n"
    
    for location, name in items:
        out += "#EXTINF:-1,%s\n" % name
        out += "%s\n" % location

    try:
        open(path, "w").write(out)
    except:
        pass

