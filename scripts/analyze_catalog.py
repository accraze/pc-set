#!/usr/bin/env python3
"""
Catalog Analyzer CLI

Analyze a music catalog and discover harmonic patterns using pitch class set theory.

Usage:
    python scripts/analyze_catalog.py /path/to/music
    python scripts/analyze_catalog.py /path/to/music --max-duration 30
    python scripts/analyze_catalog.py /path/to/music --output results.json
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pc_set.catalog import CatalogAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a music catalog for harmonic patterns using pitch class set theory."
    )
    parser.add_argument(
        "directory",
        help="Path to directory containing audio files"
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=None,
        help="Maximum duration per track in seconds (for faster analysis)"
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=['.wav', '.mp3', '.flac', '.m4a', '.ogg'],
        help="Audio file extensions to process (default: wav mp3 flac m4a ogg)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output JSON file for results (default: catalog_analysis.json)"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Also export results to CSV"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Don't use cached analysis results"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)
    
    # Default output path
    output_path = args.output or str(directory / "catalog_analysis.json")
    
    print(f"Analyzing catalog: {directory}")
    print(f"File extensions: {', '.join(args.extensions)}")
    if args.max_duration:
        print(f"Max duration per track: {args.max_duration}s")
    print()
    
    # Create analyzer
    analyzer = CatalogAnalyzer(str(directory))
    
    # Process all files
    try:
        analyzer.process_all(
            extensions=tuple(args.extensions),
            max_duration=args.max_duration,
            use_cache=not args.no_cache
        )
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    
    if not analyzer.results:
        print("No audio files found to analyze.")
        sys.exit(1)
    
    print(f"\nProcessed {len(analyzer.results)} tracks.\n")
    
    # Discover patterns
    insights = analyzer.discover_patterns()
    
    # Print summary
    print(insights.summary())
    
    # Save results
    print(f"\nSaving results to: {output_path}")
    analyzer.save_results(output_path, include_moments=False)
    
    # Export CSV if requested
    if args.csv:
        csv_path = output_path.replace('.json', '.csv')
        print(f"Exporting to CSV: {csv_path}")
        analyzer.export_to_csv(csv_path)
    
    print("\nDone!")


if __name__ == "__main__":
    main()