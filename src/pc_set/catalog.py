"""
Catalog analysis tools for batch processing and pattern discovery.

This module provides the CatalogAnalyzer class for processing entire
music collections and discovering harmonic patterns.
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import Counter
import json
from pathlib import Path
from datetime import datetime

from .audio import TrackAnalysis, analyze_audio, batch_analyze
from .pcset import PCSet
from .common_sets import get_common_set


@dataclass
class CatalogInsights:
    """Container for catalog-wide insights and patterns."""
    total_tracks: int
    total_moments: int
    unique_sets: Set[str] = field(default_factory=set)
    top_sets: List[Tuple[str, int]] = field(default_factory=list)
    average_cardinality: float = 0.0
    set_distribution: Dict[str, int] = field(default_factory=dict)
    cardinality_distribution: Dict[int, int] = field(default_factory=dict)
    most_common_names: List[Tuple[str, int]] = field(default_factory=list)
    z_relation_pairs: List[Tuple[str, str, int]] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate a human-readable summary of insights."""
        lines = [
            f"=== Catalog Analysis Summary ===",
            f"Total tracks analyzed: {self.total_tracks}",
            f"Total harmonic moments: {self.total_moments}",
            f"Unique set classes: {len(self.unique_sets)}",
            f"Average cardinality: {self.average_cardinality:.2f}",
            "",
            "Top 10 Set Classes:",
        ]
        
        for i, (forte, count) in enumerate(self.top_sets[:10], 1):
            name = "Unknown"
            set_info = get_common_set(forte)
            if set_info and set_info.get('common_name'):
                name = set_info['common_name']
            lines.append(f"  {i}. {forte}: {count} occurrences ({name})")
        
        if self.z_relation_pairs:
            lines.append("")
            lines.append("Detected Z-Relation Pairs:")
            for pair_a, pair_b, count in self.z_relation_pairs[:5]:
                lines.append(f"  {pair_a} <-> {pair_b}: {count} occurrences")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_tracks': self.total_tracks,
            'total_moments': self.total_moments,
            'unique_sets': list(self.unique_sets),
            'top_sets': [{'forte_number': f, 'count': c} for f, c in self.top_sets],
            'average_cardinality': self.average_cardinality,
            'set_distribution': self.set_distribution,
            'cardinality_distribution': self.cardinality_distribution,
            'most_common_names': [{'name': n, 'count': c} for n, c in self.most_common_names],
            'z_relation_pairs': [
                {'set_a': a, 'set_b': b, 'count': c}
                for a, b, c in self.z_relation_pairs
            ]
        }
    
    def to_json(self, path: str) -> None:
        """Save insights to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CatalogInsights':
        """Create CatalogInsights from dictionary."""
        return cls(
            total_tracks=data['total_tracks'],
            total_moments=data['total_moments'],
            unique_sets=set(data['unique_sets']),
            top_sets=[(t['forte_number'], t['count']) for t in data['top_sets']],
            average_cardinality=data['average_cardinality'],
            set_distribution=data['set_distribution'],
            cardinality_distribution=data['cardinality_distribution'],
            most_common_names=[(n['name'], n['count']) for n in data['most_common_names']],
            z_relation_pairs=[(p['set_a'], p['set_b'], p['count']) for p in data['z_relation_pairs']]
        )
    
    @classmethod
    def from_json(cls, path: str) -> 'CatalogInsights':
        """Load insights from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


@dataclass
class CatalogPattern:
    """Represents a discovered pattern in the catalog."""
    pattern_type: str  # 'repeated_set', 'progression', 'similarity', etc.
    description: str
    occurrences: List[Dict]  # List of occurrence details
    frequency: float  # How often this pattern appears


