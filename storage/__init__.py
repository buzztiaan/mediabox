"""
Storage Device
==============

Classes for implementing storage devices for accessing virtual file systems.

Create a subclass derived from L{Device} in order to implement a new virtual
file system.

Do not subclass the L{File} class.
"""

from Device import Device
from File import File

