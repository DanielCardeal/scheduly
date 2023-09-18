import logging
from pathlib import Path
from typing import Optional

import click

from ime_usp_class_scheduler.interface.cli import CliInterface, Configuration


@click.group()
@click.option(
    "-l",
    "--log-file",
    type=click.Path(file_okay=True, dir_okay=False),
    default="class_scheduler.log",
    help="custom path to LOG file",
)
def main(log_file: Path) -> None:
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%b %d %H:%m:%S",
    )
    click.echo(f'Logging to "{log_file}"')


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
def cli(
    preset: str,
    num_models: Optional[int],
    time_limit: Optional[int],
    threads: Optional[int],
) -> None:
    logging.info(f"Number of models: {num_models}")

    if threads == 1:
        logging.warn("Using only 1 thread. Solving performance may be low.")
    else:
        logging.info(f"Number of threads: {threads}")

    logging.info(f"Time limit: {time_limit} seconds")

    try:
        configuration = Configuration(
            preset, num_models=num_models, time_limit=time_limit, threads=threads
        )
        interface = CliInterface(configuration)
    except Exception as e:
        print(e)
        exit(1)

    print(interface.program)


if __name__ == "__main__":
    main()
