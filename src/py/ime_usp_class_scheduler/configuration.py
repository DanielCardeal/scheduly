from __future__ import annotations

from pathlib import Path
from typing import Optional

import cattrs
import tomli
from attr import Factory, define
from attrs import field, validators

from ime_usp_class_scheduler.constants import (
    HARD_CONSTRAINTS_DIR,
    PRESETS_DIR,
    SOFT_CONSTRAINTS_DIR,
)
from ime_usp_class_scheduler.log import LOG_INFO, LOG_WARN


class ConfigurationException(Exception):
    """Raised when a configuration error is found"""


@define
class Configuration:
    """Represents the user configuration of the scheduler program"""

    clingo: ClingoOptions
    constraints: ConstraintSpecification


@define
class ClingoOptions:
    """Configuration options for the underlying clingo solver"""

    num_models: int = 1
    time_limit: int = 30
    threads: int = 1


@define
class ConstraintSpecification:
    """Configurations related to constraints of the scheduler"""

    hard: list[HardConstraintsSpecification] = Factory(list)
    soft: list[SoftConstraintsSpecification] = Factory(list)

    def into_asp(self) -> str:
        """Loads the specification's constraints into a string."""
        code = "\n".join(constraint.into_asp() for constraint in self.hard + self.soft)
        return code + "\n"


@define
class HardConstraintsSpecification:
    """User configuration of hard constraints."""

    name: str = field(validator=validators.min_len(1))

    @property
    def path(self) -> Path:
        return HARD_CONSTRAINTS_DIR.joinpath(self.name).with_suffix(".lp")

    def into_asp(self) -> str:
        """Load hard constraint into a string.

        Raises an ConfigurationException if it is not possible to load the file
        contents.
        """
        code = ""
        try:
            with open(self.path) as f:
                code += f.read()
        except OSError as e:
            raise ConfigurationException(
                f"Unable to load '{self.name}' hard constraint: {e}"
            )
        return code


@define
class SoftConstraintsSpecification:
    """User configuration of soft constraints."""

    name: str = field(validator=validators.min_len(1))

    weight: int = field()

    @weight.validator
    def _weight_validator(self, _: str, weight: int) -> None:
        if weight == 0:
            # NOTE: TIP: if you want to disable a soft constraint, just comment
            # it out of in the preset file.
            raise ConfigurationException("Weight must be different from 0.")

    priority: int

    @property
    def path(self) -> Path:
        return SOFT_CONSTRAINTS_DIR.joinpath(self.name).with_suffix(".lp")

    def into_asp(self) -> str:
        """Load soft constraint into a string, setting its weight and priority
        as ASP constants.

        Raises a ConfigurationException if it is not possible to load the file
        contents.
        """
        code = ""
        try:
            with open(self.path) as f:
                code += f.read()
        except OSError as e:
            raise ConfigurationException(
                f"Unable to load '{self.name}' soft constraint: {e}"
            )

        weight = f"#const w_{self.name} = {self.weight}.\n"
        priority = f"#const p_{self.name} = {self.priority}.\n"
        code += weight + priority

        return code


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
    except FileNotFoundError:
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
    if configuration.clingo.threads <= 0:
        raise ConfigurationException("Number of solving threads must be >= 1.")
    elif configuration.clingo.threads == 1:
        LOG_WARN("Using only one solving thread, performance might be low.")
    else:
        LOG_INFO("Number of threads:", configuration.clingo.threads)

    return configuration
