import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

STEM_ORDER = ["vocals", "guitar", "piano", "bass", "drums", "other"]
PITCH_STEMS = {"vocals", "bass"}  # монофонические — pyin имеет смысл


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="jamal",
        description="Разложить MP3 на stems и визуализировать хромаграммы + piano roll",
    )
    parser.add_argument("audio", type=Path, help="Путь к MP3-файлу")
    args = parser.parse_args()

    audio_path: Path = args.audio.resolve()
    if not audio_path.exists():
        console.print(f"[bold red]Файл не найден:[/bold red] {audio_path}")
        sys.exit(1)

    output_dir = audio_path.parent / audio_path.stem
    console.print(
        Panel(
            f"[bold cyan]{audio_path.name}[/bold cyan]\n"
            f"Вывод: [dim]{output_dir}[/dim]",
            title="[bold magenta]jamal[/bold magenta]",
            expand=False,
        )
    )

    from jamal.separate import separate
    from jamal.extract import extract_chroma, extract_cqt, extract_pitch
    from jamal.visualize import plot_chroma, plot_piano_roll, plot_pitch_overlay
    from jamal.compose import compose

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]Разделение на stems (Demucs)...", total=None)
        stem_paths = separate(audio_path, output_dir)
        progress.update(task, description="[green]Stems готовы", completed=True)

    png_paths: list[Path] = []
    ordered_stems = [s for s in STEM_ORDER if s in stem_paths]

    for name in ordered_stems:
        wav_path = stem_paths[name]
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Визуализация:[/cyan] {name}", total=None)

            chroma, sr, hop = extract_chroma(wav_path)
            chroma_png = output_dir / f"{name}_chroma.png"
            plot_chroma(chroma, name, chroma_png, sr, hop)
            png_paths.append(chroma_png)

            cqt_db, _, _ = extract_cqt(wav_path)

            if name in PITCH_STEMS:
                f0, voiced_flag, _, _ = extract_pitch(wav_path)
                pitch_png = output_dir / f"{name}_pitch.png"
                plot_pitch_overlay(cqt_db, f0, voiced_flag, name, pitch_png, sr, hop)
                png_paths.append(pitch_png)
                progress.update(task, description=f"[green]Сохранено:[/green] {name}_chroma + _pitch")
            else:
                roll_png = output_dir / f"{name}_roll.png"
                plot_piano_roll(cqt_db, name, roll_png, sr, hop)
                png_paths.append(roll_png)
                progress.update(task, description=f"[green]Сохранено:[/green] {name}_chroma + _roll")

    combined_path = output_dir / "combined.png"
    console.print("[yellow]Сборка итоговой картинки...[/yellow]")
    compose(png_paths, combined_path, title=audio_path.stem)
    console.print(f"[bold green]Готово![/bold green] {combined_path}")


if __name__ == "__main__":
    main()
