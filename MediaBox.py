#! /usr/bin/env python

from mediabox import values
from com import Container
from utils import logging
import os
import sys
import getopt

try:
    import dbus
    import dbus.glib
except:
    dbus = None
    

_LOG_LEVELS = [logging.OFF, logging.ERROR, logging.WARNING,
               logging.INFO, logging.DEBUG, logging.PROFILE]


try:
    opts, args = getopt.getopt(sys.argv[1:],
                               "vqh", ["help"])
except:
    opts = [("--help", None)]
    args = []


log_count = 1
for o, v in opts:
    if (o == "-v"):
        log_count += 1
    elif (o == "-q"):
        log_count = 0
    elif (o == "-h" or o == "--help"):
        print "Usage: %s [-v|-q] [-h|--help] [uri]" \
              % os.path.basename(sys.argv[0])
        print ""
        print "  -h, --help            Show this help."
        print "  -q                    Turn off logging."
        print "  -v                    Increase logging verbosity. Use up to three -v."
        sys.exit(0)
#end for

if (args):
    values.uri = args[0]
else:
    values.uri = ""

logging.set_level(_LOG_LEVELS[min(5, log_count)])


# check if MediaBox is running already, and load the file given on the command
# line into the running instance in this case. thanks to thp for this trick!
if (dbus):
    bus = dbus.SessionBus()
    if (bus.name_has_owner("de.pycage.mediabox")):
        try:
            proxy = bus.get_object("de.pycage.mediabox",
                                   "/de/pycage/mediabox/control")
        except:
            proxy = None
    else:
        proxy = None
                               
    if (proxy and values.uri):
        proxy.load(values.uri, "")
        sys.exit(0)
#end if
                               
comp_dir = os.path.join(values.MEDIABOX_DIR, "components")
plugins = [ os.path.join(comp_dir, d) for d in os.listdir(comp_dir) 
            if not d.startswith(".") ]

logging.debug("initializing application")
container = Container(plugins)

logging.debug("running application")
import gobject; gobject.threads_init()
import gtk
gtk.main()

