from functools import partial
from typing import Optional, TextIO

import rich.prompt
from rich.console import Console
from rich.prompt import InvalidResponse, PromptType
from rich.text import Text, TextType

CONSOLE = Console(stderr=True, log_time=False)

_ERR_PREAMBLE = "[dim red]ERROR[/]"
_INFO_PREAMBLE = "[dim cyan]INFO[/]"
_WARN_PREAMBLE = "[dim yellow]WARN[/]"


class PromptBase(rich.prompt.PromptBase[PromptType]):
    """Overriten PromptBase class that adheres to the CLI output standard of
    the class scheduler.
    """

    validate_error_message = "Please enter a valid value"
    illegal_choice_message = "Please select one of the available options"

    @classmethod
    def get_input(
        cls,
        console: Console,
        prompt: TextType,
        password: bool,
        stream: Optional[TextIO] = None,
    ) -> str:
        """Get input from user using stderr for messages."""
        return CONSOLE.input(prompt, password=password, stream=stream)

    def on_validate_error(self, _: str, error: InvalidResponse) -> None:
        """Called to handle a validation error."""
        LOG_ERROR(error)


class Prompt(PromptBase[str]):
    """Prompts the user for a string.

    This is a customized prompt that adheres to the CLI output standard of the
    class scheduler.
    """

    response_type = str


class Confirm(PromptBase[bool]):
    """A yes / no confirmation prompt.

    This is a customized prompt that adheres to the CLI output standard of the
    class scheduler.
    """

    response_type = bool
    validate_error_message = "Please enter Y or N"
    choices: list[str] = ["yes", "no"]

    def render_default(self, default: bool) -> Text:
        """Render the default as (y) or (n) rather than True/False."""
        yes, no = self.choices
        return Text(f"({yes})" if default else f"({no})", style="prompt.default")

    def process_response(self, value: str) -> bool:
        """Convert choices to a bool."""
        value = value.strip().lower()
        match value:
            case "y" | "yes":
                return True
            case "n" | "no":
                return False
            case _:
                raise InvalidResponse(self.validate_error_message)


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
