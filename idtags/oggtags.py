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
            value = e[idx + 1:-1]
            tags[key.upper()] = value
    #end for

    return tags



def read(filename):

    try:
        fd = open(filename, "r")
    except:
        return {}
        
    block = fd.read(1024)
    
    idx = block.find("\x03vorbis")    
    if (idx != -1):
        fd.seek(idx + len("\x03vorbis"))
        tagsoup = _read_tagsoup(fd)
        tags = _parse_tagsoup(tagsoup)
    else:
        tags = {}

    fd.close()        
    return tags
        
if (__name__ == "__main__"):
    import sys
    
    print read(sys.argv[1])
    
