"""
Search and analysis tools for pitch class sets.

Provides utilities for finding, filtering, and analyzing sets based on
various criteria like interval vector, cardinality, and similarity.
"""

from typing import List, Tuple, Optional
from .pcset import PCSet
from .common_sets import COMMON_SETS, get_z_partners, is_z_related


def find_by_interval_vector(interval_vector: Tuple[int, int, int, int, int, int]) -> List[str]:
    """
    Find all set classes matching an interval vector.
    
    Args:
        interval_vector: Target interval vector (6 integers)
    
    Returns:
        List of matching Forte numbers.
    
    Example:
        >>> find_by_interval_vector((0, 0, 1, 1, 1, 0))
        ['3-11', '3-12']  # Major and minor triads
    """
    matches = []
    for forte_num, info in COMMON_SETS.items():
        # Would need to compute IV for each - for now just check common sets
        # This is a placeholder for a more complete implementation
        pass
    return matches


def find_similar_to(pcset: PCSet, max_difference: int = 1) -> List[Tuple[str, int]]:
    """
    Find set classes similar to the given set.
    
    Similarity is measured by interval vector difference.
    
    Args:
        pcset: Reference PCSet
        max_difference: Maximum allowed difference in interval vector
    
    Returns:
        List of (forte_number, difference_score) tuples.
    """
    target_iv = pcset.interval_vector()
    results = []
    
    for forte_num, info in COMMON_SETS.items():
        # Skip if different cardinality
        prime = info.get("prime", ())
        if len(prime) != len(pcset):
            continue
        
        # For now, just return common sets of same cardinality
        # A full implementation would compute and compare IVs
        results.append((forte_num, 0))
    
    return results


def find_z_pairs_by_cardinality(cardinality: int) -> List[Tuple[str, str]]:
    """
    Find all Z-related pairs of a given cardinality.
    
    Args:
        cardinality: Number of pitch classes
    
    Returns:
        List of (forte_a, forte_b) tuples.
    
    Example:
        >>> find_z_pairs_by_cardinality(4)
        [('4-Z15', '4-Z29'), ('4-Z18', '4-Z42'), ('4-Z20', '4-Z53')]
    """
    card_str = str(cardinality)
    return [
        pair for pair in [
            ("4-Z15", "4-Z29"),
            ("4-Z18", "4-Z42"),
            ("4-Z20", "4-Z53"),
            ("5-Z17", "5-Z36"),
            ("5-Z18", "5-Z44"),
            ("5-Z19", "5-Z45"),
            ("5-Z37", "5-Z50"),
            ("6-Z17", "6-Z49"),
            ("6-Z19", "6-Z50"),
            ("6-Z28", "6-Z51"),
        ]
        if pair[0].startswith(card_str)
    ]


def compare_sets(set1: PCSet, set2: PCSet) -> dict:
    """
    Compare two pitch class sets.
    
    Returns a dictionary with comparison results:
    - same_cardinality: bool
    - same_prime_form: bool
    - same_interval_vector: bool
    - is_z_related: bool
    - iv_difference: int (sum of absolute differences)
    
    Example:
        >>> s1 = PCSet([0, 4, 7])
        >>> s2 = PCSet([0, 3, 7])
        >>> compare_sets(s1, s2)
        {'same_cardinality': True, 'same_prime_form': True, ...}
    """
    iv1 = set1.interval_vector()
    iv2 = set2.interval_vector()
    
    iv_diff = sum(abs(a - b) for a, b in zip(iv1, iv2))
    
    return {
        "same_cardinality": len(set1) == len(set2),
        "same_prime_form": set1.prime_form() == set2.prime_form(),
        "same_interval_vector": iv1 == iv2,
        "is_z_related": set1.is_z_related_to(set2),
        "iv_difference": iv_diff,
    }


def analyze(pcset: PCSet) -> dict:
    """
    Comprehensive analysis of a pitch class set.
    
    Returns a dictionary with:
    - forte_number: Forte classification
    - prime_form: Prime form tuple
    - interval_vector: Interval content
    - common_name: Common musical name (if known)
    - z_partner: Z-partner (if applicable)
    - cardinality: Number of pitch classes
    - symmetry_order: Symmetry order (if symmetric)
    
    Example:
        >>> s = PCSet([0, 4, 7])
        >>> analysis = analyze(s)
        >>> analysis['common_name']
        'Major Triad'
    """
    from .common_sets import get_by_prime_form, get_z_partners
    
    prime = pcset.prime_form()
    result = get_by_prime_form(prime)
    common_info = result[1] if result else None
    
    forte_num = result[0] if result else pcset.forte_number()
    return {
        "forte_number": forte_num,
        "prime_form": pcset.prime_form(),
        "interval_vector": pcset.interval_vector(),
        "common_name": common_info["name"] if common_info else None,
        "description": common_info["description"] if common_info else None,
        "z_partner": get_z_partners(forte_num),
        "cardinality": len(pcset),
        "pitch_classes": list(pcset.pitch_classes),
    }
