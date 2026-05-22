# PC-Set Project Roadmap

## Vision
A comprehensive toolkit for experimental musicians, composers, and music theorists to analyze, generate, and understand harmonic content through pitch class set theory.

---

## Phase 1: Core Library ✅ (Complete)
- [x] PCSet class with transpose, invert, prime_form, interval_vector
- [x] Forte number classification
- [x] Z-relation detection
- [x] Common set names (40+ triads, 7ths, scales)
- [x] Search and analysis tools
- [x] Comprehensive test suite (44 tests)

**Status:** ✅ Released v0.1.0

---

## Phase 2: Catalog Analysis Tools (Next Steps)

### 2A: Audio Analysis Pipeline
**Goal:** Analyze harmonic content of existing audio files (WAV, MP3, FLAC)

```python
# Example: Analyze a single track
from pc_set.audio import analyze_audio

results = analyze_audio("track.wav", duration=60)
print(f"Found {len(results['moments'])} harmonic moments")
print(f"Most common set: {results['top_set']}")

# Example: Batch process entire catalog
from pc_set.catalog import CatalogAnalyzer

analyzer = CatalogAnalyzer("/path/to/tracks")
analyzer.process_all()
analyzer.save_results("catalog_analysis.json")

# Discover patterns
insights = analyzer.discover_patterns()
print(insights.summary())
```

**Features:**
- [ ] Chroma feature extraction (LibROSA backend)
- [ ] Pitch class detection from audio
- [ ] Batch processing for multiple tracks
- [ ] JSON/CSV export for further analysis
- [ ] Pattern discovery (most common sets, similarities between tracks)

**Use Cases:**
- Analyze your label's entire catalog
- Discover "label sound" characteristics
- Find harmonic similarities between artists
- Generate insights for liner notes, blog posts

### 2B: MIDI Integration
**Goal:** Generate and export MIDI from set theory concepts

```python
from pc_set.midi import Composer, generate_midi

# Generate melody from set class
composer = Composer()
composer.set_row([0, 4, 7, 10])  # Dominant 7th
composer.generate_variations(n=4, technique="Z-relation")
composer.save_midi("composition.mid")

# Export twelve-tone row with variations
from twelve_tone import Composer as TTComposer
tt = TTComposer()
tt.compose(top_row=[0, 1, 4, 5, 7, 8, 9, 11, 2, 3, 6, 10])
tt.export_midi("row.mid", format="matrix")
```

**Features:**
- [ ] MIDI file generation from PCSet
- [ ] Integration with twelve-tone package
- [ ] Multiple output formats ( melody, matrix, arpeggiation)
- [ ] Tempo and velocity mapping
- [ ] Multi-track export (different row forms per track)

**Use Cases:**
- Generate compositional sketches
- Create variations on a row
- Export to DAW for further production
- Generative composition systems

---

## Phase 3: Real-Time & Live Performance

### 3A: Audio Processing (Python-based)
**Goal:** Real-time audio effects controlled by set theory

```python
from pc_set.live import AudioProcessor, SetBasedFX

processor = AudioProcessor()

# Map set classes to effects
@processor.on_set_detect
def handle_set(pcset, audio_buffer):
    if pcset.common_name() == "Diminished Seventh":
        return apply_distortion(audio_buffer, drive=0.8)
    elif "Pentatonic" in pcset.common_name():
        return apply_reverb(audio_buffer, room_size=0.9)
    return audio_buffer

processor.start()
```

**Features:**
- [ ] Real-time pitch detection (SoundDevice backend)
- [ ] Set class analysis on audio buffers
- [ ] Effect parameter mapping based on set content
- [ ] Low-latency processing (~10-50ms)

**Use Cases:**
- Live performance processing
- Interactive installations
- Generative sound design

### 3B: SuperCollider Integration (Optional)
**Goal:** Hybrid Python + SuperCollider for sample-accurate synthesis

```python
from pc_set.supercollider import SCClient

sc = SCClient()
sc.send_set_class([0, 4, 7], synth_id="poly_synth")
sc.trigger_pattern("Z-relation-variation")
```

**Features:**
- [ ] OSC communication with SuperCollider
- [ ] Pre-built SynthDefs for common synthesis tasks
- [ ] Parameter mapping from set analysis
- [ ] Network transparency (remote synthesis)

**Use Cases:**
- When sample-accurate timing is critical
- Complex synthesis architectures
- Networked music performance

---

## Phase 4: Visualization & Education

### 4A: Interactive Visualizations
**Goal:** Visual representation of set relationships

```python
from pc_set.viz import plot_set_space, animate_progression

# Static visualization
plot_set_space(tracks=catalog, color_by="artist")

# Animate chord progression
animate_progression("track.wav", output="progression.mp4")

# 3D interval vector space
from pc_set.viz import plot_interval_space
plot_interval_space(catalog_analysis)
```

