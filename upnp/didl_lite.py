"""
Parser for DIDL-Lite directory data.
"""

from MiniXML import MiniXML


_XMLNS_DIDL = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
_XMLNS_UPNP = "urn:schemas-upnp-org:metadata-1-0/upnp/"
_XMLNS_DC = "http://purl.org/dc/elements/1.1/"


class _Item(object):
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.id = ""
        self.child_count = 0
        self.res = ""
        self.clss = ""


def parse(xml):
    """
    Parses the given DIDL-Lite XML and returns a list of items.
    """

    items = []
    didl = MiniXML(xml).get_dom()
    for c in didl.get_children():
        item = _parse_entry(c)
        if (item):
            items.append(item)
    #end for
    
    return items
    
    
    
def _parse_entry(node):

    if (node.get_name() == "{%s}item" % _XMLNS_DIDL):
        return _parse_item(node)
    elif (node.get_name() == "{%s}container" % _XMLNS_DIDL):
        return _parse_container(node)
    else:
        return None
        

def _parse_item(node):

    try:
        # these are mandatory
        ident = node.get_attr("{%s}id" % _XMLNS_DIDL)
        res = node.get_pcdata("{%s}res" % _XMLNS_DIDL)
        clss = node.get_pcdata("{%s}class" % _XMLNS_UPNP)
        title = node.get_pcdata("{%s}title" % _XMLNS_DC)
    except:
        return None

    try:
        artist = node.get_pcdata("{%s}artist" % _XMLNS_UPNP)
    except:
        artist = ""
    
    return (ident, clss, 0, res, title, artist)
    
        
def _parse_container(node):

    try:
        ident = node.get_attr("{%s}id" % _XMLNS_DIDL)
        child_count = int(node.get_attr("{%s}childCount" % _XMLNS_DIDL))
    
        clss = node.get_pcdata("{%s}class" % _XMLNS_UPNP)
        title = node.get_pcdata("{%s}title" % _XMLNS_DC)
    except:
        return None

    return (ident, clss, child_count, "", title, "")

    
    
if (__name__ == "__main__"):
    import sys
    didl = open(sys.argv[1]).read()
    print [ d.title for d in parse(didl) ]
    
