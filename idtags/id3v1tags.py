import mapping


def _read_tagsoup(fd):

    fd.seek(-128, 2)
    return fd.read(128)


def _parse_tagsoup(soup):

    tags = {}

    tag = soup[0:3]
    tags["TITLE"] = soup[3:33].strip("\x00")
    tags["ARTIST"] = soup[33:63].strip("\x00")
    tags["ALBUM"] = soup[63:93].strip("\x00")
    tags["YEAR"] = soup[93:97].strip("\x00")
    if (soup[125] == "\x00" and soup[126] != "\x00"):
        # ID3v1.1        
        tags["COMMENT"] = soup[97:125].strip("\x00")
        tags["TRACKNUMBER"] = `ord(soup[126])`
    else:
        # ID3v1
        tags["COMMENT"] = soup[97:127].strip("\x00")
    tags["GENRE"] = mapping.GENRES[ord(soup[127])]

    return tags



def read(fd):

    #print "Reading ID3v1 tags"     
    tagsoup = _read_tagsoup(fd)
    tags = _parse_tagsoup(tagsoup)
             
    return tags

