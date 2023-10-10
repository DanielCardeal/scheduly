from __future__ import annotations

from pathlib import Path
from typing import Optional

import cattrs
import tomli
from attr import Factory, define

from ime_usp_class_scheduler.constants import PRESETS_DIR
from ime_usp_class_scheduler.log import LOG_INFO, LOG_WARN


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

    num_models: int = 1
    time_limit: int = 30
    threads: int = 1


@define
class ConstraintsConfiguration:
    """Configurations related to constraints of the scheduler"""

    hard: list[HardConstraintsConfiguration] = Factory(list)
    soft: list[SoftConstraintsConfiguration] = Factory(list)


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
    num_schedules: Optional[int] = None,
    time_limit: Optional[int] = None,
    threads: Optional[int] = None,
) -> Configuration:
    """Loads configuration from a preset file.

    If any of the keyword arguments is not None, the loader overwrites the
    respective configuration key with the given value.
    """
    preset_path = PRESETS_DIR.joinpath(preset).with_suffix(".toml")
    try:
        with open(preset_path, "rb") as f:
            configuration_dict = tomli.load(f)
        configuration = cattrs.structure(configuration_dict, Configuration)
    except tomli.TOMLDecodeError as e:
        raise ConfigurationException(
            f"TOML syntax error in preset file {preset_path}:\n{e}"
        )
    except FileNotFoundError as e:
        raise ConfigurationException(f"Unable to find preset file {preset_path}.")
    except cattrs.ClassValidationError as e:
        # Capture the first error and raise it as a ConfigurationException
        message = cattrs.transform_error(e)[0]
        raise ConfigurationException(f"Malformed preset file {preset_path}: {message}")

    if num_schedules is not None:
        configuration.clingo.num_models = num_schedules
    if time_limit is not None:
        configuration.clingo.time_limit = time_limit
    if threads is not None:
        configuration.clingo.threads = threads

    LOG_INFO("Number of models:", configuration.clingo.num_models)
    LOG_INFO("Time limit (s):", configuration.clingo.time_limit)
    if configuration.clingo.threads == 1:
        LOG_WARN("Using only one solving thread, performance might be low.")
    else:
        LOG_INFO("Number of threads:", configuration.clingo.threads)

    return configuration
