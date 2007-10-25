_MAPPING = { "TCOP": "COPYRIGHT",
             "TDOR": "DATE",
             "TIT2": "TITLE",
             "TLEN": "LENGTH",
             "TPE1": "ARTIST",
             "TALB": "ALBUM",
             "TOAL": "ALBUM",
             "TCON": "GENRE",
             "TRCK": "TRACKNUMBER" }


def _read_tagsoup(fd):

    vmaj = fd.read(1)
    vrev = fd.read(1)
    flags = fd.read(1)
    
    size = (ord(fd.read(1)) << 24) + \
           (ord(fd.read(1)) << 16) + \
           (ord(fd.read(1)) << 8) + \
           ord(fd.read(1))
    
    soup = fd.read(size - 10)
    return soup            


def _parse_tagsoup(soup):

    tags = {}
    pos = 0
    while (pos < len(soup)):
        idx = soup.find("\x00", pos)
        if (idx == -1 or soup[pos:pos + 2] == "\x00\x00"): break
        
        key = soup[pos:idx]
        key = _MAPPING.get(key, key)
        size = ord(soup[idx + 3])

        pos = idx + 6
        idx = pos + size
        value = soup[pos:idx]        
        pos = idx
        
        # strip off unwanted characters
        value = "".join([ c for c in list(value) if ord(c) >= 0x20 ])
        
        tags[key] = value.strip()
    #end while
        
    return tags



def read(filename):

    try:
        fd = open(filename, "r")
    except:
        return {}
        
    block = fd.read(3)
    if (block == "ID3"):
        tagsoup = _read_tagsoup(fd)
        tags = _parse_tagsoup(tagsoup)
    else:
        tags = {}
        
    fd.close()        
    return tags
        
if (__name__ == "__main__"):
    import sys
    
    print read(sys.argv[1])
    
