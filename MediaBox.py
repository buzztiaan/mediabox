#! /usr/bin/env python

from utils import logging
logging.set_level(logging.DEBUG)


logging.debug("initializing application")

from mediabox.App import App



app = App()
logging.debug("running application")
app.run()

