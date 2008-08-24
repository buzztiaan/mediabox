"""
Module with useful memory card functions for maemo.

@copyright: 2007 - 2008
@author: Martin Grimme  <martin.grimme@lintegra.de>

@license: This module is licensed under the terms of the GNU LGPL.
"""


import commands
import os


CARD_1 = "/media/mmc1"
CARD_2 = "/media/mmc2"

_LABEL_FILES = { CARD_1: "/tmp/.mmc-volume-label",
                 CARD_2: "/tmp/.internal-mmc-volume-label" }
_DEFAULT_LABELS = { CARD_1: "Memory card",
                    CARD_2: "Internal memory card" }


def exists(card):
    """
    Returns whether the given card exists, i.e. mounted.
    
    @param card: card (one of C{CARD_1} or C{CARD_2})
    @return: whether the card exists
    """
    
    # it can be so easy...
    mounts = open("/proc/mounts").read()
    return (card in mounts)


def get_label(card):
    """
    Returns the label of the given card.
    
    @param card: card (one of C{CARD_1} or C{CARD_2})
    @return: label string
    """

    label = ""
    filename = _LABEL_FILES.get(card)
    if (filename):
        try:
            label = open(filename).read().strip()
        except:
            pass

    return label or _DEFAULT_LABELS.get(card) or os.path.basename(card)


def get_path(card):
    """
    Returns the path of the mount point of the given card.
    
    @param card: card (one of C{CARD_1} or C{CARD_2})
    @return: path of mount point
    """

    return card


def get_device(card):
    """
    Returns the device node of the given card.
    Returns C{/dev/null} if the card does not exist.

    @param card: card (one of C{CARD_1} or C{CARD_2})
    @return: path of device node
    """

    mounts = open("/proc/mounts").readlines()
    for line in mounts:
        if (card in line):
            device = line.split()[0]
            return device
    #end for

    return "/dev/null"
