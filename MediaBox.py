#! /usr/bin/env python

# bad hack!
# work around broken D-Bus bindings on OS 2006; this breaks urllib2 for us,
# but we don't use it anyway
def f(*args): raise RuntimeError("Ignore me...")
import urllib2
urllib2.AbstractHTTPHandler.do_open = f


from utils import logging
logging.set_level(logging.INFO)


logging.debug("initializing application")


from com import Container
import os
container = Container(os.path.join(os.path.dirname(__file__), "components"))

logging.debug("running application")
import gtk
gtk.main()
#from mediabox.App import App



#app = App()
#logging.debug("running application")
#app.run()

