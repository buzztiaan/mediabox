"""
Lightweight logger
"""

import time


OFF = 0         # log nothing
ERROR = 1       # log errors
WARNING = 2     # log errors and warnings
INFO = 3        # log errors, warnings, and info
DEBUG = 4       # log errors, warnings, info, and debugging


_level = ERROR


def set_level(level):
    global _level
    
    _level = level


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

