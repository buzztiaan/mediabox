#! /usr/bin/env python

from mediabox import values
from com import Container
from utils import logging
import os
import sys
import getopt


_LOG_LEVELS = [logging.OFF, logging.ERROR, logging.WARNING,
               logging.INFO, logging.DEBUG]


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
        print "Usage: %s [-v|-q] [-h|--help] [plugin ...]" \
              % os.path.basename(sys.argv[0])
        print ""
        print "  -h, --help            Show this help."
        print "  -q                    Turn off logging."
        print "  -v                    Increase logging verbosity. Use up to three -v."
        sys.exit(0)
#end for

logging.set_level(_LOG_LEVELS[min(4, log_count)])


comp_dir = os.path.join(values.MEDIABOX_DIR, "components")
plugins = [ os.path.join(comp_dir, d) for d in os.listdir(comp_dir) 
            if not d.startswith(".") ]
plugins += args


#import gtk
#win = gtk.Window(gtk.WINDOW_TOPLEVEL)
#win.set_title("MediaBox")
#lbl = gtk.Button("Loading Components")
#lbl.show()
#win.add(lbl)
#win.show()
#while (gtk.gdk.events_pending()):
#    gtk.main_iteration(False)


logging.debug("initializing application")
container = Container(plugins)
#win.destroy()

logging.debug("running application")
import gobject; gobject.threads_init()
import gtk
gtk.main()

