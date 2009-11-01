from ui.Widget import Widget
from utils.MiniXML import MiniXML

_PX  = 0
_PCT = 1
_LIKE_X1 = 2
_LIKE_Y1 = 3
_LIKE_X2 = 4
_LIKE_Y2 = 5


class Arrangement(Widget):
    """
    Layouter for complex arrangements of widgets.
    @since: 2009.10.29
    """

    EVENT_RESIZED = "event-resized"
    

    def __init__(self):
    
        # table: name -> widget
        self.__names = {}

        # table: widget -> (x1, y1, x2, y2)
        self.__constraints = {}
        
        # cache of arrangements, table: widget -> (x1, y1, x2, y2)
        self.__cache = {}
    
        Widget.__init__(self)
        
        
    def connect_resized(self, cb, *args):
    
        self._connect(self.EVENT_RESIZED, cb, *args)

        
    @staticmethod
    def px(v):
    
        return (_PX, v)


    @staticmethod
    def pct(v):
    
        return (_PCT, v)
        
        
    @staticmethod
    def like_x1(child):
    
        return (_LIKE_X1, child)


    @staticmethod
    def like_y1(child):
    
        return (_LIKE_Y1, child)


    @staticmethod
    def like_x2(child):
    
        return (_LIKE_X2, child)


    @staticmethod
    def like_y2(child):
    
        return (_LIKE_Y2, child)

        

    def __resolve_child(self, child):
    
        if (not child in self.__constraints):
            return (0, 0, 10, 10)
        
        x1, y1, x2, y2 = self.__constraints[child]
        w, h = self.get_size()
        
        if (child in self.__cache):
            real_x1, real_y1, real_x2, real_y2 = self.__cache[child]
        else:
            real_x1 = self.__resolve(x1, w)
            real_y1 = self.__resolve(y1, h)
            real_x2 = self.__resolve(x2, w)
            real_y2 = self.__resolve(y2, h)
            self.__cache[child] = (real_x1, real_y1, real_x2, real_y2)

        return (real_x1, real_y1, real_x2, real_y2)

        
    def __resolve(self, v, full_width):
    
        vtype, value = v
        if (vtype == _PX):
            if (value >= 0):
                return value
            else:
                return full_width + value 

        elif (vtype == _PCT):
            if (value >= 0):
                return int(full_width * (value / 100.0))
            else:
                return full_width + int(full_width * (value / 100.0)) 
        
        elif (vtype == _LIKE_X1):
            x1, y1, x2, y2 = self.__resolve_child(value)
            return x1

        elif (vtype == _LIKE_Y1):
            x1, y1, x2, y2 = self.__resolve_child(value)
            return y1

        elif (vtype == _LIKE_X2):
            x1, y1, x2, y2 = self.__resolve_child(value)
            return x2

        elif (vtype == _LIKE_Y2):
            x1, y1, x2, y2 = self.__resolve_child(value)
            return y2

        
    def set_size(self, w, h):
    
        prev_w, prev_h = self.get_size()
        Widget.set_size(self, w, h)
        if ((w, h) != (prev_w, prev_h)):
            self.__cache.clear()
            self.emit_event(self.EVENT_RESIZED)


    def add(self, child, name = ""):
        """
        Adds a child widget. A unique name must be given when using arrangement
        definitions in XML format.
        
        @param child: child widget
        @param name: name string
        """
        
        if (name):
            self.__names[name] = child
        Widget.add(self, child)

        
    def place(self, child, x1, y1, x2, y2):
        """
        Changes the placement of the given child widget.
        
        @param child: child widget
        @param x1: x-coordinate of top-left corner
        @param y1: y-coordinate of top-left corner
        @param x2: x-coordinate of bottom-right corner
        @param y2: y-coordinate of botton-right corner
        """
    
        self.__constraints[child] = (x1, y1, x2, y2)
        
        if (child in self.__cache):
            del self.__cache[child]


    def set_xml(self, xml):
        """
        Loads an arrangement from an XML arrangement definition.
        
        @param xml: XML string containing the arrangement
        """
    
        dom = MiniXML(xml).get_dom()
        self.__parse_node(dom, [], [])

        
    def __parse_node(self, node, required_visibles, required_invisibles):
    
        name = node.get_name()
        if (name == "if-visible"):
            child = self.__names[node.get_attr("name")]
            required_visibles.append(child)
        elif (name == "if-invisible"):
            child = self.__names[node.get_attr("name")]
            required_invisibles.append(child)
        elif (name == "widget"):
            child = self.__names[node.get_attr("name")]
            x1 = self.__parse_value(node.get_attr("x1"))
            y1 = self.__parse_value(node.get_attr("y1"))
            x2 = self.__parse_value(node.get_attr("x2"))
            y2 = self.__parse_value(node.get_attr("y2"))
            
            if (self.__check_visibles(required_visibles, required_invisibles)):
                self.place(child, x1, y1, x2, y2)
        #end if
        
        for c in node.get_children():
            self.__parse_node(c, required_visibles[:], required_invisibles[:])
        #end for


    def __parse_value(self, v):
    
        if (v[-1] == "%"):
            return self.pct(int(v[:-1]))
        else:
            return self.px(int(v))


    def __check_visibles(self, required_visibles, required_invisibles):
    
        for v in required_visibles:
            if (not v.is_visible()):
                return False
        #end for
        
        for v in required_invisibles:
            if (v.is_visible()):
                return False
        #end for
        
        return True
        

    def render_this(self):

        for child in self.get_children():
            x1, y1, x2, y2 = self.__resolve_child(child)
            child.set_geometry(x1, y1, x2 - x1, y2 - y1)
        #end for

