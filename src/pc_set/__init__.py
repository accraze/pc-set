"""
PC-Set: Pitch Class Set Theory for Python

A library for analyzing and manipulating pitch class sets using musical set theory.
Useful for atonal music analysis, composition, and music theory education.

Basic usage:
    >>> from pc_set import PCSet
    >>> # Create a set from pitch classes (C=0, C#=1, ..., B=11)
    >>> s = PCSet([0, 4, 7])  # Major triad
    >>> print(s.prime_form())
    (0, 3, 7)
    >>> print(s.forte_number())
    3-11
"""

__version__ = "0.1.0"
__author__ = "Andy Craze"

from .pcset import PCSet

__all__ = ["PCSet"]
