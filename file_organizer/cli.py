# file_organizer/cli.py
import typer
from pathlib import Path
from rich.console import Console
from datetime import datetime

app = typer.Typer()
console = Console()


def organize_by_extension(
    path: Path,
    dry_run: bool = False,
    recursive: bool = False,
    ext_template: str = "{ext}",
):
    """Organizes files in the given path by their extension."""
    console.print(
        f"\n[bold cyan]Organizing {path} by file extension...[/bold cyan]"
    )

    items = path.rglob("*") if recursive else path.iterdir()
    for item in items:
        if not item.is_file() or item.name.startswith("."):
            continue

        extension = item.suffix.lower()
        if not extension:
            console.print(
                f"[yellow]Skipping '{item.name}' (no extension)[/yellow]"
            )
            continue

        dest_dir_name = ext_template.format(ext=extension[1:])
        dest_dir = path / dest_dir_name

        if dry_run:
            console.print(
                f"[yellow][DRY RUN] Would move '{item.name}' to "
                f"'{dest_dir.name}/'[/yellow]"
            )
            continue

        dest_dir.mkdir(exist_ok=True)
        try:
            dest_path = dest_dir / item.name
            item.rename(dest_path)
            console.print(
                f"[green]Moved '{item.name}' to '{dest_dir.name}/'[/green]"
            )
        except Exception as e:  # noqa: F841
            console.print(
                f"[bold red]Error moving '{item.name}': {{e}}[/bold red]"
            )


def organize_by_date(
    path: Path,
    dry_run: bool = False,
    recursive: bool = False,
    date_template: str = "{YYYY}-{MM}-{DD}",
):
    """Organizes files in the given path by their modification date."""
    console.print(f"\n[bold cyan]Organizing {path} by date...[/bold cyan]")

    items = path.rglob("*") if recursive else path.iterdir()
    for item in items:
        if not item.is_file() or item.name.startswith("."):
            continue

        m_time = item.stat().st_mtime
        dt_object = datetime.fromtimestamp(m_time)
        dest_dir_name = date_template.format(
            YYYY=dt_object.year,
            MM=f"{dt_object.month:02}",
            DD=f"{dt_object.day:02}",
        )
        dest_dir = path / dest_dir_name

        if dry_run:
            console.print(
                f"[yellow][DRY RUN] Would move '{item.name}' to "
                f"'{dest_dir.name}/'[/yellow]"
            )
            continue

        dest_dir.mkdir(exist_ok=True)
        try:
            dest_path = dest_dir / item.name
            item.rename(dest_path)
            console.print(
                f"[green]Moved '{item.name}' to '{dest_dir.name}/'[/green]"
            )
        except Exception as e:  # noqa: F841
            console.print(
                f"[bold red]Error moving '{item.name}': {{e}}[/bold red]"
            )


def organize_by_size(
    path: Path,
    dry_run: bool = False,
    recursive: bool = False,
    size_template: str = "{size}",
):
    """Organizes files in the given path by their size."""
    console.print(
        f"\n[bold cyan]Organizing {path} by file size...[/bold cyan]"
    )

    size_map = {
        "Tiny": (0, 1_024),  # < 1 KB
        "Small": (1_024, 1_048_576),  # 1 KB - 1 MB
        "Medium": (1_048_576, 134_217_728),  # 1 MB - 128 MB
        "Large": (134_217_728, 1_073_741_824),  # 128 MB - 1 GB
        "Huge": (1_073_741_824, float("inf")),  # > 1 GB
    }

    items = path.rglob("*") if recursive else path.iterdir()
    for item in items:
        if not item.is_file() or item.name.startswith("."):
            continue

        size = item.stat().st_size
        dest_folder_name = "Unknown"
        for name, (min_size, max_size) in size_map.items():
            if min_size <= size < max_size:
                dest_folder_name = name
                break

        dest_dir_name = size_template.format(size=dest_folder_name)
        dest_dir = path / dest_dir_name

        if dry_run:
            console.print(
                f"[yellow][DRY RUN] Would move '{item.name}' to "
                f"'{dest_dir.name}/'[/yellow]"
            )
            continue

        dest_dir.mkdir(exist_ok=True)
        try:
            dest_path = dest_dir / item.name
            item.rename(dest_path)
            console.print(
                f"[green]Moved '{item.name}' to '{dest_dir.name}/'[/green]"
            )
        except Exception as e:  # noqa: F841
            console.print(
                f"[bold red]Error moving '{item.name}': {{e}}[/bold red]"
            )


@app.command()
def main(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
        help="The directory path to organize.",
    ),
    by_extension: bool = typer.Option(
        False, "--by-extension", "-e", help="Organize files by extension."
    ),
    by_date: bool = typer.Option(
        False, "--by-date", "-d", help="Organize files by modification date."
    ),
    by_size: bool = typer.Option(
        False, "--by-size", "-s", help="Organize files by size."
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Organize files recursively."
    ),
    ext_template: str = typer.Option(
        "{ext}",
        "--ext-template",
        help="Template for extension-based folder names.",
    ),
    date_template: str = typer.Option(
        "{YYYY}-{MM}-{DD}",
        "--date-template",
        help="Template for date-based folder names.",
    ),
    size_template: str = typer.Option(
        "{size}",
        "--size-template",
        help="Template for size-based folder names.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what changes would be made without moving files.",
    ),
):
    """
    A powerful and configurable CLI tool to organize your files effortlessly.
    """
    if not any([by_extension, by_date, by_size]):
        console.print(
            "[bold yellow]No organization mode selected. "
            "Please specify an option like --by-extension, --by-date, "
            "or --by-size.[/bold yellow]"
        )
        raise typer.Exit()

    if by_extension:
        organize_by_extension(path, dry_run, recursive, ext_template)
    if by_date:
        organize_by_date(path, dry_run, recursive, date_template)
    if by_size:
        organize_by_size(path, dry_run, recursive, size_template)

    if not dry_run:
        console.print("\n[bold green]✨ Organization complete! ✨[/bold green]")


if __name__ == "__main__":
    app()
