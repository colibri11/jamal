# jamal

Audio analysis tool for AI agents. Separates an MP3 into stems, extracts chromatic and pitch features, and produces visualizations that a vision-capable model can read and reason about.

## What it does

1. **Separates** the track into up to 6 stems using Demucs `htdemucs_6s`: vocals, guitar, piano, bass, drums, other
2. **Filters** stems below an RMS threshold — absent instruments produce no output
3. **Extracts** per-stem chromagram (12 pitch classes) and CQT piano roll (C1–B7, full octave resolution)
4. **Detects pitch** (pyin) for monophonic stems (vocals, bass) — produces a cyan melodic contour line overlaid on the piano roll
5. **Composes** all images into a single `combined.png`

## Output

For a file `Song.mp3`, output goes to `Song/` in the same directory:

```
Song/
├── vocals_chroma.png   # 12 pitch classes, no octave — harmonic colour
├── vocals_pitch.png    # CQT heatmap + pitch line (note + octave + vibrato)
├── guitar_chroma.png
├── guitar_roll.png     # CQT piano roll, C1–B7
├── piano_chroma.png
├── piano_roll.png
├── bass_chroma.png
├── bass_pitch.png      # CQT + bass line pitch
├── other_chroma.png
├── other_roll.png
└── combined.png        # all images stacked vertically
```

Stems not detected (RMS < 0.01) are skipped silently.

## Installation

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone <repo>
cd jamal
uv sync
```

First run downloads the Demucs model weights (~52 MB, cached in `~/.cache/torch/`).

## Usage

```bash
uv run jamal /path/to/track.mp3
```

## Runtime requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU cores (physical) | 8 | 16 |
| RAM | 8 GB | 16 GB |
| Disk (models + cache) | 2 GB | 5 GB |
| GPU | not required | speeds up Demucs 4–6× |

Processing time per 5-minute track (CPU only, no GPU):
- Modern Xeon (Skylake+): ~2–3 min
- Older Xeon (Broadwell): ~4–6 min
- Apple M-series: ~90–120 s

Results are not cached automatically. Re-running on the same file overwrites the output folder.

## Dependencies

| Package | Purpose |
|---------|---------|
| `demucs` | Stem separation (htdemucs_6s, shifts=4) |
| `librosa` | Chroma extraction, CQT, pyin pitch detection |
| `matplotlib` | Visualization |
| `Pillow` | Image composition |
| `soundfile` | WAV export |
| `rich` | Terminal output |

## Agent integration

A Claude Code skill is included at `.claude/skills/jamal.md`. Copy it to `~/.claude/skills/` (user-wide) or keep it in the project for project-level access.

Invoke with `/jamal` inside a Claude Code session. The skill instructs the agent to:
- run `uv run jamal <file>`
- view the output images
- perform structured musical and aesthetic analysis

## Model details

**Stem separation**: `htdemucs_6s` with `shifts=4` — 4-fold time-shift averaging for higher quality at the cost of ~4× inference time. RMS threshold 0.01 filters absent stems.

**Chromagram**: `chroma_cqt`, hop_length=512

**Piano roll**: CQT, C1–B7 (84 semitones), displayed with per-semitone Y-axis labels

**Pitch detection**: `pyin`, range C2–C7, applied only to monophonic stems (vocals, bass)
