"""Tests for common sets and search functionality."""

import pytest
from pc_set import PCSet
from pc_set.common_sets import (
    get_common_set,
    get_set_by_name,
    search_by_name,
    get_z_partners,
    is_z_related,
    get_all_z_pairs,
    get_by_cardinality,
)
from pc_set.search import analyze, compare_sets, find_z_pairs_by_cardinality


class TestCommonSets:
    """Test common set lookup functions."""
    
    def test_get_common_set_exists(self):
        """Test getting a known set."""
        info = get_common_set("3-12")
        assert info is not None
        assert info["name"] == "Major Triad"
    
    def test_get_common_set_not_exists(self):
        """Test getting an unknown set."""
        info = get_common_set("99-99")
        assert info is None
    
    def test_get_set_by_name_exact(self):
        """Test finding set by exact name."""
        result = get_set_by_name("Major Triad")
        assert result is not None
        forte_num, info = result
        assert forte_num == "3-12"
    
    def test_get_set_by_name_case_insensitive(self):
        """Test case-insensitive name lookup."""
        result1 = get_set_by_name("major triad")
        result2 = get_set_by_name("MAJOR TRIAD")
        assert result1 is not None
        assert result2 is not None
        assert result1[0] == result2[0]
    
    def test_search_by_name_partial(self):
        """Test partial name search."""
        results = search_by_name("dominant")
        assert len(results) > 0
        # All results should contain "dominant"
        for forte_num, info in results:
            assert "dominant" in info["name"].lower() or "dominant" in info["description"].lower()
    
    def test_get_by_cardinality(self):
        """Test filtering by cardinality."""
        trichords = get_by_cardinality(3)
        assert len(trichords) > 0
        for forte_num, info in trichords:
            assert forte_num.startswith("3-")
    
    def test_z_partners(self):
        """Test Z-partner lookup."""
        # 4-Z15 and 4-Z29 are Z-related
        assert get_z_partners("4-Z15") == "4-Z29"
        assert get_z_partners("4-Z29") == "4-Z15"
        # Non-Z sets return None
        assert get_z_partners("3-12") is None
    
    def test_is_z_related(self):
        """Test Z-relation check."""
        assert is_z_related("4-Z15")
        assert not is_z_related("3-12")
    
    def test_all_z_pairs(self):
        """Test getting all Z pairs."""
        pairs = get_all_z_pairs()
        assert len(pairs) > 0
        # Should be a list of tuples
        for pair in pairs:
            assert isinstance(pair, tuple)
            assert len(pair) == 2


class TestPCSetExtensions:
    """Test PCSet methods for common names."""
    
    def test_common_name_major_triad(self):
        """Test common name for major triad."""
        s = PCSet([0, 4, 7])
        assert s.common_name() in ["Major Triad", "Minor Triad"]
    
    def test_common_name_minor_triad(self):
        """Test common name for minor triad."""
        s = PCSet([0, 3, 7])
        assert s.common_name() == "Minor Triad"
    
    def test_common_name_unknown(self):
        """Test common name for unknown set."""
        # Some random set that might not be in common sets
        s = PCSet([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # Should return something (chromatic scale is common)
        # If not in database, returns None
        name = s.common_name()
        # Either has a name or doesn't - just checking it doesn't crash
        assert name is None or isinstance(name, str)
    
    def test_description(self):
        """Test set description."""
        s = PCSet([0, 4, 7])
        desc = s.description()
        assert desc is not None
        assert "major" in desc.lower() or "triad" in desc.lower()


class TestAnalyze:
    """Test comprehensive analysis function."""
    
    def test_analyze_major_triad(self):
        """Test analyzing a major triad."""
        s = PCSet([0, 4, 7])
        analysis = analyze(s)
        
        assert analysis["forte_number"].startswith("3-")
        assert analysis["common_name"] in ["Major Triad", "Minor Triad"]
        assert analysis["cardinality"] == 3
        assert len(analysis["interval_vector"]) == 6
    
    def test_analyze_returns_all_fields(self):
        """Test that analyze returns all expected fields."""
        s = PCSet([0, 4, 7])
        analysis = analyze(s)
        
        expected_fields = [
            "forte_number", "prime_form", "interval_vector",
            "common_name", "description", "z_partner",
            "cardinality", "pitch_classes"
        ]
        for field in expected_fields:
            assert field in analysis


class TestCompareSets:
    """Test set comparison."""
    
    def test_compare_same_sets(self):
        """Test comparing identical sets."""
        s1 = PCSet([0, 4, 7])
        s2 = PCSet([0, 4, 7])
        result = compare_sets(s1, s2)
        
        assert result["same_cardinality"]
        assert result["same_prime_form"]
        assert result["same_interval_vector"]
        assert result["iv_difference"] == 0
    
    def test_compare_major_minor(self):
        """Test comparing major and minor triads."""
        s1 = PCSet([0, 4, 7])  # Major
        s2 = PCSet([0, 3, 7])  # Minor
        result = compare_sets(s1, s2)
        
        assert result["same_cardinality"]
        assert result["same_prime_form"]  # Both have same prime form
        assert result["same_interval_vector"]  # Same IV
        assert not result["is_z_related"]  # Not Z-related (same set class)
    
    def test_compare_different_cardinality(self):
        """Test comparing sets of different sizes."""
        s1 = PCSet([0, 4, 7])  # Trichord
        s2 = PCSet([0, 4, 7, 10])  # Tetrachord
        result = compare_sets(s1, s2)
        
        assert not result["same_cardinality"]


class TestFindZPairs:
    """Test Z-pair finding."""
    
    def test_find_z_pairs_cardinality_4(self):
        """Test finding Z pairs for cardinality 4."""
        pairs = find_z_pairs_by_cardinality(4)
        assert len(pairs) > 0
        for pair in pairs:
            assert pair[0].startswith("4-")
            assert pair[1].startswith("4-")
    
    def test_find_z_pairs_cardinality_3(self):
        """Test that cardinality 3 has no Z pairs."""
        pairs = find_z_pairs_by_cardinality(3)
        assert len(pairs) == 0  # No Z-relations for trichords
