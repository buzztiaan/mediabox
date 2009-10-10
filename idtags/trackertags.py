"""
Dummy parser for reading tags from the tracker database.
"""

import mapping
import commands
import os


_TRACKER_INFO = "/usr/bin/tracker-info"


def _read_tagsoup(fd):

    path = fd.name

    path = path.replace("\"", "\\\"")
    fail, soup = commands.getstatusoutput(_TRACKER_INFO + " -s Audio \"" + path + "\"")
    if (fail):
        return ""
    else:
        return soup


def _parse_tagsoup(soup):

    tags = {}
    for line in soup.splitlines()[1:]:
        idx1 = line.find("'")
        idx2 = line.find("'", idx1 + 1)
        idx3 = line.find("=")
        key = mapping.MAPPING.get(line[idx1 + 1:idx2], "")
        if (not key): continue
        value = line[idx3 + 1:].strip()[1:-1]

        if (key.upper() == "GENRE"):
            value = mapping.resolve_genre(value)

        tags[key.upper()] = value
    #end for
    
    return tags


def read(fd):

    if (os.path.exists(_TRACKER_INFO)):
        tagsoup = _read_tagsoup(fd)
        tags = _parse_tagsoup(tagsoup)
    else:
        tags = {}
      
    return tags

