from com import Component, FileInspector, msgs
from utils import mimetypes
from utils import logging
from mediabox import values
import os


_INDEX_FILE = os.path.join(values.USER_DIR, "files.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0006


class FileIndex(Component):
    """
    Component for creating and querying a file index. The index is serialized
    to disk.
    """

    def __init__(self):
    
        # table: path -> table: key -> value
        self.__index = {}
        
        # whether the index has unsaved changes
        self.__is_dirty = False
        
        # table: mimetype -> [inspectors]
        self.__inspectors = {}
        
        
        Component.__init__(self)
        self.__load_index()


    def __load_index(self):

        try:
            import cPickle
            fd = open(_INDEX_FILE, "rb")
        except:
            return
            
        try:
            magic, data = cPickle.load(fd)
        except:
            logging.error(logging.stacktrace())
            return
        finally:
            fd.close()

        # ignore the file if it isn't compatible
        if (magic == _MAGIC):
            self.__index = data
            self.__is_dirty = False


    def __save_index(self):
    
        self.__is_dirty = False
        try:
            import cPickle
            fd = open(_INDEX_FILE, "wb")
        except:
            return
            
        try:
            cPickle.dump((_MAGIC, self.__index), fd, 2)
        except:
            pass
        finally:
            fd.close()

        
    def __guess_mimetype(self, path):
        
        ext = os.path.splitext(path)[1]
        return mimetypes.ext_to_mimetype(ext)


    def __inspect(self, path):
    
        entry = self.__index[path]
    
        mimetype = entry["File.Format"]
        insp = self.__inspectors.get(mimetype)

        if (not insp):
            m1, m2 = mimetype.split("/")
            insp = self.__inspectors.get(m1 + "/*")

        if (not insp):
            return
            
        else:
            insp.inspect(entry)


    def discover(self, path, mtime):
    
        # case 1: file is new
        if (not path in self.__index):
            entry = {"File.Path": path,
                     "File.Modified": mtime,
                     "File.Format": self.__guess_mimetype(path)}
            self.__index[path] = entry
            self.__inspect(path)
            self.__is_dirty = True
            
        # case 2: file is updated
        elif (mtime > self.__index[path]["File.Modified"]):
            entry = {"File.Path": path,
                     "File.Modified": mtime,
                     "File.Format": self.__guess_mimetype(path)}
            self.__index[path] = entry
            self.__inspect(path)
            self.__is_dirty = True

        # case 3: file already in index
        else:
            # do nothing
            pass


    def remove(self, path):
    
        del self.__index[path]
        self.__is_dirty = True


    def query(self, qs, *query_args):
    
        if (self.__is_dirty):
            self.__save_index()
    
        # normalize argument strings (replace unsafe chars)
        qas = []
        for q in query_args:
            if (type(q) == type("")):
                qas.append(q.replace("'", "\\'"))
            else:
                qas.append(q)
        #end for
        qas = tuple(qas)
        if (qas):
            qs = qs % qas

        print "QUERY:", qs

        wrapped_qs = [qs]
        filter_props = self.__parse_filter(wrapped_qs)
        items = self.__parse_condition(wrapped_qs, set(self.__index.keys()))
        
        out = set()
        for item in items:
            values = ( self.__index[item].get(key, "") for key in filter_props )
            out.add(tuple(values))
        #end for
        
        if (len(out) < 100):
            print "RESULT:", out
        else:
            print "RESULT: ..."
            
        return out
        
        
    def __parse_filter(self, w_qs):
    
        qs = w_qs[0].strip()
        #print "parse filter:", qs
        idx = qs.find(" of ")
        part1 = qs[:idx]
        part2 = qs[idx + 4:]
        
        props = [ p.strip() for p in part1.split(",") if p.strip() ]
        w_qs[0] = part2

        return props
        
        
    def __parse_condition(self, w_qs, set0):
    
        qs = w_qs[0].strip() + " "
        #print "parse condition:", qs
        idx = qs.find(" ")
        operator = qs[:idx]
        
        if (operator == "all"):
            return set0
        
        elif (operator == "and"):
            w_qs[0] = qs[idx:].strip()
            set1 = self.__parse_condition(w_qs, set0)
            set2 = self.__parse_condition(w_qs, set1)
        
            return set2
            
        elif (operator == "or"):
            w_qs[0] = qs[idx:].strip()
            set1 = self.__parse_condition(w_qs, set0)
            set2 = self.__parse_condition(w_qs, set0)
            
            return set1.union(set2)
            
        else:
            set1 = self.__parse_expr(w_qs, set0)
            
            return set1


    def __parse_expr(self, w_qs, set0):
    
        qs = w_qs[0].strip()
        #print "parse expr:", qs
        idx = qs.find("=")
        key = qs[:idx]
        
        value = ""
        state = 0
        pos = idx + 1
        is_string = False
        for c in qs[idx + 1:]:
            pos += 1
            if (state == 0):
                if (c == "'"):
                    is_string = True
                    state = 1
                elif (c == " "):
                    break
                else:
                    value += c

            elif (state == 1):
                if (c == "'"):
                    break
                elif (c == "\\"):
                    state = 2
                else:
                    value += c
                    
            elif (state == 2):
                value += c
                state = 1
        #end for

        if (not is_string):
            value = int(value)

        w_qs[0] = qs[pos:]
        return set([ p for p in set0 if self.__index[p].get(key) == value ])


    def handle_COM_EV_COMPONENT_LOADED(self, comp):
    
        # watch out for FileInspectors
        if (isinstance(comp, FileInspector)):
            for mt in comp.get_mime_types():
                #print "INSPECTOR FOR", mt, comp
                self.__inspectors[mt] = comp
            #end for
        #end if
        
        
    def handle_COM_EV_APP_SHUTDOWN(self):
    
        if (self.__is_dirty):
            self.__save_index()


    def handle_FILEINDEX_SVC_DISCOVER(self, path, mtime):
    
        self.discover(path, mtime)
        return 0
        
        
    def handle_FILEINDEX_SVC_REMOVE(self, path):
    
        self.remove(path)
        return 0
        
        
    def handle_FILEINDEX_SVC_QUERY(self, query, *query_args):
    
        return self.query(query, *query_args)


    def handle_FILEINDEX_SVC_CLEAR(self):

        self.__index = {}
        self.__save_index()
        
        return 0


if (__name__ == "__main__"):
    import sys
   
    fi = FileIndex()
    cwd = sys.argv[1]
    
    for f in os.listdir(cwd):
        path = os.path.join(cwd, f)
        if (not os.path.isfile(path)): continue
        mtime = int(os.path.getmtime(path))
        fi.discover(path, mtime)
        
    print fi.query("File.Format, File.Path of or File.Format='video/mp4' File.Format='audio/mpeg'")

