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
import mapping



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
        #tags = trackertags.read(fd)
        #if (tags):
        #    return tags

        tags = {}
        if (tagtype == "Ogg"):
            tags = oggtags.read(fd)
        elif (tagtype == "fLa"):
            tags = flactags.read(fd)
        elif (tagtype == "ID3"):
            if (major == "\x02"):
                tags = id3v2tags.read(fd, id3v2tags.REV2)
            elif (major == "\x03"):
                tags = id3v2tags.read(fd, id3v2tags.REV3)
            elif (major == "\x04"):
                tags = id3v2tags.read(fd, id3v2tags.REV4)
            else:
                tags = id3v2tags.read(fd, id3v2tags.REV4)
        else:
            fd.seek(-128, 2)
            tag = fd.read(3)
            if (tag == "TAG"): tags = id3v1tags.read(fd)

        return _encode_strings(tags)
    
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


def _encode_strings(tags):

    for key in mapping.STRINGS:
        if (key in tags):
            v = str(tags[key])
            # strip off unicode byte order marks
            v = v.replace("\x00\x00\xfe\xff", "") \
                 .replace("\xff\xfe\x00\x00", "") \
                 .replace("\xef\xbb\xbf", "") \
                 .replace("\xff\xfe", "") \
                 .replace("\xfe\xff", "")
            tags[key] = v.encode("utf-8", "replace")
    #end for
    
    return tags

    
    
if (__name__ == "__main__"):
    import sys
    import time
    
    now = time.time()
    for k, v in read(sys.argv[1]).items():
        if (len(v) < 80):
            print "%s:\t%s" % (k, v)
        else:
            print "%s:\t[...] (%d chars)" % (k, len(v))
    print "took %0.5f seconds" % (time.time() - now)

