import os

_formats = {}
_order = []

# read format map
fmt_file = os.path.join(os.path.dirname(__file__), "formats.dat")
for line in open(fmt_file, "r").readlines():
    line = line.strip()
    if (not line or line.startswith("#")):
        continue
    else:
        fmt, container, descr = line.split(",")
        _formats[int(fmt)] = (container.strip(), descr.strip())
        _order.append(int(fmt))
#end for




def get_container(fmt):

    try:
        return _formats[fmt][0]
    except:
        return ""
        
        
def get_description(fmt):

    try:
        return _formats[fmt][1]
    except:
        return ""


def get_formats():

    fmts = _formats.keys()
    fmts.sort()
    return fmts


def get_extensions():

    return [ "." + get_container(fmt) for fmt in get_formats() ]


def comparator(a, b):

    return cmp(_order.index(a), _order.index(b))

