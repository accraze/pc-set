# PC-Set

**Pitch Class Set Theory for Python**

A library for analyzing and manipulating pitch class sets using musical set theory. Useful for atonal music analysis, composition, and music theory education.

[![PyPI](https://img.shields.io/pypi/v/pc-set.svg)](https://pypi.org/project/pc-set/)
[![Python Version](https://img.shields.io/pypi/pyversions/pc-set.svg)](https://pypi.org/project/pc-set/)
[![License](https://img.shields.io/pypi/l/pc-set.svg)](https://github.com/accraze/pc-set/blob/master/LICENSE)

## Installation

```bash
pip install pc-set
```

## Quick Start

```python
from pc_set import PCSet

# Create a pitch class set (C=0, C#=1, ..., B=11)
s = PCSet([0, 4, 7])  # C major triad: C-E-G

# Get prime form (canonical representation)
print(s.prime_form())  # (0, 3, 7) - minor triad is prime form

# Get Forte number (set class identifier)
print(s.forte_number())  # "3-11"

# Get interval vector (harmonic content)
print(s.interval_vector())  # (0, 0, 1, 1, 1, 0)

# Transpose
print(s.transpose(5))  # PCSet([5, 9, 0]) - F major

# Invert
print(s.invert())  # PCSet([0, 8, 5]) - C-Ab-F
```

## What are Pitch Class Sets?

In music theory, a **pitch class** groups all notes with the same name across octaves:
- C4, C3, C5 → all belong to pitch class **C** (or **0**)
- We use integers 0-11: C=0, C#=1, D=2, ..., B=11

A **pitch class set** is an unordered collection of these pitch classes, used to analyze atonal music and discover harmonic relationships.

## Features

### Basic Operations

```python
from pc_set import PCSet

# Create sets
major = PCSet([0, 4, 7])    # C-E-G
minor = PCSet([0, 3, 7])    # C-Eb-G
diminished = PCSet([0, 3, 6, 9])  # C-Eb-Gb-A

# Transposition
print(major.transpose(7))   # G-B-D

# Inversion
print(major.invert())       # C-Ab-F

# Normal order (most compact arrangement)
print(PCSet([8, 0, 4]).normal_order())  # (8, 0, 4)

# Prime form (canonical version)
print(major.prime_form())   # (0, 3, 7)
```

### Set Analysis

```python
# Forte number (set class classification)
print(major.forte_number())  # "3-11"

# Interval vector (interval content)
print(diminished.interval_vector())  # (0, 3, 0, 3, 0, 0)
# Interpretation: 3 minor thirds, 3 tritones

# Subset relationships
print(PCSet([0, 4]).is_subset_of(major))  # True
print(major.is_superset_of(PCSet([0, 4])))  # True

# Get all subsets of a given size
for subset in major.subsets(2):
    print(subset)  # {C, E}, {C, G}, {E, G}
```

### Z-Relations

Z-related sets have the same interval vector but different prime forms:

```python
# Two hexachords that are Z-related
s1 = PCSet([0, 1, 4, 5, 7, 8])
s2 = PCSet([0, 2, 3, 5, 8, 9])

print(s1.interval_vector())  # Same as s2
print(s2.interval_vector())  # Same as s1
print(s1.is_z_related_to(s2))  # True
```

## Integration with twelve-tone

PC-Set works great with the `twelve-tone` package for serial composition:

```python
from twelve_tone import Composer
from pc_set import PCSet

# Generate a twelve-tone row
c = Composer()
c.compose()
row = c.get_melody_integers()

# Analyze hexachords
hexachord1 = PCSet(row[:6])
hexachord2 = PCSet(row[6:])

print(f"First hexachord: {hexachord1.prime_form()}")
print(f"Second hexachord: {hexachord2.prime_form()}")
print(f"Z-related: {hexachord1.is_z_related_to(hexachord2)}")
```

## API Reference

### PCSet Class

#### Initialization
- `PCSet(pitch_classes)`: Create from list of integers 0-11

#### Properties
- `.pitch_classes`: Tuple of pitch classes
- `.prime_form()`: Canonical form starting at 0
- `.forte_number()`: Forte classification (e.g., "3-11")
- `.interval_vector()`: Interval content tuple

#### Operations
- `.transpose(semitones)`: Transpose by semitones
- `.invert()`: Invert around pitch class 0
- `.normal_order()`: Most compact rotation
- `.is_subset_of(other)`: Check subset relationship
- `.is_superset_of(other)`: Check superset relationship
- `.subsets(size)`: Get all subsets of given size
- `.is_z_related_to(other)`: Check Z-relation

## Background

Pitch class set theory was developed in the 1960s-70s by music theorists including Allen Forte, John Rahn, and others to analyze atonal music (Schoenberg, Webern, Berg, Babbitt). It provides a mathematical framework for understanding harmonic relationships in music without traditional tonality.

Key concepts:
- **Normal Order**: Most compact arrangement of a set
- **Prime Form**: Canonical representation (transposed to start at 0)
- **Forte Number**: Classification system (e.g., "3-11" for major/minor triads)
- **Interval Vector**: Distribution of interval classes in the set
- **Z-Relation**: Sets with same interval vector but different prime forms

## License

BSD 2-Clause License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! This is a learning project exploring music theory through code.

## Related Projects

- [twelve-tone](https://github.com/accraze/python-twelve-tone) - Twelve-tone matrix generator
- [music21](https://github.com/cuthbertLab/music21) - Comprehensive music analysis toolkit
- [teoria](https://github.com/bernhardschultze/teoria) - Music theory library (JavaScript)
