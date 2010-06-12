"""
Module for dealing with MIME types. MIME type definitions are read from the
C{mimetypes.mapping} file.
@since: 0.96
"""

import os


_MIMETYPES_FILE = os.path.join(os.path.dirname(__file__), "..", "mimetypes.mapping")

_EXT_TO_MIMETYPE = {}
_MIMETYPE_TO_EXT = {}
_MIMETYPE_TO_NAME = {}
_VIDEO_TYPES = []
_AUDIO_TYPES = []
_IMAGE_TYPES = []


def _load_mimetypes(path):

    try:
        fd = open(path, "r")
        lines = fd.readlines()
        fd.close()
    except:
        return
        
    cnt = 0
    for line in lines:
        cnt += 1
        if (not line.strip() or line.startswith("#")):
            continue
            
        parts = line.split()
        try:
            mimetype = parts[0]
            exts = parts[1]
            name = parts[2]
            mediatype = parts[3]
        except:
            continue
            
        _MIMETYPE_TO_NAME[mimetype] = name
        if (exts != "-"):
            es = exts.split(",")
            for ext in es:
                _EXT_TO_MIMETYPE[ext] = mimetype
            _MIMETYPE_TO_EXT[mimetype] = es[0]
        #end if
        
        if (mediatype == "A"):   _AUDIO_TYPES.append(mimetype)
        elif (mediatype == "I"): _IMAGE_TYPES.append(mimetype)
        elif (mediatype == "V"): _VIDEO_TYPES.append(mimetype)
    #end for



def ext_to_mimetype(ext):
    """
    Looks up the MIME type for the given file extension.
    @since: 0.96
    
    @param ext: file extension (including leading '.')
    @return: MIME type
    """

    return _EXT_TO_MIMETYPE.get(ext, "application/x-unknown")


def mimetype_to_ext(mimetype):
    """
    Returns an extension for the given MIME type.
    @since: 2010.06.12
    
    @param mimetype: MIME type
    @return: file extension (including leading '.')
    """
    
    return _MIMETYPE_TO_EXT.get(mimetype, "")


def mimetype_to_name(mimetype):
    """
    Returns the name of the filetype for the given MIME type.
    @since: 0.96
    
    @param mimetype: MIME type
    @return: name of filetype
    """

    return _MIMETYPE_TO_NAME.get(mimetype, "Unknown")


def get_audio_types():
    """
    Returns a list of all audio MIME types.
    @since: 0.96
    
    @return: list of audio MIME types
    """
    
    return _AUDIO_TYPES


def get_image_types():
    """
    Returns a list of all image MIME types.
    @since: 0.96
    
    @return: list of image MIME types
    """
    
    return _IMAGE_TYPES


def get_video_types():
    """
    Returns a list of all video MIME types.
    @since: 0.96
    
    @return: list of video MIME types
    """

    return _VIDEO_TYPES

    
_load_mimetypes(_MIMETYPES_FILE)
