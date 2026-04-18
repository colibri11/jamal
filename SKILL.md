---
name: jamal
description: Analyze an audio file (MP3/WAV) using jamal — stem separation, chromagram, piano roll, and pitch visualization. Use when the user wants to analyze music, understand its structure, evaluate it aesthetically, or compare tracks.
metadata:
  openclaw:
    emoji: "🎹"
    requires:
      bins: ["uv"]
---

You are analyzing an audio file using the `jamal` tool. Follow these steps precisely.

## Step 1 — Get the file path

If the user did not provide a path, ask for it. Accept MP3 or WAV files.

## Step 2 — Run jamal

**Claude Code:**
```bash
cd ${CLAUDE_SKILL_DIR} && uv run jamal <path_to_file>
```

**OpenClaw:**
```bash
{baseDir}/scripts/analyze.sh <path_to_file>
```

The script runs directly from the skill directory — no separate installation step required.

Wait for completion. It takes 2–5 minutes on CPU (Demucs separation is the slow part). Keep the user informed with a brief status message.

## Step 3 — Locate the output

Output is saved to a folder named after the audio file, in the same directory as the file. For example:
`/path/to/Song_Name/`

It contains:
| File | What it shows |
|------|--------------|
| `vocals_chroma.png` | 12 pitch classes over time — harmonic colour |
| `vocals_pitch.png` | CQT heatmap + cyan pitch line (exact note, octave, vibrato) |
| `bass_chroma.png` | harmonic content of bass |
| `bass_pitch.png` | CQT + pitch line for bass (pedal tones, bass line) |
| `guitar_chroma.png` | harmonic colour of guitar |
| `guitar_roll.png` | CQT piano roll — register, density |
| `piano_chroma.png` | harmonic colour of piano |
| `piano_roll.png` | CQT piano roll |
| `other_chroma.png` | everything else |
| `other_roll.png` | CQT piano roll for residual |
| `combined.png` | all of the above stacked vertically |

Stems not present (RMS below threshold) are skipped automatically — the instrument is absent or inaudible in the track.

## Step 4 — View and analyze each image

Use the Read tool to view each PNG. Analyze in this order:

### vocals_pitch.png (if present)
- **Pitch line (cyan)**: trace the melodic contour. Note the octave range (Y-axis labels: C1–B7), vibrato (wavy line), glissando (smooth curves between notes), breaks (silences).
- **Tessitura**: where does most of the singing concentrate? (e.g., F3–A3 = low tenor/baritone)
- **Range**: distance between lowest and highest voiced note in semitones
- **Climax**: does the line rise significantly toward the end? By how much?
- **CQT background**: the heatmap shows all harmonics. Bright areas above the pitch line are overtones, not separate notes.

### bass_pitch.png (if present)
- Look for pedal tones (flat horizontal line) vs active bass lines
- Note the octave — most bass lines live in C1–C3

### guitar_roll.png / piano_roll.png
- Note which octaves are active (Y-axis)
- Dense/bright zones = sustained chords or repeated patterns
- Gaps = rests or sparse playing

### *_chroma.png files
- Bright rows = frequently occurring pitch classes → reveals the key and mode
- Sustained brightness = drone or pedal harmony
- Rapid changes = complex harmony or chromatic movement

## Step 5 — Aesthetic evaluation

After analysis, provide:

1. **Structure**: how the track is built (sections visible as vertical patterns, silences, density changes)
2. **Voice/instrument character**: what kind of voice/playing is this? Register, technique, expressiveness
3. **Harmonic language**: what pitch classes dominate? What mode or tonal center?
4. **Emotional arc**: how does energy/register/density evolve over time?
5. **Aesthetic impression**: describe what the visualizations convey beyond the technical — texture, colour, tension, release

Be direct and specific. Refer to exact timestamps and note names when possible. This is not a summary — it is an analysis that should reveal something non-obvious.

## Notes

- pyin pitch detection (used for vocals and bass) works only for monophonic signals. For guitar/piano, only the CQT heatmap is reliable — the pitch line is absent by design.
- The chromagram collapses all octaves into 12 classes — use it for harmony, not register.
- The CQT piano roll preserves register — use it for pitch height and range.
- Silences (black vertical bands) are meaningful: they reveal phrasing, breathing, song structure.
