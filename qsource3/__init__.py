"""
QSource3 - Python library for controlling quadrupole mass filter RF generator QSource3 by Janascard.

This library provides high-level and low-level interfaces for controlling the QSource3 device.
"""

__version__ = "0.1.1"
__author__ = "Juraj Jasik"
__email__ = "juraj.jasik@gmail.com"

from .qsource3 import QSource3
from .qsource3driver import QSource3Driver
from .massfilter import Quadrupole, interp_fnc

__all__ = [
    "QSource3",
    "QSource3Driver", 
    "Quadrupole",
    "interp_fnc",
]