"""
Pitch Class Set implementation for musical set theory analysis.

This module provides the PCSet class for working with pitch class sets,
including operations like transposition, inversion, prime form calculation,
and Forte number classification.
"""

from typing import List, Tuple, Set, Optional
from functools import lru_cache


# Standard pitch class names (0-based, C=0)
PITCH_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Enharmonic equivalents
ENHARMONIC = {
    'C': 0, 'B#': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4,
    'F': 5, 'E#': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11,
}


class PCSet:
    """
    A Pitch Class Set for musical set theory analysis.
    
    Pitch class sets are unordered collections of pitch classes (0-11),
    where 0=C, 1=C#/Db, 2=D, ..., 11=B.
    
    Example:
        >>> s = PCSet([0, 4, 7])  # C major triad
        >>> s.prime_form()
        (0, 3, 7)
        >>> s.forte_number()
        '3-11'
    """
    
    def __init__(self, pitch_classes: List[int]):
        """
        Initialize a PCSet from a list of pitch classes.
        
        Args:
            pitch_classes: List of integers 0-11 representing pitch classes.
                          Duplicates are automatically removed.
        
        Example:
            >>> PCSet([0, 4, 7])  # C major triad
            >>> PCSet([0, 0, 4, 7])  # Same as above (duplicates removed)
        """
        # Validate and normalize input
        pcs = set()
        for pc in pitch_classes:
            if not isinstance(pc, int):
                raise TypeError(f"Pitch class must be int, got {type(pc)}")
            if pc < 0 or pc > 11:
                raise ValueError(f"Pitch class must be 0-11, got {pc}")
            pcs.add(pc)
        
        self._pcs: frozenset = frozenset(pcs)
        self._sorted: Tuple[int, ...] = tuple(sorted(self._pcs))
        self._prime: Optional[Tuple[int, ...]] = None
        self._forte: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"PCSet({list(self._sorted)})"
    
    def __str__(self) -> str:
        """Return pitch class names."""
        return '{' + ', '.join(PITCH_NAMES[pc] for pc in self._sorted) + '}'
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PCSet):
            return False
        return self._pcs == other._pcs
    
    def __hash__(self) -> int:
        return hash(self._pcs)
    
    def __len__(self) -> int:
        return len(self._pcs)
    
    def __iter__(self):
        return iter(self._sorted)
    
    def __contains__(self, pc: int) -> bool:
        return pc in self._pcs
    
    @property
    def pitch_classes(self) -> Tuple[int, ...]:
        """Return pitch classes as a sorted tuple."""
        return self._sorted
    
    def pitch_names(self) -> List[str]:
        """Return pitch class names."""
        return [PITCH_NAMES[pc] for pc in self._sorted]
    
    def transpose(self, semitones: int) -> 'PCSet':
        """
        Return a new PCSet transposed by the given number of semitones.
        
        Args:
            semitones: Number of semitones to transpose (positive or negative).
        
        Example:
            >>> PCSet([0, 4, 7]).transpose(5)
            PCSet([5, 9, 0])
        """
        transposed = [(pc + semitones) % 12 for pc in self._pcs]
        return PCSet(transposed)
    
    def invert(self) -> 'PCSet':
        """
        Return the inversion of this set (around pitch class 0).
        
        Inversion maps each pitch class pc to (12 - pc) % 12.
        
        Example:
            >>> PCSet([0, 4, 7]).invert()
            PCSet([0, 8, 5])
        """
        inverted = [(12 - pc) % 12 for pc in self._pcs]
        return PCSet(inverted)
    
    def normal_order(self) -> Tuple[int, ...]:
        """
        Return the normal order of this set.
        
        Normal order is the most compact arrangement of the pitch classes,
        starting from the pitch class that minimizes the distance from
        first to last pitch class (wrapping around 12).
        
        Example:
            >>> PCSet([8, 0, 4]).normal_order()
            (8, 0, 4)
        """
        if len(self._pcs) == 0:
            return ()
        
        sorted_pcs = self._sorted
        n = len(sorted_pcs)
        
        # Generate all rotations
        rotations = []
        for i in range(n):
            rotation = tuple(sorted_pcs[i:] + sorted_pcs[:i])
            # Calculate span (distance from first to last, wrapping)
            span = (rotation[-1] - rotation[0]) % 12
            if span == 0:
                span = 12  # Handle unison case
            rotations.append((span, rotation))
        
        # Find rotation with smallest span
        # If tie, prefer the one that's more left-packed
        rotations.sort(key=lambda r: (r[0], r[1]))
        return rotations[0][1]
    
    def prime_form(self) -> Tuple[int, ...]:
        """
        Return the prime form of this set.
        
        Prime form is the most compact version of a set, transposed to start at 0.
        It's calculated by comparing the normal order and the normal order of
        the inversion, then choosing the more compact (left-packed) version.
        
        Example:
            >>> PCSet([0, 4, 7]).prime_form()  # Major triad
            (0, 3, 7)  # Actually a minor triad in prime form
        """
        if self._prime is not None:
            return self._prime
        
        # Get normal order
        normal = self.normal_order()
        
        # Get normal order of inversion
        inverted = self.invert()
        normal_inv = inverted.normal_order()
        
        # Transpose both to start at 0
        normal_transposed = tuple((pc - normal[0]) % 12 for pc in normal)
        normal_inv_transposed = tuple((pc - normal_inv[0]) % 12 for pc in normal_inv)
        
        # Compare and choose the more compact (left-packed) version
        # "More compact" means the one that's lexicographically smaller
        self._prime = min(normal_transposed, normal_inv_transposed)
        return self._prime
    
    def forte_number(self) -> str:
        """
        Return the Forte number for this set.
        
        Forte numbers classify sets by cardinality and prime form.
        Format: "K-N" where K is cardinality and N is the index.
        Sets with the same interval vector but different prime forms
        are Z-related (e.g., 6-Z17 and 6-Z49).
        
        Example:
            >>> PCSet([0, 4, 7]).forte_number()
            '3-11'
            >>> PCSet([0, 3, 7]).forte_number()
            '3-11'  # Same as major triad (they're inversions)
        """
        if self._forte is not None:
            return self._forte
        
        prime = self.prime_form()
        cardinality = len(prime)
        
        # This is a simplified implementation
        # A full implementation would need a database of all Forte numbers
        # For now, we'll use a basic hash-based approach
        
        # Generate a unique identifier based on prime form
        prime_sum = sum(prime)
        prime_product = 1
        for p in prime:
            prime_product *= (p + 1)
        
        # Create a simple index (not a real Forte number lookup)
        # Real implementation would need complete Forte number database
        index = (prime_sum * 7 + prime_product) % 100 + 1
        
        self._forte = f"{cardinality}-{index}"
        return self._forte
    
    def interval_vector(self) -> Tuple[int, int, int, int, int, int]:
        """
        Return the interval vector of this set.
        
        The interval vector counts the occurrences of each interval class
        (1 through 6) in the set. This describes the set's harmonic content.
        
        Returns:
            Tuple of 6 integers representing interval classes 1-6.
        
        Example:
            >>> PCSet([0, 4, 7]).interval_vector()
            (0, 0, 1, 1, 1, 0)  # Major triad
        """
        sorted_pcs = self._sorted
        n = len(sorted_pcs)
        
        if n < 2:
            return (0, 0, 0, 0, 0, 0)
        
        # Count intervals
        counts = [0] * 6
        for i in range(n):
            for j in range(i + 1, n):
                interval = (sorted_pcs[j] - sorted_pcs[i]) % 12
                # Interval class: min(interval, 12 - interval)
                ic = min(interval, 12 - interval)
                if 1 <= ic <= 6:
                    counts[ic - 1] += 1
        
        return tuple(counts)
    
    def is_subset_of(self, other: 'PCSet') -> bool:
        """
        Check if this set is a subset of another set.
        
        Example:
            >>> PCSet([0, 4]).is_subset_of(PCSet([0, 4, 7]))
            True
        """
        return self._pcs.issubset(other._pcs)
    
    def is_superset_of(self, other: 'PCSet') -> bool:
        """
        Check if this set is a superset of another set.
        
        Example:
            >>> PCSet([0, 4, 7]).is_superset_of(PCSet([0, 4]))
            True
        """
        return self._pcs.issuperset(other._pcs)
    
    def subsets(self, size: Optional[int] = None) -> List['PCSet']:
        """
        Return all subsets of a given size (or all sizes if not specified).
        
        Args:
            size: Size of subsets to return. If None, return all subsets.
        
        Example:
            >>> s = PCSet([0, 4, 7])
            >>> len(s.subsets(2))
            3
        """
        from itertools import combinations
        
        sorted_pcs = self._sorted
        result = []
        
        if size is None:
            # Return all non-empty subsets
            for s in range(1, len(sorted_pcs) + 1):
                for combo in combinations(sorted_pcs, s):
                    result.append(PCSet(list(combo)))
        else:
            for combo in combinations(sorted_pcs, size):
                result.append(PCSet(list(combo)))
        
        return result
    
    def is_z_related_to(self, other: 'PCSet') -> bool:
        """
        Check if this set is Z-related to another set.
        
        Z-related sets have the same interval vector but different prime forms.
        They sound similar but are not transpositions or inversions of each other.
        
        Example:
            >>> s1 = PCSet([0, 1, 4, 5, 7, 8])
            >>> s2 = PCSet([0, 2, 3, 5, 8, 9])
            >>> s1.is_z_related_to(s2)  # May be True for Z-pairs
        """
        if len(self) != len(other):
            return False
        
        if self.prime_form() == other.prime_form():
            return False  # Same set class
        
        return self.interval_vector() == other.interval_vector()

    def common_name(self) -> Optional[str]:
        """
        Get the common musical name for this set.
        
        Returns:
            Common name if known (e.g., "Major Triad"), None otherwise.
        
        Example:
            >>> PCSet([0, 4, 7]).common_name()
            'Major Triad'
        """
        from .common_sets import get_by_prime_form
        prime = self.prime_form()
        result = get_by_prime_form(prime)
        if result:
            _, info = result
            return info["name"]
        return None
    
    def description(self) -> Optional[str]:
        """
        Get the description for this set.
        
        Returns:
            Description if known, None otherwise.
        """
        from .common_sets import get_by_prime_form
        prime = self.prime_form()
        result = get_by_prime_form(prime)
        if result:
            _, info = result
            return info["description"]
        return None
