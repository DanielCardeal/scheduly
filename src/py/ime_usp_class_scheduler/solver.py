from abc import ABC, abstractmethod
from typing import Callable, Optional

from clingo import Control, Model, SolveResult

from ime_usp_class_scheduler.configuration import (
    ClingoOptions,
    ConfigurationException,
    ConstraintSpecification,
)
from ime_usp_class_scheduler.constants import CONSTRAINTS_DIR
from ime_usp_class_scheduler.log import LOG_WARN
from ime_usp_class_scheduler.model.input import InputDataset


class Solver(ABC):
    """An interface to configure, load, run and the underlying ASP solver."""

    _BASE_MODEL_FILES = ["base", "aliases"]

    def __init__(
        self,
        options: ClingoOptions,
        /,
        inputs: Optional[InputDataset] = None,
        constraints: Optional[ConstraintSpecification] = None,
    ) -> None:
        """Initialize and configure the underlying solver."""
        self.options = options
        self.inputs = inputs
        self.constraints = constraints

        # Load base model
        base = ""
        for filename in self._BASE_MODEL_FILES:
            path = CONSTRAINTS_DIR.joinpath(filename).with_suffix(".lp")
            try:
                with open(path) as base_file:
                    base += base_file.read() + "\n"
            except IOError as e:
                raise ConfigurationException(
                    f"Unable to load base model file '{filename}' from {path}: {e}"
                )
        self._base = base

    @abstractmethod
    def run(
        self,
        on_model: Callable[[Model], bool | None],
        on_finish: Callable[[SolveResult], None],
    ) -> None:
        """Run the solver, sending intermediate models through the on_model
        callback.
        """
        ...

    @property
    def program(self) -> str:
        """Returns the string representation of the program."""

        def header(header: str) -> str:
            return f"% --- {header.upper()} ---\n"

        program = header("inputs")
        if self._inputs:
            program += self._inputs.into_str()
        else:
            program += "% NO INPUTS ADDED\n"

        program += "\n"
        program += header("base model")
        program += self._base

        program += "\n"
        program += header("constraints")
        if self.constraints:
            program += self.constraints.into_asp()
        else:
            program += "% NO CONSTRAINTS ADDED\n"

        return program

    @property
    def inputs(self) -> Optional[InputDataset]:
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: Optional[InputDataset]) -> None:
        """Loads an input dataset into the solver.

        This setter can add extra information to the dataset in case of
        incomplete or missing data.
        """
        if inputs:
            inputs.validate_and_normalize()
        self._inputs = inputs


class CliSolver(Solver):
    """An implementation of Solver aimed at CLI applications."""

    def run(
        self,
        on_model: Callable[[Model], bool | None],
        on_finish: Callable[[SolveResult], None],
    ) -> None:
        """Run the solver, sending intermediate models through the on_model
        callback.

        Arguments:
            on_model: callback for intercepting models. Can cancel the search by returning False.
            on_finish: callback run after the solve is concluded or canceled
        """
        control = Control()

        control.configuration.solve.opt_mode = "optN"  # type: ignore[union-attr]
        control.configuration.solve.models = self.options.num_models  # type: ignore[union-attr]
        control.configuration.solve.parallel_mode = self.options.threads  # type: ignore[union-attr]

        if self.inputs is None:
            LOG_WARN("Running the solver without any inputs.")

        control.add(self.program)
        control.ground()

        with control.solve(on_model=on_model, async_=True) as handle:  # type: ignore[union-attr]
            handle.wait(self.options.time_limit)
            handle.cancel()
            result = handle.get()
            on_finish(result)
