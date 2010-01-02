from com import FileInspector, msgs
from mediabox import tagreader

import os


class AudioInspector(FileInspector):
    """
    File inspector for audio metadata.
    """

    def __init__(self):
    
        FileInspector.__init__(self)
    

    def get_mime_types(self):
    
        return ["application/ogg", "audio/*"]
        
        
    def inspect(self, entry):   
        
        path = entry["File.Path"]
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        
        f = self.call_service(msgs.CORE_SVC_GET_FILE, path)
        tags = tagreader.get_tags(f)
        
        entry["File.Type"] = "audio"
        entry["File.Folder"] = os.path.basename(dirname)
        entry["Audio.Title"] = tags.get("TITLE") or os.path.basename(path)
        entry["Audio.Artist"] = tags.get("ARTIST") or "unknown"
        entry["Audio.Album"] = tags.get("ALBUM") or entry["Audio.Artist"]
        entry["Audio.Genre"] = tags.get("GENRE") or "unknown"
        #print "ENTRY", entry
