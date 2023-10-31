# Getting started

Scheduly is built so that users are not only able, but also encouraged, to
configure the system to their respective needs. With that in mind, we
recommended way to install and use the system is **cloning the repo and running
the system locally**.

## Cloning the repo

To get an up-to-date copy of the repository on your system, run:

```
git clone https://github.com/DanielCardeal/scheduly
```

This will download the scheduler code into the `scheduly/` directory. All the
commands listed below should be run on the root of the `scheduly/` directory.

## Installing dependencies

Scheduly uses [poetry](https://python-poetry.org) as a dependency manager and
packaging tool. With that in mind, follow the instructions on
[poetry's documentation](https://python-poetry.org/docs/#installing-with-the-official-installer)
to get poetry properly installed and configured in your system.

We also recommend that users install [pyenv](https://github.com/pyenv/pyenv) to
manage local versions of Python. The officially supported Python version of the
project is Python 3.10, but newer versions should work fine. **Python versions
prior to 3.10 will not work at all!**

After installing the poetry package manager and setting up the correct Python
version, run the following command on the project root to install all the
dependencies:

```
poetry install
```

If everything runs smoothly, you will be now able to run the commands:

```
poetry shell # Open a shell inside the project virtual environment
scheduly cli # Runs the command-line interface of the scheduler
```

After a short amount of time, a nicely formatted example timetable should be
displayed in the terminal window. To learn more about how to use and configure
the system, see [scheduling 101](docs/scheduling_101.md).
