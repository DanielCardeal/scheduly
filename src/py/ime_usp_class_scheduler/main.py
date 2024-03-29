from os import EX_DATAERR, EX_OSERR
from pathlib import Path
from textwrap import dedent
from typing import Optional

import click

from ime_usp_class_scheduler.errors import (
    FileTreeError,
    InconsistentInputError,
    ParsingError,
)
from ime_usp_class_scheduler.log import LOG_ERROR, LOG_EXCEPTION, LOG_INFO, LOG_WARN
from ime_usp_class_scheduler.model.configuration import load_preset
from ime_usp_class_scheduler.paths import HARD_CONSTRAINTS_DIR, SOFT_CONSTRAINTS_DIR
from ime_usp_class_scheduler.program import CliProgram
from ime_usp_class_scheduler.prompt import Confirm, Prompt, PromptNonEmpty


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
    help="Number (N > 1) of threads to use for solving.",
)
@click.option(
    "-o",
    "--output_model",
    "output_model",
    required=False,
    type=click.Path(path_type=Path),
    help="Output generated ASP program to PATH",
)
@click.option(
    "-d",
    "--dump",
    required=False,
    type=click.Choice(["json", "csv"], case_sensitive=False),
    help="Dump schedule results into a traditional format.",
)
def cli(
    preset: str,
    num_schedules: Optional[int],
    time_limit: Optional[int],
    threads: Optional[int],
    output_model: Optional[Path],
    dump: Optional[str],
) -> None:
    """Create and display a nice timetable from the terminal."""
    try:
        configuration = load_preset(
            preset, num_schedules=num_schedules, time_limit=time_limit, threads=threads
        )
        program = CliProgram(configuration, dump_symbols=dump)
    except (ParsingError, InconsistentInputError) as e:
        LOG_EXCEPTION(e)
        exit(EX_DATAERR)
    except FileTreeError as e:
        LOG_EXCEPTION(e)
        exit(EX_OSERR)

    if output_model is not None:
        try:
            if not output_model.exists() or Confirm.ask(
                f"{output_model} file already exists, overwrite?",
                default=True,
            ):
                with open(output_model, "w") as file:
                    program.save_program(file)
                LOG_INFO(f"Starting model saved to {output_model}")
            else:
                LOG_WARN("Aborted saving model to disk")
        except OSError as e:
            LOG_ERROR(
                f"Unable to write program to '{e.filename}': {e.strerror.lower()}"
            )
            exit(EX_OSERR)

    try:
        program.start()
    except FileTreeError as e:
        LOG_EXCEPTION(e)
        exit(EX_OSERR)


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
            f"""\
        %*
        {description}
        *%
        :- % your rules here
        """
        )
    elif constraint_type == "soft":
        path = SOFT_CONSTRAINTS_DIR.joinpath(constraint_name).with_suffix(".lp")
        contents = dedent(
            f"""\
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
