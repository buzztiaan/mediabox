#! /usr/bin/env python

from utils import logging
logging.set_level(logging.INFO)


logging.debug("initializing application")

from mediabox.App import App



app = App()
logging.debug("running application")
app.run()

