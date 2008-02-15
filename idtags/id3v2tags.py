import mapping

class REV2:
    version = "v2.2"
    key_length = 3
    size_length = 3
    syncsafe = False
    has_flags = False
    flag_compressed = 0
    flag_encrypted = 0
    flag_ingroup = 0
    encodings = ()

class REV3:
    version = "v2.3"
    key_length = 4
    size_length = 4
    syncsafe = False
    has_flags = True
    flag_compressed = 0x0080
    flag_encrypted = 0x0040
    flag_ingroup = 0x0020
    encodings = ("latin1", "utf-16", "utf_16_be", "utf-8")

class REV4:
    version = "v2.4"
    key_length = 4
    size_length = 4
    syncsafe = True
    has_flags = True
    flag_compressed = 0x0008
    flag_encrypted = 0x0004
    flag_ingroup = 0x0002
    encodings = ("latin1", "utf-16", "utf_16_be", "utf-8")
    

def _read_tagsoup(fd):

    fd.read(3)
    vmaj = ord(fd.read(1))
    vrev = ord(fd.read(1))
    flags = fd.read(1)
    
    size = (ord(fd.read(1)) << 21) + \
           (ord(fd.read(1)) << 14) + \
           (ord(fd.read(1)) << 7) + \
           ord(fd.read(1))
    
    soup = fd.read(size - 10)
    #print "Size: " + hex(len(soup)) + ", Flags: " + hex(ord(flags))

    return soup


def _read_frame(soup, pos, params):
    
    if (pos > len(soup) - 10 or soup[pos:pos + 2] == "\x00\x00"): return None
    key = soup[pos:pos + params.key_length]    
    pos += params.key_length
    
    bytes = [ ord(b) for b in soup[pos:pos + params.size_length] ]
    if (params.syncsafe):
        size = (bytes[0] << 21) + (bytes[1] << 14) + (bytes[2] << 7) + bytes[3]
    else:
        i = 0
        for b in bytes: i = (i << 8) + b
        size = i
    pos += params.size_length
        
    if (params.has_flags):
        flags = (ord(soup[pos]) << 8) + ord(soup[pos + 1])
        pos += 2        
    else:
        flags = 0

    if (flags & params.flag_compressed):
        try:
            value = soup[pos + 4:pos + size].decode("zlib")
        except:
            try:
                value = soup[pos:pos + size].decode("zlib")
            except:
                print "  zlib decoding error on", key
                value = ""
    else:
        value = soup[pos:pos + size]
        if (params.encodings and ord(value[0]) < 5):
            encoding = params.encodings[ord(value[0])]
            value = value[1:].decode(encoding, "replace")
        
    #print "  " + key, hex(size), size < 60 and value or "<binary>"

    key = mapping.MAPPING.get(key, key)
    
    # strip off unwanted characters
    if (size < 512):
        value = "".join([ c for c in list(value) if ord(c) >= 0x20 ])
        
    return (key, value, pos + size)
    
    

def _parse_tagsoup(soup, params):

    tags = {}
    pos = 0
    while (True):
        result = _read_frame(soup, pos, params)
        if (not result): break
        key, value, pos = result
        tags[key] = value
    #end while
    
    return tags


def read(fd, params):

    #print "Reading ID3v2 tags", params.version
    tagsoup = _read_tagsoup(fd)
    tags = _parse_tagsoup(tagsoup, params)

    return tags

