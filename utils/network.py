import urlparse


def parse_addr(addr):
    """
    Splits the given address URL into a tuple
    C{(host, port, path)}.
    
    @param addr: address URL
    @return: C{(host, port, path)}
    """
        
    urlparts = urlparse.urlparse(addr)
    
    netloc = urlparts.netloc.split(":")[0]
    path = urlparts.path
    if (urlparts.query):
        path += "?" + urlparts.query
    return (netloc, int(urlparts.port or 0), path)

