def DOWNLOADER_SVC_GET(url, destination): pass
"""
Schedules the given URL for downloading to the given destination.
Returns a download ID token for later reference.
@since: 2010.06.08

@param url: download URL
@param destination: destination path in the local filesystem
@return: download ID
"""

def DOWNLOADER_SVC_GET_RECURSIVE(f, destination): pass
"""
Schedules the given file object for downloading to the given destination.
Returns a download ID token for later reference.
If the file object is a directory, the destination is treated as a directory,
too, and the directory's contents are downloaded recursively.

@param f: file object
@param destination: destination path in the local filesystem
@return: download ID
"""

def DOWNLOADER_ACT_ABORT(download_id): pass
"""
Causes the downloader to abort the download identified by the given ID token.
@since: 2010.06.08

@param download_id: download ID
"""

def DOWNLOADER_EV_STARTED(download_id, url, destination): pass
"""
Gets emitted when a download starts.
@since: 2010.06.08

@param download_id: download ID
@param url: download URL
@param destination: destination path in the local file system
"""

def DOWNLOADER_EV_PROGRESS(download_id, name, amount, total): pass
"""
Gets emitted during a download to report the progress for the download
identified by the ID token.

@param download_id: download ID
@param name: name of download
@param amount: amount of progress in bytes
@param total: total amount in bytes (or 0 if unknown)
"""

def DOWNLOADER_EV_FINISHED(download_id): pass
"""
Gets emitted when the download identified by the ID token has finished.
This is not implemented as a private callback to enable external monitoring
of active downloads.
@since: 2010.06.08
"""

def DOWNLOADER_EV_ABORTED(download_id): pass
"""
Gets emitted when the download identified by the ID token gets aborted.
@since: 2010.06.11
"""
