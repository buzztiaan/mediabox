from com import FileInspector, msgs

import os


class VideoInspector(FileInspector):

    def __init__(self):
    
        FileInspector.__init__(self)
    

    def get_mime_types(self):
    
        return ["video/*"]
        
        
    def inspect(self, entry):   
        
        path = entry["File.Path"]
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        
        entry["File.Type"] = "video"
        entry["Video.Title"] = os.path.splitext(basename)[0].replace("_", " ")
        entry["File.Folder"] = os.path.basename(dirname)
        print "ENTRY", entry

