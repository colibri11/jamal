from pathlib import Path

import torch
import torchaudio
from demucs.apply import apply_model
from demucs.audio import save_audio
from demucs.pretrained import get_model


def separate(audio_path: Path, output_dir: Path) -> dict[str, Path]:
    model = get_model("htdemucs")
    model.eval()

    wav, sr = torchaudio.load(audio_path)

    if sr != model.samplerate:
        wav = torchaudio.functional.resample(wav, sr, model.samplerate)

    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)

    ref = wav.mean(0)
    wav = (wav - ref.mean()) / ref.std()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    sources = apply_model(model, wav[None], device=device, progress=True)[0]
    sources = sources * ref.std() + ref.mean()

    output_dir.mkdir(parents=True, exist_ok=True)
    stem_paths: dict[str, Path] = {}
    for source, name in zip(sources, model.sources):
        path = output_dir / f"{name}.wav"
        save_audio(source, str(path), model.samplerate)
        stem_paths[name] = path

    return stem_paths
