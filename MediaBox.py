#! /usr/bin/env python

from com import Container
from mediabox import values
from utils import logging
import os
import sys
import getopt


_LOG_LEVELS = [logging.OFF, logging.ERROR, logging.WARNING,
               logging.INFO, logging.DEBUG]


try:
    opts, args = getopt.getopt(sys.argv[1:],
                               "vqh", ["plugin-dir=", "blacklist-plugins=", "help"])
except:
    opts = [("--help", None)]

log_count = 1
plugin_dirs = [os.path.join(values.MEDIABOX_DIR, "components")]
blacklist = []
for o, v in opts:
    if (o == "-v"):
        log_count += 1
    elif (o == "-q"):
        log_count = 0
    elif (o == "--plugin-dir"):
        plugin_dirs.append(os.path.abspath(v))
    elif (o == "--blacklist-plugins"):
        blacklist = v.split(",")
    elif (o == "-h" or o == "--help"):
        print "Usage: %s [-v|-q] [--blacklist-plugins=plugin1,plugin2,...] [-h|--help]" \
              % os.path.basename(sys.argv[0])
        print ""
        print "  -h, --help            Show this help."
        print "  -q                    Turn off logging."
        print "  -v                    Increase logging verbosity. Use up to three -v."
        print "  --blacklist-plugins   Don't load the given plugins. Separate plugin"
        print "                        names by commas."
        print "  --plugin-dir          Load additional plugins from the given directory."
        sys.exit(0)
#end for

logging.set_level(_LOG_LEVELS[min(4, log_count)])


logging.debug("initializing application")
container = Container(plugin_dirs, blacklist)

logging.debug("running application")
import gtk
gtk.main()

