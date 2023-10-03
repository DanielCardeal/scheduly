from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import cattrs
import tomli
from attr import define

from ime_usp_class_scheduler.constants import PRESETS_DIR


class ConfigurationException(Exception):
    """Raised when a configuration error is found"""


@define
class Configuration:
    """Represents the user configuration of the scheduler program"""

    clingo: ClingoOptions
    constraints: ConstraintsConfiguration


@define
class ClingoOptions:
    """Configuration options for the underlying clingo solver"""

    num_models: int
    time_limit: int
    threads: int


@define
class ConstraintsConfiguration:
    """Configurations related to constraints of the scheduler"""

    hard: list[HardConstraintsConfiguration]
    soft: list[SoftConstraintsConfiguration]


@define
class HardConstraintsConfiguration:
    """User configuration of hard constraints."""

    name: str

    @property
    def path(self) -> Path:
        return Path(self.name).with_suffix(".lp")


@define
class SoftConstraintsConfiguration:
    """User configuration of soft constraints."""

    name: str
    weight: int
    priority: int

    @property
    def path(self) -> Path:
        return Path(self.name).with_suffix(".lp")


def load_preset(
    preset: str,
    /,
    num_models: Optional[int] = None,
    time_limit: Optional[int] = None,
    threads: Optional[int] = None,
) -> Configuration:
    preset_path = PRESETS_DIR.joinpath(preset).with_suffix(".toml")
    try:
        with open(preset_path, "rb") as f:
            configuration_dict = tomli.load(f)
    except tomli.TOMLDecodeError as e:
        raise ConfigurationException(
            f"TOML syntax error in preset file {preset_path}:\n{e}"
        )
    except FileNotFoundError as e:
        raise ConfigurationException(f"Unable to find preset file {preset_path}.")

    configuration = cattrs.structure(configuration_dict, Configuration)

    if num_models is not None:
        configuration.clingo.num_models = num_models
    if time_limit is not None:
        configuration.clingo.time_limit = time_limit
    if threads is not None:
        configuration.clingo.threads = threads

    logging.info(f"Number of models: {configuration.clingo.num_models}")
    logging.info(f"Time limit: {configuration.clingo.time_limit} seconds")
    if configuration.clingo.threads == 1:
        logging.warn("Using only 1 thread. Solving performance may be low.")
    else:
        logging.info(f"Number of threads: {configuration.clingo.threads}")

    return configuration
