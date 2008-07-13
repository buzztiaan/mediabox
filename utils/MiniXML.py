class MiniXML(object):
    """
    This is a tiny parser for a subset of XML with namespace support.
    This is useful when RAM is limited and we don't need a full-featured
    XML parser.
    """

    def __init__(self, data, namespace = "", callback = None):
        """
        Creates a new MiniXML object and parses the given XML data.
        If a namespace is given, it is used as the default namespace unless
        the XML overrides the default namespace.
        If a callback is given, the callback is being called every time a
        node has been closed and is thus finished.
        """

        self.__data = data
        self.__position = 0
        
        self.__callback = callback
        self.__cancelled = False

        self.__dom = None
        
        # stack of ancestor nodes
        self.__stack = []
        
        # stack for resolving namespaces
        self.__ns_stack = [{"": namespace}]

        self.__parse_document()


    def get_dom(self):
        """
        Returns the DOM representation of the XML tree. This does not
        adhere to the DOM specification.
        """

        return self.__dom


    def __parse_document(self):

        if (self.__callback):
            # run async
            import gobject
            gobject.timeout_add(0, self.__parser_iteration)
        else:
            # run sync
            while (self.__parser_iteration()): pass


    def __parser_iteration(self):

        if (self.__cancelled): return False

        # find next tag
        index = self.__data.find("<", self.__position)            
        if (index != -1):
            # skip comments
            if (self.__data[index:index + 4] == "<!--"):
                self.__position = self.__data.find("-->", index) + 3
                return True
        
            # read text up to next tag
            self.__read_text(self.__position, index)
            self.__position = index

            # check if its an opening or closing tag
            if (self.__data[index + 1] == "/"):
                self.__close_tag()
            else:
                self.__open_tag()
            
            return True
            
        else:
            return False
            


    def __read_text(self, begin, end):

        text = self.__data[begin:end]
        text = text.replace("\n", " ")
        text = text.replace("&lt;", "<") \
                   .replace("&gt;", ">") \
                   .replace("&quot;", "\"") \
                   .replace("&apos;", "'") \
                   .replace("&amp;", "&")
        if (text.strip()):
            node = _Node("", {})
            node.set_value(text)
            self.__push_node(node)
            self.__pop_node()


    def __parse_tag(self, tag):
    
        # normalize
        tag = tag.strip()
        if (tag[-1] == "/"): tag = tag[:-1]
        tag = tag.replace("\n", " ")

        # read tag name
        idx = tag.find(" ")
        if (idx > 0):
            tagname = tag[:idx]
            tag = tag[idx:].strip()
        else:
            tagname = tag
            tag = ""

        # read attributes
        # XML makes it easy to parse this since escaped quotes don't contain the
        # quote character and since every value must be enclosed in quotes    
        attrs = {}
        while (tag):
            # key
            idx = tag.find("=")
            if (idx == -1): break            
            key = tag[:idx].strip()
            tag = tag[idx + 1:].strip()
            
            # value
            quote = tag[0]
            idx = tag.find(quote, 1)
            if (idx == -1): break
            value = tag[1:idx]
            tag = tag[idx + 1:].strip()
            
            attrs[key] = value
        #end while

        return (tagname, attrs)


    def __lookup_namespace(self, ns):
    
        for i in range(len(self.__ns_stack) - 1, 0, -1):
            ns_table = self.__ns_stack[i]
            try:
                return ns_table[ns]
            except KeyError:
                pass
        #end for

        return ns


    def __resolve_namespaces(self, tagname, attrs):
    
        ns_table = {}
        self.__ns_stack.append(ns_table)
        
        # check attrs for new namespace definitions
        for key, value in attrs.items():
            if (key.startswith("xmlns:")):
                ns_name = key.split(":")[1]
                ns_table[ns_name] = value
            elif (key == "xmlns"):
                ns_table[""] = value
        #end for
        
        # check tagname
        if (":" in tagname):
            ns_name, tagname = tagname.split(":")
            ns = self.__lookup_namespace(ns_name)
            if (ns):
                tagname = "{" + ns + "}" + tagname
        else:
            ns = self.__lookup_namespace("")
            if (ns):
                tagname = "{" + ns + "}" + tagname
        #end if
        
        # check attrs
        items = attrs.items()
        for k, v in items:
            if (":" in k):
                ns, key = k.split(":")
                key = self.__lookup_namespace(ns) + ":" + key
                del attrs[k]
                attrs[key] = v
            else:
                ns = self.__lookup_namespace("")
                if (ns):
                    key = "{" + ns + "}" + k
                    del attrs[k]
                    attrs[key] = v                    
            #end if
        #end for

        return (tagname, attrs)
        

    def __open_tag(self):

        index = self.__data.find(">", self.__position + 1)
        tagdata = self.__data[self.__position + 1:index]
        self.__position = index + 1

        # skip control tags
        if (tagdata[0] == "?"):
            return
            
        tagname, attrs = self.__parse_tag(tagdata)
        tagname, attrs = self.__resolve_namespaces(tagname, attrs)

        if (tagname[-1] == "/"): tagname = tagname[:-1]

        node = _Node(tagname, attrs)
        self.__push_node(node)
        
        if (self.__data[index - 1] == "/"):
            self.__pop_node()
            self.__ns_stack.pop()
        

    def __close_tag(self):

        index = self.__data.find(">", self.__position + 1)
        #tagname = self.__data[self.__position + 2:index].rstrip()

        node = self.__pop_node()
        self.__ns_stack.pop()
        self.__position = index + 1
        
        if (self.__callback):
            try:
                v = self.__callback(node)
                if (not v): self.__cancelled = True
            except:
                import traceback; traceback.print_exc()


    def __push_node(self, node):

        if (self.__stack):
            parent = self.__stack[-1]
        else:
            parent = None

        if (parent):
            parent.add_child(node)
        else:
            self.__dom = node

        self.__stack.append(node)


    def __pop_node(self):

        return self.__stack.pop()




