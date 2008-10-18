"""
Parser for FLAC tags.
"""


def _read_int(fd, size):

    bytes = fd.read(size)
    i = 0
    for b in bytes: i = (i << 8) + ord(b)
    return i


def _read_tagsoup(fd):

    # skip STREAMINFO block
    btype = fd.read(1)
    size = _read_int(fd, 3)
    block = fd.read(size)

    # read VORBIS_COMMENT block
    btype = fd.read(1)
    if (ord(btype) & 0x04):
        size = _read_int(fd, 3)
        if (size < 50000):
            # most likely not a comment block
            soup = fd.read(size)
        else:
            soup = ""
    else:
        soup = ""
        
    return soup           


def _parse_tagsoup(soup):

    tags = {}
    entries = soup.split("\x00\x00\x00")
    for e in entries:
        idx = e.find("=")
        if (idx != -1):
            key = e[:idx]
            #print "  " + key
            value = e[idx + 1:-1]
            tags[key.upper()] = value
    #end for

    return tags



def read(fd):

    #print "Reading FLAC tags"       
    marker = fd.read(4)    
    if (marker == "fLaC"):
        tagsoup = _read_tagsoup(fd)
        tags = _parse_tagsoup(tagsoup)
    else:
        tags = {}
      
    return tags
    
