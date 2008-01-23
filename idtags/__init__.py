# This package provides a quick and dirty tag parser for quickly finding
# tags in a media file. It just aims to be quick, but not necessarily correct.
# Well, it works for me (TM).


import oggtags
import id3v1tags
import id3v2tags


def read(filename):

    try:
        #print "Scanning", filename
        fd = open(filename, "r")               
    except:
        return {}
        
    tagtype = fd.read(3)
    major, minor = fd.read(1), fd.read(1)
    fd.seek(0)

    try:
        if (tagtype == "Ogg"):
            return oggtags.read(fd)
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

    finally:
        fd.close()
        
    
    
if (__name__ == "__main__"):
    import sys
    read(sys.argv[1]).keys()
        
