# This package provides a quick and dirty tag parser for quickly finding
# tags in a media file. It just aims to be quick, but not necessarily correct.
# Well, it works for me (TM).


import flactags
import oggtags
import id3v1tags
import id3v2tags



def read_fd(fd):

    tagtype = fd.read(3)
    major, minor = fd.read(1), fd.read(1)

    try:
        fd.seek(0)

        if (tagtype == "Ogg"):
            return oggtags.read(fd)
        elif (tagtype == "fLa"):
            return flactags.read(fd)
        elif (tagtype == "ID3"):
            if (major == "\x02"):
                return id3v2tags.read(fd, id3v2tags.REV2)
            elif (major == "\x03"):
                return id3v2tags.read(fd, id3v2tags.REV3)
            else:
                return id3v2tags.read(fd, id3v2tags.REV4)
        else:
            fd.seek(-128, 2)
            tag = fd.read(3)
            if (tag == "TAG"): return id3v1tags.read(fd)

        return {}
    
    except:
        import traceback; traceback.print_exc()
        return {}



def read(filename):

    try:
        #print "Scanning", filename
        fd = open(filename, "r")               
    except:
        return {}

    try:
        return read_fd(fd)    

    except:
        import traceback; traceback.print_exc()
        return {}
        
    finally:
        fd.close()
        
    
    
if (__name__ == "__main__"):
    import sys
    read(sys.argv[1]).keys()
        