**Features:**
- [ ] Interval vector scatter plots (Plotly backend)
- [ ] Chord progression animations
- [ ] Set class relationship graphs
- [ ] Export to video/GIF for social media

**Use Cases:**
- Educational content
- Album artwork / visuals
- Social media content
- Workshop materials

### 4B: Educational Tools
**Goal:** Teach set theory through interactive examples

```python
from pc_set.edu import Quiz, InteractiveDemo

# Generate quiz questions
quiz = Quiz(difficulty="intermediate", topic="Z-relations")
quiz.generate(n=10)
quiz.export("quiz.json")

# Interactive demo
demo = InteractiveDemo(topic="prime_form")
demo.create_web_app()
```

**Features:**
- [ ] Quiz generation (identify set classes by ear/sight)
- [ ] Interactive web demos
- [ ] Worksheet generation (PDF export)
- [ ] Video tutorial scripts

**Use Cases:**
- Label workshops
- University courses
- Self-study
- Blog content

---

## Phase 5: Advanced Applications

### 5A: Generative Composition Engine
**Goal:** Autonomous composition using set theory constraints

```python
from pc_set.generate import GenerativeComposer

composer = GenerativeComposer(
    constraints={
        "allowed_sets": ["3-11", "3-12", "4-21"],
        "progression_rules": "common_tone",
        "density": "sparse"
    }
)

composition = composer.generate(duration=120)
composition.export_midi("generated.mid")
composition.export_score("generated.pdf")  # via LilyPond
```

**Features:**
- [ ] Constraint-based composition
- [ ] Style emulation (analyze artist, generate in their style)
- [ ] Multi-voice counterpoint
- [ ] Export to MIDI, MusicXML, LilyPond

### 5B: Machine Learning Integration
**Goal:** Use ML to discover new set-theoretic patterns

```python
from pc_set.ml import ClusterAnalyzer, StylePredictor

# Cluster tracks by harmonic content
clusterer = ClusterAnalyzer(catalog_analysis)
clusters = clusterer.find_clusters(n=5)

# Predict artist/label from harmonic content
predictor = StylePredictor()
predictor.train(catalog_analysis)
prediction = predictor.predict(new_track)
```

**Features:**
- [ ] Clustering by interval vector similarity
- [ ] Artist/label classification
- [ ] Anomaly detection (find outliers in catalog)
- [ ] Recommendation system ("if you like this set, try...")

---

## Phase 6: Integration & Ecosystem

### 6A: DAW Plugins
**Goal:** VST/AU plugins for common DAWs

- [ ] VST3 plugin (Python-based via JUCE wrapper)
- [ ] Ableton Live Max for Live devices
- [ ] Reaper JSFX scripts
- [ ] Logic Pro scripter plugins

### 6B: Web Application
**Goal:** Browser-based analysis and composition

- [ ] Upload audio → get harmonic analysis
- [ ] Interactive set class explorer
- [ ] Composition tool (generate MIDI from browser)
- [ ] Collaborative features (share analyses)

### 6C: Integration with Existing Tools
- [ ] Music21 bridge (import/export)
- [ ] Sonic Visualiser plugin
- [ ] Praat integration (for vocal analysis)
- [ ] Max/MSP externals

---

## Immediate Next Steps (Pick One)

### Option 1: Catalog Analyzer (Recommended First Project)
**Time:** 2-3 days to MVP
**Output:** JSON analysis of your entire label catalog
**Impact:** Immediate insights into your label's sound

Tasks:
1. Add LibROSA dependency
2. Implement `analyze_audio()` function
3. Batch processing script
4. Pattern discovery algorithms
5. Export to JSON/CSV

### Option 2: MIDI Generator
**Time:** 1-2 days to MVP
**Output:** MIDI files from set theory concepts
**Impact:** New compositional tool for your work

Tasks:
1. Add mido dependency (already in twelve-tone!)
2. Implement PCSet → MIDI conversion
3. Generate variations (transpose, invert, Z-relations)
4. Export standard MIDI files

### Option 3: Pattern Discovery Script
**Time:** 1 day to MVP
**Output:** Report on harmonic patterns in your catalog
**Impact:** Content for blog, workshops, label identity

Tasks:
1. Process existing audio files (if you have them)
2. Or: analyze MIDI exports from your DAW
3. Statistical analysis (most common sets, etc.)
4. Generate human-readable report

---

## How to Use This Roadmap

1. **Pick one item** from "Immediate Next Steps"
2. **Implement it** (I can help scaffold the code)
3. **Test it** on your actual music/catalog
4. **Iterate** based on what you learn
5. **Move to next item** or dive deeper into current one

## Contributing

This is a living document. As you use pc-set in your work, update this with:
- New use cases you discover
- Features you need
- Patterns you find in your catalog

## License & Open Source

- Core library: BSD 2-Clause (permissive, commercial-friendly)
- Documentation: CC BY-SA 4.0
- Example compositions: Your choice

---

**Last Updated:** 2026-05-21
**Version:** 0.1.0 (Initial roadmap)
