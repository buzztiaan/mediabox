"""
Lightweight logging module with formatted output. Logs are written to C{stdout}.
"""

import sys
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
PROFILE = 5
"""log level: log errors, warnings, info, debugging, and profiling"""


_level = ERROR


def set_level(level):
    """
    Sets the log level. This is a global setting. The default log level
    is C{ERROR}.
    @since: 0.96
    
    @param level: log level
    """
    global _level
    
    _level = level
    
    
def get_level():
    """
    Returns the current log level.
    @since: 0.96.4
    
    @return: log level
    """
    
    return _level
    

def is_level(level):
    """
    Returns whether messages of the given level are logged.
    @since: 0.96
    
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
    sys.stdout.flush()


def error(msg, *args):
    """
    @since: 0.96
    """

    if (_level < ERROR): return
    if (args):
        msg = msg % args

    _log("ERROR  ", msg)


def warning(msg, *args):
    """
    @since: 0.96
    """

    if (_level < WARNING): return
    if (args):
        msg = msg % args

    _log("WARNING", msg)


def info(msg, *args):
    """
    @since: 0.96
    """

    if (_level < INFO): return
    if (args):
        msg = msg % args

    _log("INFO   ", msg)


def debug(msg, *args):
    """
    @since: 0.96
    """

    if (_level < DEBUG): return
    if (args):
        msg = msg % args

    _log("DEBUG  ", msg)


def profile(stopwatch, msg, *args):
    """
    @since: 2010.10.09
    """
    
    if (_level < PROFILE): return
    if (args):
        msg = msg % args
    _log("PROFILE (%0.4fs)" % (time.time() - stopwatch), msg)


def stacktrace():
    """
    Returns the current stack trace.
    @since: 0.96
    
    @return: stack trace
    """

    return traceback.format_exc()


def stopwatch():
    """
    Returns a stopwatch for profiling.
    @since: 2010.10.19
    
    @return: a stopwatch object
    """
    
    return time.time()

