"""Tests for pc_set module."""

import pytest
from pc_set import PCSet


class TestPCSetBasics:
    """Basic PCSet functionality tests."""
    
    def test_create_from_list(self):
        """Test creating a PCSet from a list."""
        s = PCSet([0, 4, 7])
        assert len(s) == 3
        assert 0 in s
        assert 4 in s
        assert 7 in s
    
    def test_remove_duplicates(self):
        """Test that duplicates are removed."""
        s1 = PCSet([0, 4, 7])
        s2 = PCSet([0, 0, 4, 4, 7, 7])
        assert s1 == s2
    
    def test_validate_pitch_classes(self):
        """Test validation of pitch class values."""
        with pytest.raises(ValueError):
            PCSet([12])  # Out of range
        
        with pytest.raises(ValueError):
            PCSet([-1])  # Negative
    
    def test_string_representation(self):
        """Test string representation."""
        s = PCSet([0, 4, 7])
        assert 'C' in str(s)
        assert 'E' in str(s)
        assert 'G' in str(s)


class TestTranspose:
    """Transposition tests."""
    
    def test_transpose_up(self):
        """Test transposing up."""
        s = PCSet([0, 4, 7])  # C major
        t = s.transpose(5)
        assert t == PCSet([5, 9, 0])  # F major
    
    def test_transpose_down(self):
        """Test transposing down."""
        s = PCSet([0, 4, 7])
        t = s.transpose(-5)
        assert t == PCSet([7, 11, 2])
    
    def test_transpose_twelve(self):
        """Test transposing by 12 semitones (octave)."""
        s = PCSet([0, 4, 7])
        t = s.transpose(12)
        assert t == s


class TestInversion:
    """Inversion tests."""
    
    def test_invert_major_triad(self):
        """Test inverting a major triad."""
        s = PCSet([0, 4, 7])  # C major
        inv = s.invert()
        # Inversion of C-E-G around C is C-Ab-F
        assert inv == PCSet([0, 8, 5])
    
    def test_invert_twice(self):
        """Test that inverting twice returns original."""
        s = PCSet([0, 4, 7])
        inv_inv = s.invert().invert()
        assert inv_inv == s


class TestNormalOrder:
    """Normal order tests."""
    
    def test_already_sorted(self):
        """Test normal order when already sorted."""
        s = PCSet([0, 4, 7])
        assert s.normal_order() == (0, 4, 7)
    
    def test_needs_rotation(self):
        """Test normal order with rotation."""
        s = PCSet([8, 0, 4])
        assert s.normal_order() == (0, 4, 8)


class TestPrimeForm:
    """Prime form tests."""
    
    def test_major_triad_prime_form(self):
        """Test prime form of major triad."""
        s = PCSet([0, 4, 7])  # C major
        assert s.prime_form() == (0, 3, 7)  # Minor triad is prime form
    
    def test_minor_triad_prime_form(self):
        """Test prime form of minor triad."""
        s = PCSet([0, 3, 7])  # C minor
        assert s.prime_form() == (0, 3, 7)
    
    def test_consistency_across_transpositions(self):
        """Test that prime form is consistent across transpositions."""
        s1 = PCSet([0, 4, 7])  # C major
        s2 = PCSet([5, 9, 0])  # F major (transposed)
        assert s1.prime_form() == s2.prime_form()


class TestIntervalVector:
    """Interval vector tests."""
    
    def test_major_triad_iv(self):
        """Test interval vector of major triad."""
        s = PCSet([0, 4, 7])
        iv = s.interval_vector()
        # Major triad: M3 (4), m3 (3), P5 (5) -> ic: 1, 1, 1
        assert iv == (0, 0, 1, 1, 1, 0)
    
    def test_chromatic_cluster_iv(self):
        """Test interval vector of chromatic cluster."""
        s = PCSet([0, 1, 2])
        iv = s.interval_vector()
        # Three consecutive semitones
        assert iv[0] == 2  # Two m2 intervals
        assert iv[1] == 1  # One M2 interval
    
    def test_empty_set_iv(self):
        """Test interval vector of empty or single-note set."""
        s = PCSet([0])
        iv = s.interval_vector()
        assert iv == (0, 0, 0, 0, 0, 0)


class TestSubsetOperations:
    """Subset and superset tests."""
    
    def test_is_subset(self):
        """Test subset relationship."""
        s1 = PCSet([0, 4])
        s2 = PCSet([0, 4, 7])
        assert s1.is_subset_of(s2)
        assert not s2.is_subset_of(s1)
    
    def test_is_superset(self):
        """Test superset relationship."""
        s1 = PCSet([0, 4, 7])
        s2 = PCSet([0, 4])
        assert s1.is_superset_of(s2)
        assert not s2.is_superset_of(s1)
    
    def test_subsets_count(self):
        """Test counting subsets."""
        s = PCSet([0, 4, 7])
        subsets_size_2 = s.subsets(2)
        assert len(subsets_size_2) == 3  # 3 choose 2


class TestZRelation:
    """Z-relation tests."""
    
    def test_not_z_related_different_size(self):
        """Test that different-sized sets are not Z-related."""
        s1 = PCSet([0, 4, 7])
        s2 = PCSet([0, 1, 4, 5])
        assert not s1.is_z_related_to(s2)
    
    def test_not_z_related_same_set(self):
        """Test that identical sets are not Z-related."""
        s = PCSet([0, 4, 7])
        assert not s.is_z_related_to(s)


class TestForteNumber:
    """Forte number tests."""
    
    def test_major_triad_forte(self):
        """Test Forte number of major triad."""
        s = PCSet([0, 4, 7])
        fn = s.forte_number()
        assert fn.startswith('3-')  # Cardinality 3
    
    def test_consistency_across_inversions(self):
        """Test that Forte number is consistent across inversions."""
        s1 = PCSet([0, 4, 7])  # Major
        s2 = PCSet([0, 3, 7])  # Minor (inversion of major)
        assert s1.forte_number() == s2.forte_number()
