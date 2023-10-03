import rich


def info(message: str) -> None:
    """Logs an information to the standard output."""
    rich.print(f"[bold][blue]INFO[/] {message}")


def warn(message: str) -> None:
    """Logs a warning to the standard output."""
    rich.print(f"[bold][yellow]WARN[/] {message}")


def error(message: str) -> None:
    """Logs an error to the standard output."""
    rich.print(f"[bold][red]ERROR[/] {message}")
