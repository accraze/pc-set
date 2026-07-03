"""Tests for catalog analysis module."""

import pytest
from pc_set.catalog import (
    CatalogAnalyzer,
    CatalogInsights,
    CatalogPattern,
)
from pc_set.audio import TrackAnalysis, HarmonicMoment


class TestCatalogInsights:
    """Tests for CatalogInsights dataclass."""

    def test_create_insights(self):
        """Test creating CatalogInsights."""
        insights = CatalogInsights(
            total_tracks=10,
            total_moments=100,
            unique_sets={"3-11", "3-7", "4-19"},
            top_sets=[("3-11", 40), ("3-7", 30)],
            average_cardinality=3.5,
            set_distribution={"3-11": 40, "3-7": 30},
            cardinality_distribution={3: 60, 4: 40},
            most_common_names=[("Major Triad", 40)],
            z_relation_pairs=[("6-Z44", "6-Z38", 10)],
        )
        assert insights.total_tracks == 10
        assert insights.total_moments == 100
        assert len(insights.unique_sets) == 3

    def test_insights_summary(self):
        """Test generating insights summary."""
        insights = CatalogInsights(
            total_tracks=5,
            total_moments=50,
            unique_sets={"3-11", "4-19"},
            top_sets=[("3-11", 30), ("4-19", 20)],
            average_cardinality=3.2,
        )
        summary = insights.summary()
        assert "5" in summary
        assert "50" in summary
        assert "3-11" in summary

    def test_insights_to_dict(self):
        """Test converting insights to dictionary."""
        insights = CatalogInsights(
            total_tracks=1,
            total_moments=10,
            unique_sets={"3-11"},
            top_sets=[("3-11", 10)],
            average_cardinality=3.0,
            set_distribution={"3-11": 10},
            cardinality_distribution={3: 10},
            most_common_names=[],
            z_relation_pairs=[],
        )
        data = insights.to_dict()
        assert data["total_tracks"] == 1
        assert "3-11" in data["unique_sets"]

    def test_insights_json_roundtrip(self, tmp_path):
        """Test JSON serialization and deserialization."""
        insights = CatalogInsights(
            total_tracks=3,
            total_moments=30,
            unique_sets={"3-11", "3-7"},
            top_sets=[("3-11", 20), ("3-7", 10)],
            average_cardinality=3.1,
            set_distribution={"3-11": 20, "3-7": 10},
            cardinality_distribution={3: 25, 4: 5},
            most_common_names=[("Major Triad", 20)],
            z_relation_pairs=[("6-Z44", "6-Z38", 5)],
        )
        
        json_path = tmp_path / "insights.json"
        insights.to_json(str(json_path))
        
        loaded = CatalogInsights.from_json(str(json_path))
        assert loaded.total_tracks == 3
        assert len(loaded.unique_sets) == 2
        assert len(loaded.z_relation_pairs) == 1


class TestCatalogPattern:
    """Tests for CatalogPattern dataclass."""

    def test_create_pattern(self):
        """Test creating CatalogPattern."""
        pattern = CatalogPattern(
            pattern_type="repeated_set",
            description="Major triad appears frequently",
            occurrences=[{"timestamp": 0.0}, {"timestamp": 1.0}],
            frequency=0.25,
        )
        assert pattern.pattern_type == "repeated_set"
        assert len(pattern.occurrences) == 2


