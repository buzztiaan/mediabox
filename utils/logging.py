"""
Lightweight logging module with formatted output. Logs are written to C{stdout}.
"""

import time
import traceback


OFF = 0
"""log level: log nothing"""
ERROR = 1
"""log level: log errors"""
WARNING = 2
"""log level: log errors and warnings"""
INFO = 3
"""log level: log errors, warnings, and info"""
DEBUG = 4
"""log level: log errors, warnings, info, and debugging"""


_level = ERROR


def set_level(level):
    """
    Sets the log level. This is a global setting. The default log level
    is C{ERROR}.
    
    @param level: log level
    """
    global _level
    
    _level = level
    
    
def get_level():
    """
    Returns the current log level.
    
    @return: log level
    """
    
    return _level
    

def is_level(level):
    """
    Returns whether messages of the given level are logged.
    
    @param level: log level
    @return: whether messages are logged
    """

    return (_level >= level)


def _log(ltype, s):

    now = time.time()
    msecs = (now - int(now)) * 1000
    now = time.strftime("%F %T", time.localtime(now))
    print "%s.%03d - %s ---" % (now, msecs, ltype),
    
    first_line = True
    for line in s.splitlines():
        if (first_line):
            print line
            first_line = False
        else:
            print ">   " + line
    #end for


def error(msg, *args):

    if (_level < ERROR): return
    if (args):
        msg = msg % args

    _log("ERROR  ", msg)


def warning(msg, *args):

    if (_level < WARNING): return
    if (args):
        msg = msg % args

    _log("WARNING", msg)


def info(msg, *args):

    if (_level < INFO): return
    if (args):
        msg = msg % args

    _log("INFO   ", msg)


def debug(msg, *args):

    if (_level < DEBUG): return
    if (args):
        msg = msg % args

    _log("DEBUG  ", msg)


def stacktrace():
    """
    Returns the current stack trace.
    
    @return: stack trace
    """

    return traceback.format_exc()