class _Node(object):
    """
    Class for representing a node in the DOM.
    """

    def __init__(self, tagname, attrs):
        """
        Creates a new node with the given tagname and attributes.
        Pass an empty tagname for PCDATA nodes.
        """

        self.__tagname = tagname
        self.__attrs = attrs
        self.__children = []
        self.__value = ""


    def add_child(self, child):
        """
        Adds a child node to this node.
        """

        self.__children.append(child)

    def get_name(self):
        """
        Returns the node name. The name is prefixed by its namespace, if any.
        PCDATA nodes have an empty node name.
        """

        return self.__tagname
        

    def get_attrs(self):
        """
        Returns the attributes of this node as a dictionary.
        """
    
        return self.__attrs


    def get_attr(self, key):
        """
        Returns the value of the given attribute.
        Raises a KeyError if the attribute does not exist.
        """
        
        return self.__attrs[key]


    def get_children(self):
        """
        Returns a list of this node's child nodes.
        """

        return self.__children
        
        
    def get_child(self, name = ""):
        """
        Convenience method for returning the child node with the given name,
        or the first child node if no name is given.
        Returns None if the child does not exist.
        """
    
        if (not name):
            return self.__children[0]
        else:
            for c in self.__children:
                if (name == c.get_name()):
                    return c
        return None
        
        
    def get_pcdata(self, name = ""):
        """
        Convenience function for returning the value of the PCDATA child
        node of this node.
        Returns "" if PCDATA is not available.
        """
        
        try:
            node = self.get_child(name)    
            return node.get_child().get_value()
        except:
            return ""
        

    def set_value(self, value):
        """
        Sets the PCDATA value.
        """
        self.__value = value


    def get_value(self):
        """
        Returns the PCDATA value.
        """

        return self.__value


    def _dump(self, indent = 0):
        """
        Recursively dumps the subtree beginning at this node.
        """
        
        out = ""
        if (self.__tagname):
            out += " " * indent
            out += "<%s" % self.__tagname
            attr_indent = indent + 1 + len(self.__tagname) + 1
            cnt = 0
            for k, v in self.__attrs.items():
                if (cnt > 0):
                    out += " " * attr_indent
                out += " %s=\"%s\"\n" % (k, v)
                cnt += 1
            out += ">\n"
            for c in self.__children:
                out += c._dump(indent + 2)
            out += " " * indent
            out += "</%s>\n" % self.__tagname
        else:
            out += " " * indent
            out += self.__value + "\n"
            
        return out


    def __str__(self):

        return self._dump()

        


if (__name__ == "__main__"):
    import sys
    xml = open(sys.argv[1]).read()
    m = MiniXML(xml)
    print m.get_dom()
    
