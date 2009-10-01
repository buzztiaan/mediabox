def MEDIASCANNER_ACT_SCAN(mediaroots, rebuild_index): pass
"""
Instructs the media scanner to scan for media.

@param mediaroots: list of media root folders
@param rebuild_index: whether to rebuild the index
"""

def MEDIASCANNER_SVC_GET_MEDIA(mimetypes): pass
"""
Returns the media objects for the given MIME types. The return value is
a tuple of three lists: all items, the recently added items, and the recently
removed items.

@param mimetypes: list of MIME type strings
@return: all items
@return: recently added items
@return: recently removed items
"""

def MEDIASCANNER_SVC_LOOKUP_THUMBNAIL(f): pass
"""
Looks up a thumbnail for the given file.

@param f: file object
@return: path of thumbnail file and whether the thumbnail is final
"""

def MEDIASCANNER_SVC_LOAD_THUMBNAIL(f, cb, *args): pass
"""
Loads a thumbnail for the given file asynchronously, invoking the given callback
when a thumbnail has been found or was created.

@param f: file object
@param cb: callback handler
@param args: variable list of arguments to the callback handler
"""

def MEDIASCANNER_SVC_COPY_THUMBNAIL(f1, f2): pass
"""
Copies a thumbnail from file to another, so that both files have the same
thumbnail preview.

@param f1: source file object
@param f2: destination file object
"""

def MEDIASCANNER_SVC_GET_THUMBNAIL(f): pass
"""
@deprecated: do not use; it will be removed
"""

def MEDIASCANNER_SVC_SET_THUMBNAIL(f, pixbuf): pass
"""
@deprecated: do not use; it will be removed
"""

def MEDIASCANNER_EV_SCANNING_STARTED(): pass
"""
Gets emitted when the media scanner starts scanning.
"""

def MEDIASCANNER_EV_SCANNING_FINISHED(): pass
"""
Gets emitted when the media scanner finished scanning.
"""

def MEDIASCANNER_EV_SCANNING_PROGRESS(name): pass
"""
Gets emitted when the media scanner progresses in scanning.

@param name: name of the currently scanned media root
"""