class TestCatalogAnalyzer:
    """Tests for CatalogAnalyzer class."""

    def test_init_nonexistent_directory(self):
        """Test that nonexistent directory raises ValueError."""
        with pytest.raises(ValueError):
            CatalogAnalyzer("/nonexistent/directory")

    def test_init_valid_directory(self, tmp_path):
        """Test initialization with valid directory."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        assert analyzer.directory == tmp_path
        assert analyzer.results == []
        assert analyzer.insights is None

    def test_discover_patterns_empty_results(self, tmp_path):
        """Test discover_patterns with no results raises error."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        with pytest.raises(ValueError):
            analyzer.discover_patterns()

    def test_find_similar_tracks(self, tmp_path):
        """Test find_similar_tracks functionality."""
        # Create test files
        (tmp_path / "track1.wav").touch()
        
        analyzer = CatalogAnalyzer(str(tmp_path))
        
        # Add mock analysis results
        analysis = TrackAnalysis(
            file_path=str(tmp_path / "track1.wav"),
            duration=60.0,
            moments=[
                HarmonicMoment(0.0, [0, 4, 7], "3-11"),
                HarmonicMoment(1.0, [0, 4, 7], "3-11"),
            ],
            top_sets=[("3-11", 2)],
            average_cardinality=3.0,
            unique_sets=1,
        )
        analyzer.results = [analysis]
        
        # Test finding similar tracks
        similar = analyzer.find_similar_tracks("3-11")
        assert len(similar) == 1

    def test_find_similar_tracks_unknown_set(self, tmp_path):
        """Test find_similar_tracks with unknown set raises error."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        analyzer.results = []
        
        with pytest.raises(ValueError):
            analyzer.find_similar_tracks("unknown-set")


class TestCatalogAnalyzerIntegration:
    """Integration tests for CatalogAnalyzer with mock data."""

    def test_full_analysis_workflow(self, tmp_path):
        """Test complete analysis workflow with mock data."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        
        # Create mock analysis results
        mock_results = []
        for i in range(3):
            analysis = TrackAnalysis(
                file_path=str(tmp_path / f"track{i}.wav"),
                duration=180.0,
                moments=[
                    HarmonicMoment(0.0, [0, 4, 7], "3-11", "Major Triad"),
                    HarmonicMoment(1.0, [0, 3, 7], "3-7", "Minor Triad"),
                    HarmonicMoment(2.0, [0, 4, 7], "3-11", "Major Triad"),
                ],
                top_sets=[("3-11", 2), ("3-7", 1)],
                average_cardinality=3.0,
                unique_sets=2,
            )
            mock_results.append(analysis)
        
        analyzer.results = mock_results
        
        # Discover patterns
        insights = analyzer.discover_patterns()
        
        assert insights.total_tracks == 3
        assert insights.total_moments == 9
        assert "3-11" in insights.unique_sets
        assert "3-7" in insights.unique_sets
        
        # Check top sets
        assert len(insights.top_sets) == 2
        assert insights.top_sets[0][0] == "3-11"
        assert insights.top_sets[0][1] == 6  # 2 per track * 3 tracks

    def test_save_and_load_results(self, tmp_path):
        """Test saving and loading analysis results."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        
        # Create mock results
        analysis = TrackAnalysis(
            file_path=str(tmp_path / "track.wav"),
            duration=120.0,
            moments=[
                HarmonicMoment(0.0, [0, 4, 7], "3-11"),
            ],
            top_sets=[("3-11", 1)],
            average_cardinality=3.0,
            unique_sets=1,
        )
        analyzer.results = [analysis]
        
        # Save results
        results_path = tmp_path / "results.json"
        analyzer.save_results(str(results_path))
        
        # Load in new analyzer
        new_analyzer = CatalogAnalyzer(str(tmp_path))
        new_analyzer.load_results(str(results_path))
        
        assert len(new_analyzer.results) == 1
        assert new_analyzer.results[0].duration == 120.0

    def test_export_to_csv(self, tmp_path):
        """Test CSV export functionality."""
        analyzer = CatalogAnalyzer(str(tmp_path))
        
        # Create mock results
        analysis = TrackAnalysis(
            file_path=str(tmp_path / "track.wav"),
            duration=180.0,
            moments=[
                HarmonicMoment(0.0, [0, 4, 7], "3-11"),
                HarmonicMoment(1.0, [0, 3, 7], "3-7"),
            ],
            top_sets=[("3-11", 50), ("3-7", 30), ("4-20", 20)],
            average_cardinality=3.2,
            unique_sets=3,
        )
        analyzer.results = [analysis]
        
        # Export to CSV
        csv_path = tmp_path / "catalog.csv"
        analyzer.export_to_csv(str(csv_path))
        
        # Verify CSV was created
        assert csv_path.exists()
        
        # Read and verify content
        content = csv_path.read_text()
        assert "track.wav" in content
        assert "3-11" in content
        assert "3-7" in content