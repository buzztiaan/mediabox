from com import Component, FileInspector, msgs
from utils import mimetypes
from utils import logging
from mediabox import values

import os
import time


_INDEX_FILE = os.path.join(values.USER_DIR, "files.idx")

# when the index format becomes incompatible, raise the magic number to force
# rejection of old index
_MAGIC = 0xbeef0008


class FileIndex(Component):
    """
    Component for creating and querying a file index. The index is serialized
    to disk.
    """

    def __init__(self):

        # the current ID to be used for the identifying the next entry
        self.__current_id = 0
    
        # table: ID -> entry
        # an entry is a key-value dict
        self.__entries = {}
    
        # indices used for several properties
        self.__indices = {
            "File.Path": {},
            "Audio.Album": {}
        }

        # list of properties that are to be compared case-insensitive
        self.__case_insensitive = [ "Audio.Album",
                                    "Audio.Artist",
                                    "Audio.Title" ]
        
        # whether the index has unsaved changes
        self.__is_dirty = False
        
        # table: mimetype -> [inspectors]
        self.__inspectors = {}
        
        
        Component.__init__(self)
        self.__load_index()


    def __next_id(self):
        """
        Provides the next unique entry ID.
        """
    
        self.__current_id += 1
        return self.__current_id


    def __load_index(self):
        """
        Deserializes the index from file.
        """

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
            self.__current_id, self.__entries, self.__indices = data
            self.__is_dirty = False


    def __save_index(self):
        """
        Serializes the index to file.
        """
    
        self.__is_dirty = False
        try:
            import cPickle
            fd = open(_INDEX_FILE, "wb")
        except:
            return
            
        try:
            data = (self.__current_id, self.__entries, self.__indices)
            cPickle.dump((_MAGIC, data), fd, 2)
        except:
            pass
        finally:
            fd.close()

        
    def __guess_mimetype(self, path):
        """
        Helper method for guessing a file's MIME type based on its extension.
        """
        
        ext = os.path.splitext(path)[1]
        return mimetypes.ext_to_mimetype(ext)


    def __inspect(self, path, entry):
        """
        Invokes MIME type-specific inspectors for inspecting a file.
        """
    
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
        """
        Discovers the given local file, inspects it, and updates the index
        """

        eids = self.__lookup("File.Path", path)

        # case 1: file is new
        if (not eids):
            entry = {"File.Path": path,
                     "File.Modified": mtime,
                     "File.Format": self.__guess_mimetype(path)}
            self.__inspect(path, entry)
            self.__add(entry)
            self.__is_dirty = True
            
        # case 2: file is updated
        elif (mtime > self.__entries[eids[0]]["File.Modified"]):
            entry = {"File.Path": path,
                     "File.Modified": mtime,
                     "File.Format": self.__guess_mimetype(path)}
            self.__inspect(path, entry)
            self.__add(entry)
            self.__is_dirty = True

        # case 3: file already in index
        else:
            # do nothing
            pass


    def remove(self, path):
        """
        Removes an entry from the index.
        """
    
        # look up entry by path
        entry_ids = self.__lookup("File.Path", path)
        for eid in entry_ids:
            entry = self.__entries[eid]
            del self.__entries[eid]
            
            # remove from particular indices
            for k, v in entry:
                idx = self.__indices.get(k)
                if (idx != None):
                    l = self.__indices.get(v, [])
                    l.remove(eid)
                #end if
            #end for
            
        #end for
    
        self.__is_dirty = True


    def __add(self, entry):
        """
        Stores a new entry.
        """
    
        # store the entry itself
        entry_id = self.__next_id()
        self.__entries[entry_id] = entry
    
        # look for properties to be indexed
        for key, value in entry.items():
            # put into property index
            idx = self.__indices.get(key)
            if (idx != None):
                if (key in self.__case_insensitive): value = value.upper()
                if (not value in idx):
                    idx[value] = []
                idx[value].append(entry_id)
            #end if
        #end for


    def __lookup(self, key, value, set0 = None):
        """
        Looks up a key-value pair. Returns the set of matching entry IDs.
        The given set narrows the search space.
        """
    
        if (set0 == None): set0 = set(self.__entries.keys())
    
        entry_ids = set()
        if (key in self.__case_insensitive): value = value.upper()
    
        idx = self.__indices.get(key)
        if (idx != None):
            # indexed lookup
            new_eids = set0.intersection(idx.get(value, []))
            entry_ids = entry_ids.union(new_eids)
        else:
            # non-indexed slow lookup by searching all entries
            for entry_id, entry in self.__entries.items():
                if (not entry_id in set0): continue
                
                entry_value = entry.get(key, "")
                if (key in self.__case_insensitive):
                    entry_value = entry_value.upper()
                if (entry_value == value):
                    entry_ids.add(entry_id)
            #end for
        #end if
        
        return entry_ids


    def query(self, qs, *query_args):
        """
        Parses and performs a given query. The query uses prefix notation to
        avoid brackets. Returns a set of value-tuples.
        """
    
        if (self.__is_dirty):
            self.__save_index()
    
        stopwatch = logging.stopwatch()
    
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

        logging.debug("[fileindex] query: %s", qs)

        wrapped_qs = [qs]
        filter_props = self.__parse_filter(wrapped_qs)
        all_eids = set(self.__entries.keys())
        entry_ids = self.__parse_condition(wrapped_qs, all_eids)
        
        out = set()
        for eid in entry_ids:
            entry = self.__entries[eid]
            values = ( entry.get(key, "") for key in filter_props )
            out.add(tuple(values))
        #end for
        
        if (len(out) < 100):
            logging.debug("[fileindex] result: %d items\n%s", len(out), out)
        else:
            logging.debug("[fileindex] result: %d items", len(out))
        logging.profile(stopwatch, "[fileindex] query: %s (yields %d items)",
                        str(qs), len(out))
            
        return out
        
        
    def __parse_filter(self, w_qs):
        """
        Parses a filtering expression. A filter is a list of properties.
        """
    
        qs = w_qs[0].strip()
        #print "parse filter:", qs
        idx = qs.find(" of ")
        part1 = qs[:idx]
        part2 = qs[idx + 4:]
        
        props = [ p.strip() for p in part1.split(",") if p.strip() ]
        w_qs[0] = part2

        return props
        
        
    def __parse_condition(self, w_qs, set0):
        """
        Parses a query condition. A condition is a complex compound of
        query expressions. Returns a set of matching entry IDs.
        The given set of entry IDs narrows the search space.
        """

        qs = w_qs[0].strip() + " "
        #print "parse condition:", qs
        idx = qs.find(" ")
        operator = qs[:idx]
        
        if (operator == "all"):
            # 'all' evaluates to the set of all entry IDs
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
        """
        Parses a query expression. Returns a set of matching entry IDs.
        The given set of entry IDs narrows the search space.
        """
    
        qs = w_qs[0].strip()
        #print "parse expr:", qs
        idx = qs.find("=")
        key = qs[:idx]
        
        # quick parser for value strings
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

        w_qs[0] = qs[pos:]
        if (not is_string):
            value = int(value)
            return self.__lookup(key, value, set0)
        else:
            return self.__lookup(key, value, set0)


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

        self.__current_id = 0
        self.__entries.clear()
        for idx in self.__indices.values():
            idx.clear()

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

