import os
import time

NAME = "MediaBox"
OSSO_NAME = "de.pycage.maemo.mediabox"
VERSION = "2010.06.26"

AUTHORS = ["Martin Grimme  <martin.grimme@lintegra.de>"]
COPYRIGHT = "\xc2\xa9 2007 - 2010 Martin Grimme"

USER_DIR = os.path.expanduser("~/.mediabox")
MEDIABOX_DIR = os.path.join(os.path.dirname(__file__), "..")

START_TIME = time.time()
