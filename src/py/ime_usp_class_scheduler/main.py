from pathlib import Path
from textwrap import dedent
from typing import Optional

import click
from rich.prompt import Confirm

from ime_usp_class_scheduler.configuration import ConfigurationException, load_preset
from ime_usp_class_scheduler.constants import HARD_CONSTRAINTS_DIR, SOFT_CONSTRAINTS_DIR
from ime_usp_class_scheduler.program import CliProgram
from ime_usp_class_scheduler.terminal import (
    LOG_ERROR,
    LOG_EXCEPTION,
    LOG_INFO,
    LOG_WARN,
    Prompt,
    PromptNonEmpty,
)


@click.group()
def main() -> None:
    """A highly configurable timetabling tool."""
    pass


@main.command()
@click.option(
    "-p",
    "--preset",
    default="default",
    help="Load preset by name.",
)
@click.option(
    "-n",
    "--num-schedules",
    required=False,
    type=int,
    help="Number (N > 0) of schedules to create.",
)
@click.option(
    "-t",
    "--time-limit",
    required=False,
    type=int,
    help="Limit execution time to N seconds.",
)
@click.option(
    "-j",
    "--threads",
    required=False,
    type=int,
    help="Number of threads to use for solving. "
    "A value of 0 or less uses all of the threads available in the system.",
)
@click.option(
    "-o",
    "--output_model",
    "output_model",
    required=False,
    type=click.Path(path_type=Path),
    help="Output generated ASP program to PATH",
)
def cli(
    preset: str,
    num_schedules: Optional[int],
    time_limit: Optional[int],
    threads: Optional[int],
    output_model: Optional[Path],
) -> None:
    """Create and display a nice timetable from the terminal."""
    try:
        configuration = load_preset(
            preset, num_schedules=num_schedules, time_limit=time_limit, threads=threads
        )
        program = CliProgram(configuration)
        if output_model is not None:
            if not output_model.exists() or Confirm.ask(
                f"{output_model} file already exists, overwrite?"
            ):
                program.save_model(output_model)
                LOG_INFO(f"Starting model saved to {output_model}")
            else:
                LOG_WARN("Aborted saving model to disk")

        program.start()
    except ConfigurationException as e:
        LOG_EXCEPTION(e)
        exit(1)
    except (FileNotFoundError, OSError, PermissionError) as e:
        LOG_ERROR(f"Unable to save model to '{e.filename}': {e.__class__.__name__}")
        exit(1)


@main.command()
@click.option(
    "-t",
    "--type",
    "constraint_type",
    type=click.Choice(["hard", "soft"], case_sensitive=False),
    help="Type of the constraint to be created",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run but don't write the changes",
)
def new(constraint_type: str, dry_run: bool) -> None:
    """Add new rules for the underlying scheduler."""
    if dry_run:
        LOG_WARN("Running in 'dry_run' mode. Changes won't be saved to disk.")

    if not constraint_type:
        constraint_type = Prompt.ask("Constraint type", choices=["hard", "soft"])

    assert constraint_type in (
        "hard",
        "soft",
    ), f"Invalid constraint type: {constraint_type}"

    constraint_name = PromptNonEmpty.ask("Enter the constraint name")
    constraint_name = "_".join([word.lower() for word in constraint_name.split()])

    description = Prompt.ask(
        "Enter the constraint description",
        default="Constraint description",
        show_default=False,
    )

    if constraint_type == "hard":
        path = HARD_CONSTRAINTS_DIR.joinpath(constraint_name).with_suffix(".lp")
        contents = dedent(
            f"""
        %*
        {description}
        *%
        :- % your rules here
        """
        )
    elif constraint_type == "soft":
        path = SOFT_CONSTRAINTS_DIR.joinpath(constraint_name).with_suffix(".lp")
        contents = dedent(
            f"""
        %*
        {description}
        *%
        :~ %* constraint logic *%.
        [w_{constraint_name}@p_{constraint_name}, %* terms *% ]
        """
        )

    if path.exists() and not Confirm.ask(
        "There is already a soft constraint with this name. Override?"
    ):
        LOG_ERROR("Aborted!")
        exit(1)

    if dry_run:
        LOG_INFO(f"The following contents would be written to {path}:")
    else:
        LOG_INFO(f"Saving the following contents to {path}:")
    # NOTE: Don't use rich because of soft constraint brackets
    print(contents)

    if not dry_run:
        with open(path, "w") as f:
            f.write(contents)


if __name__ == "__main__":
    main()
