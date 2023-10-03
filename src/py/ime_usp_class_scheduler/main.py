from pathlib import Path
from textwrap import dedent
from typing import Optional

import click
from rich.prompt import Confirm, Prompt

from ime_usp_class_scheduler.constants import HARD_CONSTRAINTS_DIR, SOFT_CONSTRAINTS_DIR
from ime_usp_class_scheduler.interface.CliInterface import CliInterface
from ime_usp_class_scheduler.interface.configuration import load_preset
from ime_usp_class_scheduler.logging import error, info


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
    configuration = load_preset(
        preset, num_models=num_models, time_limit=time_limit, threads=threads
    )
    interface = CliInterface(configuration)

    if model_out_path is not None:
        interface.save_model(model_out_path)

    interface.run()


@main.command()
@click.argument("constraint-type", type=click.Choice(["hard", "soft"]), nargs=1)
def new(constraint_type: str):
    assert constraint_type in (
        "hard",
        "soft",
    ), f"Invalid constraint type: {constraint_type}"

    name = Prompt.ask("Enter the constraint name")
    if not name:
        error("The constraint name cannot be empty.")
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
        info(f"Created {path} with the following contents:")
        # NOTE: Don't use rich because of soft constraint brackets
        print(contents)
    else:
        print()


if __name__ == "__main__":
    main()
