from pathlib import Path

import librosa
import numpy as np

N_OCTAVES = 7        # C1–B7
FMIN = librosa.note_to_hz("C1")


def extract_chroma(audio_path: Path) -> tuple[np.ndarray, int, int]:
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    hop_length = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    return chroma, sr, hop_length


def extract_pitch(audio_path: Path) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Возвращает (f0_hz, voiced_flag, sr, hop_length) через pyin."""
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    hop_length = 512
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        hop_length=hop_length,
    )
    return f0, voiced_flag, sr, hop_length


def extract_cqt(audio_path: Path) -> tuple[np.ndarray, int, int]:
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    hop_length = 512
    C = np.abs(librosa.cqt(
        y=y, sr=sr, hop_length=hop_length,
        fmin=FMIN, n_bins=N_OCTAVES * 12, bins_per_octave=12,
    ))
    C_db = librosa.amplitude_to_db(C, ref=np.max)
    return C_db, sr, hop_length
