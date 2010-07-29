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
        entry["Audio.Artist"] = tags.get("ARTIST") or "unspecified"
        entry["Audio.Album"] = tags.get("ALBUM") or entry["Audio.Artist"]
        entry["Audio.Genre"] = tags.get("GENRE") or "unspecified"
        try:
            trackno = tags.get("TRACKNUMBER")
            trackno = trackno.split("/")[0]
            trackno = int(trackno)
        except:
            trackno = 0
        entry["Audio.Tracknumber"] = trackno

