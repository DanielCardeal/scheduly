"""Dataclasses that represent the clingo solver configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import tomli
from attrs import Factory, define, field, validators
from cattrs import BaseValidationError

from ime_usp_class_scheduler.constants import (
    HARD_CONSTRAINTS_DIR,
    PRESETS_DIR,
    SOFT_CONSTRAINTS_DIR,
)
from ime_usp_class_scheduler.log import LOG_INFO, LOG_WARN, extract_cattrs_error
from ime_usp_class_scheduler.model.common import CONVERTER


class PresetConfigException(Exception):
    """Raised when an error is found while loading a preset file."""


@define
class Configuration:
    """Represents the user configuration of the scheduler program"""

    options: ClingoOptions
    """Options for the underlying clingo solver."""

    constraints: ConstraintSpecification
    """Constraints specification for the solver."""


@define
class ClingoOptions:
    """Configuration options for the underlying clingo solver"""

    threads: int = field(validator=validators.gt(0))
    """Number of clingo solving threads to use."""

    num_models: int = field(validator=validators.ge(1))
    """Number of schedules to create."""

    time_limit: int = field(validator=validators.gt(0))
    """Time limit (in seconds) to search for solutions."""


@define
class ConstraintSpecification:
    """Configurations related to constraints of the scheduler"""

    hard: list[HardConstraintsSpecification] = Factory(list)
    """List of hard constraints to add to the model."""

    soft: list[SoftConstraintsSpecification] = Factory(list)
    """List of soft constraints to add to the model."""

    def into_asp(self) -> str:
        """Loads the specification's constraints into a string."""
        code = "\n".join(constraint.into_asp() for constraint in self.hard + self.soft)
        return code + "\n"


@define
class HardConstraintsSpecification:
    """User configuration of hard constraints."""

    name: str = field(validator=validators.min_len(1))
    """Name of the hard constraint.

    Must be the same as the filename (without extension) of the file that
    contains the hard constraint code in the `HARD_CONSTRAINTS_DIR`.
    """

    @property
    def path(self) -> Path:
        """Path of the hard constraint file."""
        return HARD_CONSTRAINTS_DIR.joinpath(self.name).with_suffix(".lp")

    def into_asp(self) -> str:
        """Load hard constraint into a string.

        Raises an PresetConfigException if it is not possible to load the file
        contents.
        """
        code = ""
        try:
            with open(self.path) as f:
                code += f.read()
        except OSError as e:
            raise PresetConfigException(
                f"Unable to load '{self.name}' hard constraint: {e}"
            )
        return code


@define
class SoftConstraintsSpecification:
    """User configuration of soft constraints."""

    name: str = field(validator=validators.min_len(1))
    """Name of the soft constraint.

    Must be the same as the filename (without extension) of the file that
    contains the soft constraint code in the `SOFT_CONSTRAINTS_DIR`.
    """

    weight: int = field()
    """Weight (or cost) of the soft constraint.

    The higher the weight, the worst it is to violate the soft constraint.
    """

    @weight.validator
    def _weight_validator(self, _: str, weight: int) -> None:
        if weight == 0:
            # NOTE: TIP: if you want to disable a soft constraint, just comment
            # it out of in the preset file.
            raise ValueError("soft constraint weights must be different than 0.")

    priority: int
    """Priority (or optimization layer) of the soft constraint.

    Soft constraints with higher priority will be optimized before those with
    lower priority.
    """

    @property
    def path(self) -> Path:
        """Path of the soft constraint file."""
        return SOFT_CONSTRAINTS_DIR.joinpath(self.name).with_suffix(".lp")

    def into_asp(self) -> str:
        """Load soft constraint into a string, setting its weight and priority
        as ASP constants.

        Raises a PresetConfigException if it is not possible to load the file
        contents.
        """
        code = ""
        try:
            with open(self.path) as f:
                code += f.read()
        except OSError as e:
            raise PresetConfigException(
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
    except tomli.TOMLDecodeError as e:
        raise PresetConfigException(
            f"TOML syntax error in preset file {preset_path}:\n{e}"
        )
    except FileNotFoundError:
        raise PresetConfigException(f"Unable to find preset file {preset_path}.")

    try:
        configuration = CONVERTER.structure(configuration_dict, Configuration)
    except BaseValidationError as e:
        messages = "\n".join(f"* {msg}" for msg in extract_cattrs_error(e))
        raise PresetConfigException(
            f"Some errors were found while parsing the '{preset}' preset file:\n{messages}"
        )

    # Overwrite values
    if num_schedules is not None:
        configuration.options.num_models = num_schedules
    if time_limit is not None:
        configuration.options.time_limit = time_limit
    if threads is not None:
        configuration.options.threads = threads

    LOG_INFO("Number of models:", configuration.options.num_models)
    LOG_INFO("Time limit (s):", configuration.options.time_limit)
    if configuration.options.threads == 1:
        LOG_WARN("Using only one solving thread, performance might be low.")
    else:
        LOG_INFO("Number of threads:", configuration.options.threads)

    return configuration
