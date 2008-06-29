_EXT_TABLE = {
    ".gif":         "image/gif",
    ".jpg":         "image/jpeg",
    ".jpeg":        "image/jpeg",
    ".png":         "image/png",
    
    ".flac":        "audio/x-flac",
    ".mp2":         "audio/mp2",
    ".mp3":         "audio/mpeg",
    ".ogg":         "audio/x-vorbis+ogg",

    ".avi":         "video/x-msvideo",
    ".flv":         "video/x-flash-video",
    ".mpg":         "video/mpeg",
}


def lookup_ext(ext):

    return _EXT_TABLE.get(ext, "application/x-unknown")
