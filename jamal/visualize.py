from pathlib import Path

import librosa.display
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

STEM_COLORS = {
    "vocals": "#e63946",
    "drums": "#457b9d",
    "bass": "#2a9d8f",
    "guitar": "#f4a261",
    "piano": "#a8dadc",
    "other": "#e9c46a",
}

BG_DARK = "#1a1a2e"
BG_PANEL = "#16213e"
TICK_COLOR = "#aaaaaa"
SPINE_COLOR = "#444444"

# Названия нот для piano roll (C1…B7)
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
PIANO_ROLL_LABELS = [
    f"{note}{octave}"
    for octave in range(1, 8)
    for note in _NOTE_NAMES
]  # C1, C#1, … B7


def _style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TICK_COLOR)
    for spine in ax.spines.values():
        spine.set_edgecolor(SPINE_COLOR)


def _add_colorbar(fig: plt.Figure, img, ax: plt.Axes) -> None:
    cbar = fig.colorbar(img, ax=ax, format="%.1f", pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=TICK_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TICK_COLOR, fontsize=8)


def plot_stem(
    chroma: np.ndarray,
    cqt_db: np.ndarray,
    stem_name: str,
    output_path: Path,
    sr: int,
    hop_length: int,
) -> None:
    color = STEM_COLORS.get(stem_name, "#ffffff")
    fig, (ax_chroma, ax_roll) = plt.subplots(
        1, 2,
        figsize=(24, 5),
        facecolor=BG_DARK,
        gridspec_kw={"width_ratios": [1, 1.4]},
    )

    # --- Хромаграмма (левая панель) ---
    _style_ax(ax_chroma)
    img_c = librosa.display.specshow(
        chroma, y_axis="chroma", x_axis="time",
        ax=ax_chroma, sr=sr, hop_length=hop_length, cmap="magma",
    )
    ax_chroma.set_title("Хромаграмма", color=color, fontsize=12, fontweight="bold")
    ax_chroma.set_xlabel("Время (сек)", color=TICK_COLOR, fontsize=9)
    ax_chroma.set_ylabel("Класс ноты", color=TICK_COLOR, fontsize=9)
    _add_colorbar(fig, img_c, ax_chroma)

    # --- Piano roll / CQT (правая панель) ---
    _style_ax(ax_roll)
    img_r = librosa.display.specshow(
        cqt_db, y_axis="cqt_note", x_axis="time",
        ax=ax_roll, sr=sr, hop_length=hop_length,
        fmin=librosa.note_to_hz("C1"), cmap="magma",
    )
    ax_roll.set_title("Piano roll (CQT)", color=color, fontsize=12, fontweight="bold")
    ax_roll.set_xlabel("Время (сек)", color=TICK_COLOR, fontsize=9)
    ax_roll.set_ylabel("Нота + октава", color=TICK_COLOR, fontsize=9)
    _add_colorbar(fig, img_r, ax_roll)

    fig.suptitle(stem_name.upper(), color=color, fontsize=18, fontweight="bold", y=1.02)
    plt.tight_layout(pad=1.5)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close(fig)
