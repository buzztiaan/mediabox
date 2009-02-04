"""
Parser for Ogg tags.
"""


def _read_tagsoup(fd):

    soup = ""
    cnt = 0
    while (True):
        block = fd.read(512)        
        if (not block or cnt > 10):
            break
            
        soup += block
        idx = soup.find("\x05vorbis")
        if (idx != -1):
            return soup[:idx]

        cnt += 1
    #end while
            


def _parse_tagsoup(soup):

    tags = {}
    entries = soup.split("\x00\x00\x00")
    for e in entries:
        idx = e.find("=")
        if (idx != -1):
            key = e[:idx]
            #print "  " + key
            value = e[idx + 1:-1]
            
            if (key.upper() == "GENRE" and value.isdigit()):
                v = int(value)
                if (0 <= v < 256):
                    value = mapping.GENRES[int(value)]
            #end if

            tags[key.upper()] = value
    #end for

    return tags



def read(fd):

    #print "Reading Ogg tags"       
    block = fd.read(1024)
    
    idx = block.find("\x03vorbis")    
    if (idx != -1):
        fd.seek(idx + len("\x03vorbis"))
        tagsoup = _read_tagsoup(fd)
        tags = _parse_tagsoup(tagsoup)
    else:
        tags = {}
      
    return tags
    
