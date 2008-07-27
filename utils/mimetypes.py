import os


_EXT_TABLE = {
    ".gif":         "image/gif",
    ".jpg":         "image/jpeg",
    ".jpeg":        "image/jpeg",
    ".png":         "image/png",
    
    ".aac":         "audio/mp4",
    ".flac":        "audio/x-flac",
    ".mp2":         "audio/mp2",
    ".mp3":         "audio/mpeg",
    ".m4a":         "audio/mp4",
    ".ogg":         "audio/x-vorbis+ogg",
    ".ra":          "application/vnd.rn-realmedia",
    ".ram":         "application/vnd.rn-realmedia",
    ".wav":         "audio/x-wav",
    ".wma":         "audio/x-ms-wma",

    ".asf":         "video/x-ms-asf",
    ".avi":         "video/x-msvideo",
    ".flv":         "video/x-flash-video",
    ".m4v":         "video/mp4",
    ".mov":         "video/quicktime",
    ".mpg":         "video/mpeg",
    ".qt":          "video/quicktime",
    ".rm":          "application/vnd.rn-realmedia",
    ".rmvb":        "application/vnd.rn-realmedia",
    ".wmv":         "video/x-ms-wmv",
}

_MIMETYPES_FILE = os.path.join(os.path.dirname(__file__), "..", "mimetypes.mapping")

_EXT_TO_MIMETYPE = {}
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
            for ext in exts.split(","):
                _EXT_TO_MIMETYPE[ext] = mimetype
        #end if
        
        if (mediatype == "A"):   _AUDIO_TYPES.append(name)
        elif (mediatype == "I"): _IMAGE_TYPES.append(name)
        elif (mediatype == "V"): _VIDEO_TYPES.append(name)
    #end for



def lookup_ext(ext):

    return _EXT_TO_MIMETYPE.get(ext, "application/x-unknown")


def mimetype_to_name(mimetype):

    return _MIMETYPE_TO_NAME.get(mimetype, "Unknown")


def get_audio_types():
    
    return _AUDIO_TYPES


def get_image_types():
    
    return _IMAGE_TYPES


def get_video_types():
    
    return _VIDEO_TYPES

    
_load_mimetypes(_MIMETYPES_FILE)
