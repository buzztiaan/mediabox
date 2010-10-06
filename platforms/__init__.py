from utils import logging
import os


# available platforms
MAEMO4 = ""
MAEMO5 = ""
MER = ""
MEEGO_NETBOOK = ""
MEEGO_WETAB = ""
COMPUTER = ""
HTPC = ""


def _check_maemo4():

    try:
        import hildon
    except:
        return False
    try:
        # hildon.Window with set_app_menu is not Maemo4
        hildon.Window.set_app_menu
    except:
        return True

    return False

    
def _check_maemo5():

    try:
        import hildon
        hildon.Window.set_app_menu
    except:
        return False
    else:
        return True


def _check_mer():

    v = os.system("dpkg -l 2>&1 | grep maemo-launcher | grep mer >/dev/null")
    return (v == 0)
    
    
def _check_meego_netbook():

    v = os.system("cat /etc/meego-release 2>&1 | grep netbook >/dev/null")
    return (v == 0)


def _check_meego_wetab():

    v = os.system("rpm -qa 2>&1 | grep pega-driver-wetab >/dev/null")
    return (v == 0)
    
    
def _check_htpc():

    v = os.system("lsmod 2>&1 | grep appleir >/dev/null")
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

elif _check_meego_netbook():
    from meego_netbook import *
    MEEGO_NETBOOK = "meego_netbook"
    logging.info("using MEEGO_NETBOOK target")

elif _check_meego_wetab():
    from meego_wetab import *
    MEEGO_WETAB = "meego_netbook"
    logging.info("using MEEGO_WETAB target")

elif _check_htpc():
    from htpc import *
    HTPC = "htpc"
    logging.info("using HTPC target")

elif _check_computer():
    from computer import *
    COMPUTER = "computer"
    logging.info("using COMPUTER target")

