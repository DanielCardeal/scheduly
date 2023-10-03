import readline

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def log_info(message: str) -> None:
    """Logs an information to the standard output."""
    console.log(f":info: [dim cyan]INFO[/] {message}")


def log_warn(message: str) -> None:
    """Logs a warning to the standard output."""
    console.log(f":warning: [dim yellow]WARN[/] {message}")


def log_error(message: str) -> None:
    """Logs an error to the stderr."""
    err_console.log(f":error: [dim red]ERROR[/] {message}")


def log_exception() -> None:
    """Logs an exception to stderr."""
    console.print_exception(show_locals=True)
