from pathlib import Path

import librosa.display
import matplotlib.pyplot as plt
import numpy as np

STEM_COLORS = {
    "vocals": "#e63946",
    "drums": "#457b9d",
    "bass": "#2a9d8f",
    "other": "#e9c46a",
}

CHROMA_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def plot_chroma(
    chroma: np.ndarray,
    stem_name: str,
    output_path: Path,
    sr: int,
    hop_length: int,
) -> None:
    fig, ax = plt.subplots(figsize=(16, 4), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    color = STEM_COLORS.get(stem_name, "#ffffff")
    img = librosa.display.specshow(
        chroma,
        y_axis="chroma",
        x_axis="time",
        ax=ax,
        sr=sr,
        hop_length=hop_length,
        cmap="magma",
    )

    ax.set_title(stem_name.upper(), color=color, fontsize=16, fontweight="bold", pad=10)
    ax.set_xlabel("Время (сек)", color="#aaaaaa", fontsize=10)
    ax.set_ylabel("Нота", color="#aaaaaa", fontsize=10)
    ax.tick_params(colors="#aaaaaa")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")

    cbar = fig.colorbar(img, ax=ax, format="%.2f")
    cbar.ax.yaxis.set_tick_params(color="#aaaaaa")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#aaaaaa")

    plt.tight_layout(pad=1.5)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
