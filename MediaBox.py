#! /usr/bin/env python

"""
171     if have_dbus:
172         # Try to find an already-running instance of gPodder
173         session_bus = dbus.SessionBus()
174
175         # Obtain a reference to an existing instance; don't call get_object if
176         # such an instance doesn't exist as it *will* create a new instance
177         if session_bus.name_has_owner(gpodder.dbus_bus_name):
178             try:
179                 remote_object = session_bus.get_object(gpodder.dbus_bus_name, \
180                         gpodder.dbus_gui_object_path)
181             except dbus.exceptions.DBusException:
182                 remote_object = None
183         else:
184             remote_object = None
185     else:
186         # No D-Bus available :/
187         remote_object = None
188
189     if remote_object is not None:
190         # An instance of GUI is already running
191         print >>sys.stderr, 'Existing instance running - activating via D-Bus.'
192         remote_object.show_gui_window(dbus_interface=gpodder.dbus_interface)
193         if options.subscribe:
194             remote_object.subscribe_to_url(options.subscribe)
"""

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

logging.set_level(_LOG_LEVELS[min(4, log_count)])


comp_dir = os.path.join(values.MEDIABOX_DIR, "components")
plugins = [ os.path.join(comp_dir, d) for d in os.listdir(comp_dir) 
            if not d.startswith(".") ]
#plugins += args

logging.debug("initializing application")
container = Container(plugins)

logging.debug("running application")
import gobject; gobject.threads_init()
import gtk
gtk.main()

