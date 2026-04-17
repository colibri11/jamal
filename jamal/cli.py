import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

STEM_ORDER = ["vocals", "drums", "bass", "other"]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="jamal",
        description="Разложить MP3 на stems и визуализировать хромаграммы",
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
    from jamal.extract import extract_chroma
    from jamal.visualize import plot_chroma
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
            task = progress.add_task(f"[cyan]Хромаграмма:[/cyan] {name}", total=None)
            chroma, sr, hop_length = extract_chroma(wav_path)
            png_path = output_dir / f"{name}.png"
            plot_chroma(chroma, name, png_path, sr, hop_length)
            png_paths.append(png_path)
            progress.update(task, description=f"[green]Сохранено:[/green] {png_path.name}")

    combined_path = output_dir / "combined.png"
    console.print("[yellow]Сборка итоговой картинки...[/yellow]")
    compose(png_paths, combined_path, title=audio_path.stem)
    console.print(f"[bold green]Готово![/bold green] {combined_path}")


if __name__ == "__main__":
    main()
