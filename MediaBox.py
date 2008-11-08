#! /usr/bin/env python

from com import Container
from utils import logging
import os
import sys

# bad hack!
# work around broken D-Bus bindings on OS 2006; this breaks urllib2 for us,
# but we don't use it anyway
def f(*args): raise RuntimeError("Ignore me...")
import urllib2
urllib2.AbstractHTTPHandler.do_open = f

# TODO: use getopt
try:
    arg = sys.argv[1]
except:
    arg = ""
if (arg == "-vvv"):
    logging.set_level(logging.DEBUG)
elif (arg == "-vv"):
    logging.set_level(logging.INFO)
elif (arg == "-v"):
    logging.set_level(logging.WARNING)
elif (arg == "-q"):
    logging.set_level(logging.OFF)
else:
    logging.set_level(logging.ERROR)


logging.debug("initializing application")
container = Container(os.path.join(os.path.dirname(__file__), "components"))

logging.debug("running application")
import gtk
gtk.main()

