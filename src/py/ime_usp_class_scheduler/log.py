"""
Logging facilities for the scheduler.
"""
from functools import partial
from typing import Optional

from cattrs import (
    AttributeValidationNote,
    ClassValidationError,
    IterableValidationError,
)
from cattrs.v import format_exception
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


def _format_exception(exc: BaseException, type: Optional[type]) -> str:
    """Format a base exception raised while parsing a cattrs BaseValidationError."""
    if isinstance(exc, ValueError):
        return str(exc)
    return format_exception(exc, type)


def extract_cattrs_error(
    exc: ClassValidationError | IterableValidationError | BaseException,
    path: str = "$",
) -> list[str]:
    """Extract a list of error messages from a `cattrs` exception.

    This implementation is mostly based on the 23.2 unreleased version
    of `format_exception`."""
    errors = []
    if isinstance(exc, IterableValidationError):
        with_notes, without = exc.group_exceptions()
        for exc, note in with_notes:
            p = f"{path}[{note.index!r}]"
            if isinstance(exc, (ClassValidationError, IterableValidationError)):
                errors.extend(extract_cattrs_error(exc, p))
            else:
                errors.append(f"{_format_exception(exc, note.type)} (at {p})")
        for exc in without:
            errors.append(f"{_format_exception(exc, None)} (at {path})")
    elif isinstance(exc, ClassValidationError):
        with_notes, without = exc.group_exceptions()  # type: ignore[assignment]
        for exc, note in with_notes:
            p = f"{path}.{note.name}"  # type: ignore[attr-defined]
            if isinstance(exc, (ClassValidationError, AttributeValidationNote)):
                errors.extend(extract_cattrs_error(exc, p))
            else:
                errors.append(f"{_format_exception(exc, note.type)} (at {p})")
        for exc in without:
            errors.append(f"{_format_exception(exc, None)} (at {path})")
    else:
        errors.append(f"{_format_exception(exc, None)} (at {path})")
    return errors
