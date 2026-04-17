from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
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

# Все 84 полутона C1–B7
_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ALL_NOTE_LABELS = [f"{n}{o}" for o in range(1, 8) for n in _NOTES]


def _style_ax(ax: plt.Axes) -> None:
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TICK_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(SPINE_COLOR)


def _add_colorbar(fig: plt.Figure, img, ax: plt.Axes) -> None:
    cbar = fig.colorbar(img, ax=ax, format="%.1f", pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=TICK_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TICK_COLOR, fontsize=8)


def plot_chroma(
    chroma: np.ndarray,
    stem_name: str,
    output_path: Path,
    sr: int,
    hop_length: int,
) -> None:
    color = STEM_COLORS.get(stem_name, "#ffffff")
    fig, ax = plt.subplots(figsize=(18, 4), facecolor=BG_DARK)
    _style_ax(ax)

    img = librosa.display.specshow(
        chroma, y_axis="chroma", x_axis="time",
        ax=ax, sr=sr, hop_length=hop_length, cmap="magma",
    )
    ax.set_title(f"{stem_name.upper()} — Хромаграмма", color=color, fontsize=13, fontweight="bold")
    ax.set_xlabel("Время (сек)", color=TICK_COLOR, fontsize=9)
    ax.set_ylabel("Класс ноты", color=TICK_COLOR, fontsize=9)
    _add_colorbar(fig, img, ax)

    plt.tight_layout(pad=1.5)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close(fig)


def plot_piano_roll(
    cqt_db: np.ndarray,
    stem_name: str,
    output_path: Path,
    sr: int,
    hop_length: int,
) -> None:
    color = STEM_COLORS.get(stem_name, "#ffffff")
    n_bins = cqt_db.shape[0]  # обычно 84

    # Высота: ~14px на полутон при dpi=150 → ~0.093 дюйма на строку
    fig_h = max(10, round(n_bins * 0.093))
    fig, ax = plt.subplots(figsize=(18, fig_h), facecolor=BG_DARK)
    _style_ax(ax)

    fmin = librosa.note_to_hz("C1")
    freqs = librosa.cqt_frequencies(n_bins=n_bins, fmin=fmin)

    img = librosa.display.specshow(
        cqt_db, y_axis="cqt_note", x_axis="time",
        ax=ax, sr=sr, hop_length=hop_length,
        fmin=fmin, cmap="magma",
    )
    ax.set_title(f"{stem_name.upper()} — Piano roll (CQT)", color=color, fontsize=13, fontweight="bold")
    ax.set_xlabel("Время (сек)", color=TICK_COLOR, fontsize=9)
    ax.set_ylabel("Нота + октава", color=TICK_COLOR, fontsize=9)

    # Подпись каждого полутона — позиции в Гц, как их видит librosa
    ax.set_yticks(freqs)
    ax.set_yticklabels(ALL_NOTE_LABELS[:n_bins], fontsize=7)

    # Горизонтальные линии на границах октав (каждые 12 полутонов = одна октава)
    for i in range(0, n_bins, 12):
        ax.axhline(y=freqs[i], color=SPINE_COLOR, linewidth=0.8, linestyle="--")

    _add_colorbar(fig, img, ax)

    plt.tight_layout(pad=1.5)
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close(fig)