class CatalogAnalyzer:
    """
    Analyzer for processing and discovering patterns in music catalogs.
    
    This class provides tools for batch processing audio files and
    discovering harmonic patterns across an entire collection.
    
    Example:
        >>> analyzer = CatalogAnalyzer("/path/to/tracks")
        >>> analyzer.process_all()
        >>> insights = analyzer.discover_patterns()
        >>> print(insights.summary())
        >>> analyzer.save_results("catalog_analysis.json")
    """
    
    def __init__(self, directory: str):
        """
        Initialize the catalog analyzer.
        
        Args:
            directory: Path to directory containing audio files
        """
        self.directory = Path(directory)
        if not self.directory.is_dir():
            raise ValueError(f"Directory not found: {directory}")
        
        self.results: List[TrackAnalysis] = []
        self.insights: Optional[CatalogInsights] = None
        self.patterns: List[CatalogPattern] = []
        self._cache_dir = self.directory / ".pc_set_cache"
        
        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(exist_ok=True)
    
    def process_all(
        self,
        extensions: Tuple[str, ...] = ('.wav', '.mp3', '.flac', '.m4a', '.ogg'),
        max_duration: Optional[float] = None,
        use_cache: bool = True,
        **kwargs
    ) -> List[TrackAnalysis]:
        """
        Process all audio files in the catalog.
        
        Args:
            extensions: File extensions to process
            max_duration: Maximum duration per track
            use_cache: Whether to use cached results
            **kwargs: Additional arguments for analyze_audio
            
        Returns:
            List of TrackAnalysis results for each file
        """
        results = []
        audio_files = []
        
        for ext in extensions:
            audio_files.extend(self.directory.rglob(f"*{ext}"))
            audio_files.extend(self.directory.rglob(f"*{ext.upper()}"))
        
        # Remove duplicates (case-insensitive)
        audio_files = list({f.resolve() for f in audio_files})
        
        print(f"Found {len(audio_files)} audio files to process")
        
        for audio_file in sorted(audio_files):
            cache_file = self._cache_dir / f"{audio_file.stem}_analysis.json"
            
            # Check cache
            if use_cache and cache_file.exists():
                try:
                    analysis = TrackAnalysis.from_json(str(cache_file))
                    print(f"Loaded from cache: {audio_file.name}")
                    results.append(analysis)
                    continue
                except Exception:
                    pass  # Fall through to re-analysis
            
            try:
                print(f"Analyzing: {audio_file.name}")
                analysis = analyze_audio(str(audio_file), duration=max_duration, **kwargs)
                results.append(analysis)
                
                # Save to cache
                analysis.to_json(str(cache_file))
                
            except Exception as e:
                print(f"Error analyzing {audio_file.name}: {e}")
                continue
        
        self.results = results
        return results
    
    def discover_patterns(self, min_occurrences: int = 3) -> CatalogInsights:
        """
        Discover patterns and generate insights across the catalog.
        
        Args:
            min_occurrences: Minimum occurrences for a pattern to be reported
            
        Returns:
            CatalogInsights object with discovered patterns
        """
        if not self.results:
            raise ValueError("No analysis results. Call process_all() first.")
        
        # Aggregate statistics
        all_sets: Counter = Counter()
        all_names: Counter = Counter()
        all_cardinalities: Counter()
        all_moments = 0
        cardinalities = []
        
        for result in self.results:
            all_moments += len(result.moments)
            
            for moment in result.moments:
                if moment.forte_number:
                    all_sets[moment.forte_number] += 1
                if moment.common_name:
                    all_names[moment.common_name] += 1
                if moment.pitch_classes:
                    cardinalities.append(len(moment.pitch_classes))
        
        # Convert Counter to regular dict for dataclass
        set_distribution = dict(all_sets)
        cardinality_distribution = dict(Counter(cardinalities))
        
        # Calculate top sets
        top_sets = all_sets.most_common(20)
        most_common_names = all_names.most_common(20)
        
        # Find unique set classes
        unique_sets = set(all_sets.keys())
        
        # Calculate average cardinality
        avg_cardinality = sum(cardinalities) / len(cardinalities) if cardinalities else 0.0
        
        # Find Z-relation pairs in the catalog
        from .common_sets import get_z_partners, get_all_z_pairs
        z_relation_pairs: List[Tuple[str, str, int]] = []
        
        all_z_pairs = get_all_z_pairs()
        for pair_a, pair_b in all_z_pairs:
            count_a = set_distribution.get(pair_a, 0)
            count_b = set_distribution.get(pair_b, 0)
            if count_a > 0 and count_b > 0:
                total_count = sum(1 for r in self.results 
                                for m in r.moments 
                                if m.forte_number in (pair_a, pair_b))
                if total_count >= min_occurrences:
                    z_relation_pairs.append((pair_a, pair_b, total_count))
        
        # Sort Z-pairs by occurrence count
        z_relation_pairs.sort(key=lambda x: x[2], reverse=True)
        
        self.insights = CatalogInsights(
            total_tracks=len(self.results),
            total_moments=all_moments,
            unique_sets=unique_sets,
            top_sets=top_sets,
            average_cardinality=avg_cardinality,
            set_distribution=set_distribution,
            cardinality_distribution=cardinality_distribution,
            most_common_names=most_common_names,
            z_relation_pairs=z_relation_pairs[:10]  # Top 10 Z-pairs
        )
        
        return self.insights
    
    def find_similar_tracks(
        self,
        target_set: str,
        tolerance: int = 0
    ) -> List[Tuple[str, float]]:
        """
        Find tracks similar to a target set class.
        
        Args:
            target_set: Forte number or common name to search for
            tolerance: Allow up to this many interval differences
            
        Returns:
            List of (track_name, similarity_score) tuples
        """
        # Resolve target to forte number
        from .common_sets import get_common_set, get_set_by_name
        
        # Check if target_set is a valid forte number
        set_info = get_common_set(target_set)
        if set_info:
            target_forte = target_set
        else:
            # Try to look up by common name
            result = get_set_by_name(target_set)
            if result:
                target_forte = result[0]
            else:
                raise ValueError(f"Unknown set: {target_set}")
        
        similarities = []
        for result in self.results:
            score = 0
            for moment in result.moments:
                if moment.forte_number == target_forte:
                    score += 1
            
            if score > 0:
                similarities.append((result.file_path, score))
        
        # Sort by score
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    
    def export_to_csv(self, path: str) -> None:
        """
        Export analysis results to CSV format.
        
        Args:
            path: Output CSV file path
        """
        import csv
        
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'file', 'duration', 'total_moments', 'unique_sets',
                'avg_cardinality', 'top_set_1', 'top_set_1_count',
                'top_set_2', 'top_set_2_count', 'top_set_3', 'top_set_3_count'
            ])
            
            for result in self.results:
                row = [
                    result.file_path,
                    f"{result.duration:.2f}",
                    len(result.moments),
                    result.unique_sets,
                    f"{result.average_cardinality:.2f}"
                ]
                
                # Add top 3 sets
                for forte, count in result.top_sets[:3]:
                    row.extend([forte, count])
                
                writer.writerow(row)
    
    def save_results(self, path: str, include_moments: bool = False) -> None:
        """
        Save all analysis results to a single JSON file.
        
        Args:
            path: Output JSON file path
            include_moments: Whether to include detailed moment data
        """
        data = {
            'catalog_directory': str(self.directory),
            'analyzed_at': datetime.now().isoformat(),
            'total_tracks': len(self.results),
            'tracks': []
        }
        
        for result in self.results:
            track_data = {
                'file_path': result.file_path,
                'duration': result.duration,
                'unique_sets': result.unique_sets,
                'average_cardinality': result.average_cardinality,
                'top_sets': [{'forte_number': f, 'count': c} for f, c in result.top_sets]
            }
            
            if include_moments:
                track_data['moments'] = [m.to_dict() for m in result.moments]
            
            data['tracks'].append(track_data)
        
        if self.insights:
            data['insights'] = self.insights.to_dict()
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_results(self, path: str) -> None:
        """
        Load previously saved results.
        
        Args:
            path: Path to saved JSON file
        """
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.results = []
        for track_data in data['tracks']:
            # Reconstruct TrackAnalysis objects
            moments = []
            if 'moments' in track_data:
                from .audio import HarmonicMoment
                for m_data in track_data['moments']:
                    moment = HarmonicMoment(
                        timestamp=m_data['timestamp'],
                        pitch_classes=m_data['pitch_classes'],
                        forte_number=m_data.get('forte_number'),
                        common_name=m_data.get('common_name'),
                        interval_vector=tuple(m_data['interval_vector']) if m_data.get('interval_vector') else None
                    )
                    moments.append(moment)
            
            analysis = TrackAnalysis(
                file_path=track_data['file_path'],
                duration=track_data['duration'],
                moments=moments,
                top_sets=[(t['forte_number'], t['count']) for t in track_data['top_sets']],
                average_cardinality=track_data['average_cardinality'],
                unique_sets=track_data['unique_sets']
            )
            self.results.append(analysis)
        
        if 'insights' in data:
            self.insights = CatalogInsights.from_dict(data['insights'])