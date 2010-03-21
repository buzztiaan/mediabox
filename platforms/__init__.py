from utils import logging
import os


# available platforms
MAEMO4 = ""
MAEMO5 = ""
MER = ""
COMPUTER = ""
HTPC = ""


def _check_maemo4():

    v = os.system("cat /etc/osso_software_version | grep DIABLO >/dev/null 2>&1")
    #v = os.system("cat /etc/apt/sources.list.d/hildon-application-manager.list " \
    #              "| egrep 'gregale|bora|chinook|diablo' >/dev/null")
    return (v == 0)

    
def _check_maemo5():

    v = os.system("cat /etc/apt/sources.list " \
                  "    /etc/apt/sources.list.d/hildon-application-manager.list " \
                  "| egrep fremantle >/dev/null")
    return (v == 0)


def _check_mer():

    v = os.system("dpkg -l | grep maemo-launcher | grep mer >/dev/null")
    return (v == 0)
    
    
def _check_htpc():

    v = os.system("lsmod | grep appleir >/dev/null")
    return (v == 0)


def _check_computer():

    return True
    

if _check_maemo5():
    from maemo5 import *
    MAEMO5 = "maemo5"
    logging.info("using MAEMO5 target")

elif _check_maemo4():
    from maemo4 import *
    MAEMO4 = "maemo4"
    logging.info("using MAEMO4 target")

elif _check_mer():
    from mer import *
    MER = "mer"
    logging.info("using MER target")

elif _check_htpc():
    from htpc import *
    HTPC = "htpc"
    logging.info("using HTPC target")

elif _check_computer():
    from computer import *
    COMPUTER = "computer"
    logging.info("using COMPUTER target")

