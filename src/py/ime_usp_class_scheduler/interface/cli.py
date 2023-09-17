from __future__ import annotations

import os

from clingo import Control, Symbol

from ime_usp_class_scheduler.constants import INPUT_DIR
from ime_usp_class_scheduler.model.data import ASPData
from ime_usp_class_scheduler.parser import (
    ime_parse_schedule,
    ime_parse_workload,
    parse_courses,
    parse_curricula,
    parse_joint,
)


class CliInterface:
    def __init__(
        self,
        num_models: int,
        n_threads: int,
    ):
        self.ctl = Control()
        self.ctl.configuration.solve.opt_mode = "optN"  # type: ignore[union-attr]
        self.ctl.configuration.solve.models = num_models  # type: ignore[union-attr]
        self.ctl.configuration.solve.parallel_mode = n_threads  # type: ignore[union-attr]

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

        def input_fpath(fname):
            return os.path.join(INPUT_DIR, fname)

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
