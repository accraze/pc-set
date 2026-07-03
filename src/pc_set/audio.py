"""
Audio analysis tools for pitch class set extraction.

This module provides functionality to analyze audio files and extract
harmonic content using chroma feature extraction.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

from .pcset import PCSet


@dataclass
class HarmonicMoment:
    """Represents a harmonic moment in an audio track."""
    timestamp: float
    pitch_classes: List[int]
    forte_number: Optional[str] = None
    common_name: Optional[str] = None
    interval_vector: Optional[Tuple[int, ...]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'timestamp': self.timestamp,
            'pitch_classes': self.pitch_classes,
            'forte_number': self.forte_number,
            'common_name': self.common_name,
            'interval_vector': self.interval_vector
        }


@dataclass
class TrackAnalysis:
    """Complete analysis results for a single track."""
    file_path: str
    duration: float
    moments: List[HarmonicMoment]
    top_sets: List[Tuple[str, int]]  # (forte_number, count)
    average_cardinality: float
    unique_sets: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'file_path': self.file_path,
            'duration': self.duration,
            'moments': [m.to_dict() for m in self.moments],
            'top_sets': [{'forte_number': fs, 'count': c} for fs, c in self.top_sets],
            'average_cardinality': self.average_cardinality,
            'unique_sets': self.unique_sets
        }
    
    def to_json(self, path: str) -> None:
        """Save analysis to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrackAnalysis':
        """Create TrackAnalysis from dictionary."""
        moments = [
            HarmonicMoment(
                timestamp=m['timestamp'],
                pitch_classes=m['pitch_classes'],
                forte_number=m.get('forte_number'),
                common_name=m.get('common_name'),
                interval_vector=tuple(m['interval_vector']) if m.get('interval_vector') else None
            )
            for m in data['moments']
        ]
        return cls(
            file_path=data['file_path'],
            duration=data['duration'],
            moments=moments,
            top_sets=[(t['forte_number'], t['count']) for t in data['top_sets']],
            average_cardinality=data['average_cardinality'],
            unique_sets=data['unique_sets']
        )
    
    @classmethod
    def from_json(cls, path: str) -> 'TrackAnalysis':
        """Load analysis from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


def analyze_audio(
    file_path: str,
    duration: Optional[float] = None,
    hop_length: int = 512,
    frame_length: int = 2048,
    threshold: float = 0.1
) -> TrackAnalysis:
    """
    Analyze an audio file and extract pitch class set information.
    
    Args:
        file_path: Path to audio file (WAV, MP3, FLAC, etc.)
        duration: Optional duration in seconds to analyze (None = full track)
        hop_length: Number of samples between consecutive frames
        frame_length: Number of samples per frame
        threshold: Amplitude threshold for onset detection
        
    Returns:
        TrackAnalysis object containing all harmonic moments and statistics
        
    Example:
        >>> results = analyze_audio("track.wav", duration=60)
        >>> print(f"Found {len(results.moments)} harmonic moments")
        >>> print(f"Most common set: {results.top_sets[0]}")
    """
    try:
        import librosa
    except ImportError:
        raise ImportError(
            "librosa is required for audio analysis. "
            "Install it with: pip install librosa"
        )
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Load audio file
    y, sr = librosa.load(str(path), duration=duration, mono=True)
    duration_seconds = librosa.get_duration(y=y, sr=sr)
    
    # Compute chroma features (CQT for better pitch resolution)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    
    # Detect onsets for beat-synchronized analysis
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)[1]
    
    # Convert beat times to sample indices
    beat_samples = librosa.frames_to_samples(beats, hop_length=hop_length)
    
    # Process each beat segment
    moments = []
    for i, beat_time in enumerate(beats):
        # Get the beat segment (from this beat to the next)
        start_sample = beat_samples[i] if i < len(beat_samples) else len(y)
        end_sample = beat_samples[i + 1] if i + 1 < len(beat_samples) else len(y)
        
        if start_sample >= end_sample:
            continue
            
        # Extract chroma for this segment
        start_frame = librosa.sample_to_frames(start_sample, hop_length=hop_length)[0]
        end_frame = librosa.sample_to_frames(end_sample, hop_length=hop_length)[0]
        
        if start_frame >= chroma.shape[1] or end_frame > chroma.shape[1]:
            continue
            
        segment_chroma = chroma[:, start_frame:end_frame]
        
        # Get active pitch classes (above threshold)
        mean_chroma = segment_chroma.mean(axis=1)
        active_pcs = [i for i, val in enumerate(mean_chroma) if val > threshold]
        
        if len(active_pcs) >= 3:  # Only analyze chords with 3+ pitch classes
            # Create PCSet and analyze
            pcset = PCSet(active_pcs)
            forte = pcset.forte_number
            common = pcset.common_name()
            iv = pcset.interval_vector
            
            moment = HarmonicMoment(
                timestamp=float(beat_time),
                pitch_classes=active_pcs,
                forte_number=forte,
                common_name=common,
                interval_vector=iv
            )
            moments.append(moment)
    
    # Compute statistics
    if moments:
        # Count set occurrences
        set_counts: Dict[str, int] = {}
        cardinalities = []
        
        for moment in moments:
            if moment.forte_number:
                set_counts[moment.forte_number] = set_counts.get(moment.forte_number, 0) + 1
            if moment.pitch_classes:
                cardinalities.append(len(moment.pitch_classes))
        
        # Sort by frequency
        top_sets = sorted(set_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        avg_card = sum(cardinalities) / len(cardinalities) if cardinalities else 0
    else:
        top_sets = []
        avg_card = 0
    
    return TrackAnalysis(
        file_path=str(path.absolute()),
        duration=duration_seconds,
        moments=moments,
        top_sets=top_sets,
        average_cardinality=avg_card,
        unique_sets=len(set_counts) if moments else 0
    )


def batch_analyze(
    directory: str,
    extensions: Tuple[str, ...] = ('.wav', '.mp3', '.flac', '.m4a', '.ogg'),
    max_duration: Optional[float] = None,
    **kwargs
) -> List[TrackAnalysis]:
    """
    Analyze all audio files in a directory.
    
    Args:
        directory: Path to directory containing audio files
        extensions: Tuple of file extensions to process
        max_duration: Maximum duration per track in seconds
        **kwargs: Additional arguments passed to analyze_audio
        
    Returns:
        List of TrackAnalysis objects for each processed file
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    
    results = []
    audio_files = []
    
    for ext in extensions:
        audio_files.extend(path.rglob(f"*{ext}"))
        audio_files.extend(path.rglob(f"*{ext.upper()}"))
    
    # Remove duplicates (case-insensitive)
    audio_files = list({f.resolve() for f in audio_files})
    
    for audio_file in sorted(audio_files):
        try:
            print(f"Analyzing: {audio_file.name}")
            analysis = analyze_audio(
                str(audio_file),
                duration=max_duration,
                **kwargs
            )
            results.append(analysis)
        except Exception as e:
            print(f"Error analyzing {audio_file.name}: {e}")
            continue
    
    return results