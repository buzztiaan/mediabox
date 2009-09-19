def escape_xml(s):

    s = s.decode("utf-8", "replace").encode("utf-8")
    return s.replace("<", "&lt;") \
            .replace(">", "&gt;") \
            .replace("&", "&amp;")
