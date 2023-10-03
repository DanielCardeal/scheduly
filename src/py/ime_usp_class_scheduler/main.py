import logging
from pathlib import Path
from typing import Optional

import click

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


if __name__ == "__main__":
    main()
