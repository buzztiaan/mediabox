"""
Parser for Ogg tags.
"""

import parser
import mapping
import base64


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
            
            if (key.upper() == "GENRE"):
                value = mapping.resolve_genre(value)

            elif (key.upper() == "METADATA_BLOCK_PICTURE"):
                value = parser.parse_metadata_block_picture(value)

            elif (key.upper() == "COVERARTMIME"):
                idx = value.find("=")
                if (idx != -1):
                    key = "COVERART"
                    value = value[idx + 1:]

            if (key.upper() == "COVERART"):
                try:
                    value = base64.b64decode(value)
                except:
                    value = ""

            key = mapping.MAPPING.get(key, key)
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
    
