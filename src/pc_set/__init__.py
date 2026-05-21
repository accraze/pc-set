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
    >>> print(s.common_name())
    'Major Triad'
"""

__version__ = "0.1.0"
__author__ = "Andy Craze"

from .pcset import PCSet
from .common_sets import (
    get_common_set,
    get_set_by_name,
    search_by_name,
    get_z_partners,
    is_z_related,
    get_all_z_pairs,
    get_by_cardinality,
)
from .search import analyze, compare_sets, find_similar_to, find_z_pairs_by_cardinality

__all__ = [
    # Core class
    "PCSet",
    
    # Common sets lookup
    "get_common_set",
    "get_set_by_name",
    "search_by_name",
    "get_z_partners",
    "is_z_related",
    "get_all_z_pairs",
    "get_by_cardinality",
    
    # Analysis tools
    "analyze",
    "compare_sets",
    "find_similar_to",
    "find_z_pairs_by_cardinality",
]
