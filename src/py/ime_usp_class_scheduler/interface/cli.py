from __future__ import annotations

from pathlib import Path
from typing import Optional
from attrs import define

import tomli
from clingo import Control, Symbol

from ime_usp_class_scheduler.constants import INPUT_DIR, PRESETS_DIR
from ime_usp_class_scheduler.model.data import ASPData
from ime_usp_class_scheduler.parser import (
    ime_parse_schedule,
    ime_parse_workload,
    parse_courses,
    parse_curricula,
    parse_joint,
)


@define
class Configuration:
    """Represents the user configuration of the scheduler program"""
    preset: str
    num_models: int
    time_limit: int
    threads: int

    hard_constraints: list[str]
    soft_constraints: list[str]

    def __init__(
        self,
        preset: str,
        /,
        num_models: Optional[int],
        time_limit: Optional[int],
        threads: Optional[int],
    ) -> None:
        self.preset = preset

        preset_filepath = PRESETS_DIR.joinpath(preset).with_suffix(".toml")
        with open(preset_filepath, "rb") as f:
            config = tomli.load(f)

        match config:
            case {
                "clingo_options": {
                    "num_models": preset_num_models,
                    "time_limit": preset_time_limit,
                    "threads": preset_threads,
                },
                "constraints": {
                    "hard": [*hard_constraints],
                    "soft": [*soft_constraints],
                },
            }:
                self.num_models = preset_num_models if not num_models else num_models
                self.time_limit = preset_time_limit if not time_limit else time_limit
                self.threads = preset_threads if not threads else threads
                self.hard_constraints = hard_constraints
                self.soft_constraints = soft_constraints
            case _:
                raise ValueError(
                    f"Invalid preset configuration file ({preset_filepath}):\n{config}"
                )


class CliInterface:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

        # Set clingo options
        self.ctl = Control()
        self.ctl.configuration.solve.opt_mode = "optN"  # type: ignore[union-attr]
        self.ctl.configuration.solve.models = configuration.num_models  # type: ignore[union-attr]
        self.ctl.configuration.solve.parallel_mode = configuration.threads  # type: ignore[union-attr]

        self.raw_inputs = self._load_inputs()

    @property
    def asp_inputs(self) -> list[Symbol]:
        """Return the ASP representation of the raw input data."""
        return [
            asp_string
            for raw_input in self.raw_inputs
            for asp_string in raw_input.to_asp()
        ]

    def _load_inputs(self) -> list[ASPData]:
        """Import data on INPUT_DIR using the appropriate parsers."""
        input_data: list[ASPData] = []

        def input_fpath(fname: str) -> Path:
            return INPUT_DIR.joinpath(fname)

        with open(input_fpath("courses.csv")) as f:
            input_data += parse_courses(f)

        with open(input_fpath("curricula.csv")) as cf, open(
            input_fpath("curricula_components.csv")
        ) as ccf:
            input_data += parse_curricula(cf, ccf)

        with open(input_fpath("joint.csv")) as jf:
            input_data += parse_joint(jf)

        with open(input_fpath("schedule.csv")) as wf:
            input_data += ime_parse_schedule(wf)

        with open(input_fpath("workload.csv")) as wf:
            input_data += ime_parse_workload(wf)

        return input_data
