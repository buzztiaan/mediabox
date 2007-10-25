# This package provides a quick and dirty tag parser for quickly finding
# tags in a media file. It just aims to be quick, but not necessarily correct.
# Well, it works for me (TM).


import oggtags
import id3tags


def read(filename):

    try:
        fd = open(filename, "r")
    except:
        return {}
        
    tagtype = fd.read(3)
    fd.close()
    
    if (tagtype == "Ogg"): return oggtags.read(filename)
    elif (tagtype == "ID3"): return id3tags.read(filename)
    else: return {}
