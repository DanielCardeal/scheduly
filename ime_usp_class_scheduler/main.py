import logging

import click


@click.group()
@click.option(
    "-l",
    "--log-file",
    type=click.Path(file_okay=True, dir_okay=False),
    default="class_scheduler.log",
    help="custom path to LOG file",
)
def main(log_file):
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
@click.option("-n", "--num-models", default=1, help="number of models to be generated")
@click.option(
    "-t", "--time-limit", default=500, help="limit execution time to <n> seconds."
)
@click.option(
    "-j",
    "--threads",
    default=1,
    help="number of threads to use for solving. "
    "A value of 0 or less uses all of the threads available in the system.",
)
def cli(num_models, time_limit, threads):
    logging.info(f"Number of models: {num_models}")

    if threads == 1:
        logging.warn("Using only 1 thread. Solving performance may be low.")
    else:
        logging.info(f"Number of threads: {threads}")

    logging.info(f"Time limit: {time_limit} seconds")


if __name__ == "__main__":
    main()
