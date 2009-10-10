"""
Parser for Media Tags
=====================

This package provides a quick and dirty tag parser for quickly finding
tags in a media file. It just aims to be quick, but not necessarily correct.
Well, it works for me (TM).

B{Do not use these functions directly in MediaBox. Use L{mediabox.tagreader}
instead.}
"""


import flactags
import oggtags
import id3v1tags
import id3v2tags
import trackertags



def read_fd(fd):
    """
    Reads tags from the given file descriptor.
    
    @param fd: file descriptor
    @return: dictionary of tags
    """

    tagtype = fd.read(3)
    major, minor = fd.read(1), fd.read(1)

    try:
        fd.seek(0)

        # try tracker first
        tags = trackertags.read(fd)
        if (tags):
            return tags

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
    """
    Reads tags from the given local file.
    
    @param filename: path of file
    @return: dictionary of tags
    """

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
    import time
    
    now = time.time()
    for k, v in read(sys.argv[1]).items():
        if (len(v) < 80):
            print "%s:\t%s" % (k, v)
    print "took %0.5f seconds" % (time.time() - now)

