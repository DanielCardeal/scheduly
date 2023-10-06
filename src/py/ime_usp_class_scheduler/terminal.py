from functools import partial

from cattrs import ClassValidationError, transform_error
from rich.console import Console
from rich.prompt import InvalidResponse, PromptBase

CONSOLE = Console(stderr=True, log_time=False)

_ERR_PREAMBLE = "[dim red]ERROR[/]"
_INFO_PREAMBLE = "[dim cyan]INFO[/]"
_WARN_PREAMBLE = "[dim yellow]WARN[/]"


class Prompt(PromptBase[str]):
    """Prompts the user for a string.

    This is a customized prompt that adheres to the CLI output standard of the
    class scheduler.
    """

    response_type = str
    illegal_choice_message = "Please select one of the available options"

    def on_validate_error(self, _: str, error: InvalidResponse) -> None:
        """Called to handle a validation error."""
        LOG_ERROR(error)


class PromptNonEmpty(Prompt):
    """Prompts user for a non-empty string.

    This is a customized prompt that adheres to the CLI output standard of the
    class scheduler.
    """

    response_type = str
    validate_error_message = "Plase type a non-empty response"

    def process_response(self, value: str) -> str:
        """Validate if response is non-empty."""
        if not value:
            raise InvalidResponse(self.validate_error_message)
        return value


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
