from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model

MODEL_NAME = "htdemucs_6s"
SHIFTS = 4
RMS_THRESHOLD = 0.01  # стемы тише этого порога считаются пустыми


def separate(audio_path: Path, output_dir: Path) -> dict[str, Path]:
    model = get_model(MODEL_NAME)
    model.eval()

    y, _ = librosa.load(str(audio_path), sr=model.samplerate, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    wav = torch.from_numpy(y).float()

    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)

    ref = wav.mean(0)
    wav = (wav - ref.mean()) / ref.std()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    sources = apply_model(
        model, wav[None], device=device, shifts=SHIFTS, progress=True
    )[0]
    sources = sources * ref.std() + ref.mean()

    output_dir.mkdir(parents=True, exist_ok=True)
    stem_paths: dict[str, Path] = {}
    for source, name in zip(sources, model.sources):
        rms = float(source.pow(2).mean().sqrt())
        if rms < RMS_THRESHOLD:
            continue
        path = output_dir / f"{name}.wav"
        audio_np = source.numpy().T  # (samples, channels)
        sf.write(str(path), audio_np, model.samplerate)
        stem_paths[name] = path

    return stem_paths
