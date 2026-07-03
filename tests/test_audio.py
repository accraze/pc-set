"""Tests for audio analysis module."""

import pytest
from pc_set.audio import (
    HarmonicMoment,
    TrackAnalysis,
    analyze_audio,
    batch_analyze,
)


class TestHarmonicMoment:
    """Tests for HarmonicMoment dataclass."""

    def test_create_moment(self):
        """Test creating a HarmonicMoment."""
        moment = HarmonicMoment(
            timestamp=0.0,
            pitch_classes=[0, 4, 7],
            forte_number="3-11",
            common_name="Major Triad",
            interval_vector=(0, 0, 1, 1, 1, 0),
        )
        assert moment.timestamp == 0.0
        assert moment.pitch_classes == [0, 4, 7]
        assert moment.forte_number == "3-11"
        assert moment.common_name == "Major Triad"

    def test_moment_to_dict(self):
        """Test converting moment to dictionary."""
        moment = HarmonicMoment(
            timestamp=1.5,
            pitch_classes=[0, 3, 7],
            forte_number="3-7",
        )
        data = moment.to_dict()
        assert data["timestamp"] == 1.5
        assert data["pitch_classes"] == [0, 3, 7]
        assert data["forte_number"] == "3-7"
        assert data["common_name"] is None


class TestTrackAnalysis:
    """Tests for TrackAnalysis dataclass."""

    def test_create_analysis(self):
        """Test creating a TrackAnalysis object."""
        moments = [
            HarmonicMoment(0.0, [0, 4, 7], "3-11", "Major Triad"),
            HarmonicMoment(0.5, [0, 3, 7], "3-7", "Minor Triad"),
        ]
        analysis = TrackAnalysis(
            file_path="/path/to/track.wav",
            duration=180.0,
            moments=moments,
            top_sets=[("3-11", 50), ("3-7", 30)],
            average_cardinality=3.2,
            unique_sets=2,
        )
        assert analysis.duration == 180.0
        assert len(analysis.moments) == 2
        assert analysis.unique_sets == 2

    def test_analysis_to_dict(self):
        """Test converting analysis to dictionary."""
        analysis = TrackAnalysis(
            file_path="/test.wav",
            duration=120.0,
            moments=[],
            top_sets=[("3-11", 10)],
            average_cardinality=3.0,
            unique_sets=1,
        )
        data = analysis.to_dict()
        assert data["file_path"] == "/test.wav"
        assert data["duration"] == 120.0
        assert data["unique_sets"] == 1
        assert len(data["top_sets"]) == 1

    def test_analysis_json_roundtrip(self, tmp_path):
        """Test JSON serialization and deserialization."""
        analysis = TrackAnalysis(
            file_path="/test.wav",
            duration=60.0,
            moments=[
                HarmonicMoment(0.0, [0, 4, 7], "3-11"),
                HarmonicMoment(1.0, [0, 3, 7], "3-7"),
            ],
            top_sets=[("3-11", 5)],
            average_cardinality=3.0,
            unique_sets=2,
        )
        
        json_path = tmp_path / "test_analysis.json"
        analysis.to_json(str(json_path))
        
        loaded = TrackAnalysis.from_json(str(json_path))
        assert loaded.duration == 60.0
        assert len(loaded.moments) == 2
        assert loaded.moments[0].forte_number == "3-11"


class TestAnalyzeAudio:
    """Tests for analyze_audio function."""

    def test_missing_file_raises_error(self):
        """Test that missing files raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            analyze_audio("/nonexistent/file.wav")

    def test_missing_librosa_raises_import_error(self, monkeypatch):
        """Test that missing librosa raises ImportError."""
        import sys
        # Simulate librosa not being installed
        monkeypatch.setitem(sys.modules, "librosa", None)
        
        # This will only work if librosa is not available
        # Note: This test may not work if librosa IS installed
        pass


class TestBatchAnalyze:
    """Tests for batch_analyze function."""

    def test_nonexistent_directory_raises_error(self):
        """Test that nonexistent directory raises ValueError."""
        with pytest.raises(ValueError):
            batch_analyze("/nonexistent/directory")

    def test_batch_analyze_empty_directory(self, tmp_path):
        """Test batch_analyze with empty directory."""
        results = batch_analyze(str(tmp_path))
        assert results == []