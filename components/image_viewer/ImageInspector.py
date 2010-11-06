from com import FileInspector, msgs

import os
import time


class ImageInspector(FileInspector):
    """
    File inspector for image metadata.
    """

    def __init__(self):
    
        FileInspector.__init__(self)
    

    def get_mime_types(self):
    
        return ["image/*"]
        
        
    def inspect(self, entry):   
        
        path = entry["File.Path"]
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        
        ctime = os.path.getctime(path)
        t = time.localtime(ctime)
        
        entry["File.Type"] = "image"
        entry["Image.Title"] = os.path.splitext(basename)[0].replace("_", " ")
        entry["File.Folder"] = os.path.basename(dirname)
        entry["Image.Month"] = t.tm_mon
        entry["Image.Year"] = t.tm_year

