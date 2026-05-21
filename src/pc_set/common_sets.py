"""
Common set classes with musical names.

This module provides a curated list of frequently encountered pitch class sets
with their musical names and descriptions. Focus on sets that appear in real
compositions and jazz/tonal harmony.
"""

from typing import Dict, Tuple, Optional, List

# Common set classes organized by cardinality
COMMON_SETS: Dict[str, dict] = {
    # Dyads
    "2-1": {"name": "Minor Second", "prime": (0, 1), "description": "Minor second / Major seventh"},
    "2-6": {"name": "Tritone", "prime": (0, 6), "description": "Augmented fourth / Diminished fifth"},
    "2-7": {"name": "Perfect Fifth", "prime": (0, 7), "description": "Perfect fifth / Perfect fourth"},
    
    # Trichords
    "3-1": {"name": "Chromatic Trichord", "prime": (0, 1, 2), "description": "Three consecutive semitones"},
    "3-6": {"name": "Diminished Triad", "prime": (0, 2, 4), "description": "Two stacked minor thirds"},
    "3-11": {"name": "Minor Triad", "prime": (0, 3, 7), "description": "Minor triad"},
    "3-12": {"name": "Major Triad", "prime": (0, 4, 7), "description": "Major triad"},
    
    # Tetrachords
    "4-1": {"name": "Chromatic Tetrachord", "prime": (0, 1, 2, 3), "description": "Four consecutive semitones"},
    "4-10": {"name": "Whole Tone Fragment", "prime": (0, 2, 4, 6), "description": "Four notes from whole tone"},
    "4-14": {"name": "Diminished Seventh", "prime": (0, 3, 6, 9), "description": "Fully diminished seventh"},
    "4-17": {"name": "Minor Seventh", "prime": (0, 3, 7, 10), "description": "Minor seventh chord"},
    "4-18": {"name": "Half-Diminished Seventh", "prime": (0, 3, 7, 11), "description": "m7♭5 chord"},
    "4-19": {"name": "Major Seventh", "prime": (0, 4, 7, 11), "description": "Major seventh chord"},
    "4-21": {"name": "Dominant Seventh", "prime": (0, 4, 7, 10), "description": "Dominant seventh chord"},
    "4-22": {"name": "Minor-Major Seventh", "prime": (0, 4, 7, 11), "description": "Minor-major seventh"},
    
    # Pentachords
    "5-16": {"name": "Minor Pentatonic", "prime": (0, 3, 5, 7, 10), "description": "Minor pentatonic scale"},
    "5-33": {"name": "Major Pentatonic", "prime": (0, 2, 4, 7, 9), "description": "Major pentatonic scale"},
    "5-35": {"name": "Diatonic Pentachord", "prime": (0, 2, 4, 5, 7), "description": "First five notes of major scale"},
    
    # Hexachords
    "6-1": {"name": "Chromatic Hexachord", "prime": (0, 1, 2, 3, 4, 5), "description": "Six consecutive semitones"},
    "6-7": {"name": "Whole Tone Scale", "prime": (0, 2, 4, 6, 8, 10), "description": "Complete whole tone scale"},
    "6-20": {"name": "Diatonic Hexachord", "prime": (0, 2, 3, 5, 7, 9), "description": "Major scale without leading tone"},
    
    # Heptachords
    "7-1": {"name": "Diatonic Scale", "prime": (0, 2, 4, 5, 7, 9, 11), "description": "Major scale"},
    "7-2": {"name": "Melodic Minor", "prime": (0, 2, 3, 5, 7, 9, 11), "description": "Jazz melodic minor"},
    "7-3": {"name": "Harmonic Minor", "prime": (0, 2, 4, 5, 7, 8, 11), "description": "Harmonic minor scale"},
    
    # Octachords
    "8-1": {"name": "Octatonic Scale", "prime": (0, 1, 3, 4, 6, 7, 9, 10), "description": "Octatonic (diminished) scale"},
    
    # Dodecachords
    "12-1": {"name": "Chromatic Scale", "prime": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), "description": "Complete chromatic"},
}

# Z-related pairs
Z_PAIRS: List[Tuple[str, str]] = [
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


def get_common_set(forte_number: str) -> Optional[dict]:
    """Get info for a common set by Forte number."""
    return COMMON_SETS.get(forte_number)


def get_set_by_name(name: str) -> Optional[Tuple[str, dict]]:
    """Find set by common name (case-insensitive)."""
    name_lower = name.lower()
    for forte_num, info in COMMON_SETS.items():
        if info["name"].lower() == name_lower:
            return (forte_num, info)
    return None


def search_by_name(query: str) -> List[Tuple[str, dict]]:
    """Search sets by name (partial match)."""
    query_lower = query.lower()
    return [
        (forte_num, info)
        for forte_num, info in COMMON_SETS.items()
        if query_lower in info["name"].lower() or query_lower in info.get("description", "").lower()
    ]


def get_z_partners(forte_number: str) -> Optional[str]:
    """Get Z-partner of a Forte number."""
    for pair in Z_PAIRS:
        if forte_number == pair[0]:
            return pair[1]
        elif forte_number == pair[1]:
            return pair[0]
    return None


def is_z_related(forte_number: str) -> bool:
    """Check if Forte number has Z-partner."""
    return get_z_partners(forte_number) is not None


def get_all_z_pairs() -> List[Tuple[str, str]]:
    """Get all Z-related pairs."""
    return Z_PAIRS.copy()


def get_by_cardinality(cardinality: int) -> List[Tuple[str, dict]]:
    """Get all common sets of given cardinality."""
    cardinality_str = str(cardinality)
    return [
        (forte_num, info)
        for forte_num, info in COMMON_SETS.items()
        if forte_num.startswith(cardinality_str + "-")
    ]

# Create a reverse lookup by prime form
PRIME_TO_FORTE: Dict[Tuple[int, ...], str] = {
    info["prime"]: forte_num
    for forte_num, info in COMMON_SETS.items()
}


def get_by_prime_form(prime_form: Tuple[int, ...]) -> Optional[Tuple[str, dict]]:
    """
    Get Forte number and info by prime form.
    
    Args:
        prime_form: Prime form tuple
    
    Returns:
        Tuple of (forte_number, info) or None if not found.
    """
    forte_num = PRIME_TO_FORTE.get(prime_form)
    if forte_num:
        return (forte_num, COMMON_SETS[forte_num])
    return None
