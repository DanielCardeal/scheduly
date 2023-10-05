from pathlib import Path
from textwrap import dedent
from typing import Optional

import click
from rich.prompt import Confirm

from ime_usp_class_scheduler.configuration import load_preset
from ime_usp_class_scheduler.constants import HARD_CONSTRAINTS_DIR, SOFT_CONSTRAINTS_DIR
from ime_usp_class_scheduler.interface import CliInterface
from ime_usp_class_scheduler.terminal import (
    Prompt,
    PromptNonEmpty,
    LOG_ERROR,
    LOG_EXCEPTION,
    LOG_INFO,
    LOG_WARN,
)


@click.group()
def main() -> None:
    pass


@main.command()
@click.option(
    "-p",
    "--preset",
    default="default",
    help="filename (without extension) of TOML preset file.",
)
@click.option(
    "-n", "--num-models", required=False, help="number of models to be generated"
)
@click.option(
    "-t", "--time-limit", required=False, help="limit execution time to <n> seconds."
)
@click.option(
    "-j",
    "--threads",
    required=False,
    help="number of threads to use for solving. "
    "A value of 0 or less uses all of the threads available in the system.",
)
@click.option(
    "--save-model",
    "model_out_path",
    required=False,
    help="Save underlying clingo program - with inputs - to {file}.",
    type=click.Path(file_okay=True, dir_okay=False),
)
def cli(
    preset: str,
    num_models: Optional[int],
    time_limit: Optional[int],
    threads: Optional[int],
    model_out_path: Optional[Path],
) -> None:
    try:
        configuration = load_preset(
            preset, num_models=num_models, time_limit=time_limit, threads=threads
        )
        interface = CliInterface(configuration)
    except Exception:
        LOG_EXCEPTION()
        exit(1)

    if model_out_path is not None:
        interface.save_model(model_out_path)

    interface.run()


@main.command()
@click.argument("constraint-type", type=click.Choice(["hard", "soft"]), nargs=1)
def new(constraint_type: str) -> None:
    assert constraint_type in (
        "hard",
        "soft",
    ), f"Invalid constraint type: {constraint_type}"

    name = Prompt.ask("Enter the constraint name")
    if not name:
        log_error("The constraint name cannot be empty.")
        exit(1)
    name = "_".join([word.lower() for word in name.split()])

    description = Prompt.ask(
        "Enter the constraint description",
        default="Constraint description",
        show_default=False,
    )

    if constraint_type == "hard":
        path = HARD_CONSTRAINTS_DIR.joinpath(name).with_suffix(".lp")
        contents = dedent(
            f"""
        %*
        {description}
        *%
        :- % your rules here
        """
        )
    elif constraint_type == "soft":
        path = SOFT_CONSTRAINTS_DIR.joinpath(name).with_suffix(".lp")
        contents = dedent(
            f"""
        %*
        {description}
        *%
        :~ %* constraint logic *%.
        [w_{name}@p_{name}, %* terms *% ]
        """
        )

    if not path.exists() or Confirm.ask(
        "There is already a soft constraint with this name. Override?"
    ):
        with open(path, "w") as f:
            f.write(contents)
        log_info(f"Created {path} with the following contents:")
        # NOTE: Don't use rich because of soft constraint brackets
        print(contents)
    else:
        log_info("Operation cancelled.")


if __name__ == "__main__":
    main()
