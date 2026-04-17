from pathlib import Path

import librosa
import numpy as np


def extract_chroma(audio_path: Path) -> tuple[np.ndarray, int, int]:
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    hop_length = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    return chroma, sr, hop_length
