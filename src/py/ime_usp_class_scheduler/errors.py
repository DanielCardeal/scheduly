"""All of the exceptions that can be raised during a run of the scheduler."""


from typing import Optional

from cattrs.errors import (
    BaseValidationError,
    ClassValidationError,
    IterableValidationError,
)
from cattrs.v import format_exception
from typing_extensions import Self


class BaseSchedulerError(Exception):
    """Base for all scheduler related errors."""


class ParsingError(BaseSchedulerError):
    """Error raised whenever it is impossible to parse data from a source
    into the scheduler data model.
    """

    @classmethod
    def from_cattrs_error(cls, name: str, what: str, err: BaseValidationError) -> Self:
        """Transform a cattrs.BaseValidationError into a nicely formatted ParsingError.

        `name` is name of the object/data that was being parsed, `what` is a string
        describing what was being parsed and `err` is the thrown cattrs error.
        """
        errors = "\n".join(f" * {msg}" for msg in _extract_cattrs_error(err))
        message = f"Errors where found while parsing {what} '{name}':\n{errors}"
        return cls(message)


class InconsistentInputError(BaseSchedulerError):
    """Exception raised when the scheduler input data is malformed/inconsistent."""


class FileTreeError(BaseSchedulerError):
    """Exception raised when there are problems with the scheduler file tree structure."""

    @classmethod
    def from_os_error(cls, name: str, what: str, err: OSError) -> Self:
        """Transform a OSError into a FileTreeError.

        `name` is name of the object/data that was being read, `what` is a string
        describing what the file was expected to be and `err` is the thrown `OSError`.
        """
        message = f" Unable to load '{name}' {what} file from path '{err.filename}': {err.strerror.lower()}"

        return cls(message)


def _extract_cattrs_error(
    exc: ClassValidationError | IterableValidationError | BaseException,
    path: str = "$",
) -> list[str]:
    """Extract a list of error messages from a `cattrs` exception.

    This implementation is mostly based on the 23.2 unreleased version
    of `format_exception` and `transform_error`.
    """

    def _format_exception(exc: BaseException, type: Optional[type]) -> str:
        """Format a base exception raised while parsing a cattrs BaseValidationError."""
        if isinstance(exc, ValueError):
            return str(exc)
        return format_exception(exc, type)

    errors = []
    if isinstance(exc, IterableValidationError):
        with_notes, without = exc.group_exceptions()
        for exc, note in with_notes:
            p = f"{path}[{note.index!r}]"
            if isinstance(exc, (ClassValidationError, IterableValidationError)):
                errors.extend(_extract_cattrs_error(exc, p))
            else:
                errors.append(f"{_format_exception(exc, note.type)} (at {p})")
        for exc in without:
            errors.append(f"{_format_exception(exc, None)} (at {path})")
    elif isinstance(exc, ClassValidationError):
        with_notes, without = exc.group_exceptions()  # type: ignore[assignment]
        for exc, note in with_notes:
            p = f"{path}.{note.name}"  # type: ignore[attr-defined]
            if isinstance(exc, (ClassValidationError, IterableValidationError)):
                errors.extend(_extract_cattrs_error(exc, p))
            else:
                errors.append(f"{_format_exception(exc, note.type)} (at {p})")
        for exc in without:
            errors.append(f"{_format_exception(exc, None)} (at {path})")
    else:
        errors.append(f"{_format_exception(exc, None)} (at {path})")
    return errors
