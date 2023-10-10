"""
Logging facilities for the scheduler.
"""
from functools import partial

from rich.console import Console

CONSOLE = Console(stderr=True, log_time=False)


_ERR_PREAMBLE = "[dim red]ERROR[/]"
_INFO_PREAMBLE = "[dim cyan]INFO[/]"
_WARN_PREAMBLE = "[dim yellow]WARN[/]"


LOG_INFO = partial(CONSOLE.log, _INFO_PREAMBLE)
"""Logs an exception to stderr."""

LOG_WARN = partial(CONSOLE.log, _WARN_PREAMBLE)
"""Logs a warning to stderr."""

LOG_ERROR = partial(CONSOLE.log, _ERR_PREAMBLE)
"""Logs an error to stderr."""


def LOG_EXCEPTION(e: Exception) -> None:
    """Logs an exception to stderr."""
    name = e.__class__.__name__
    exception_name = f"([dim white]{name}[/])"
    LOG_ERROR(exception_name, e)
