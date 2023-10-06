from abc import ABC, abstractmethod, abstractproperty
from typing import Callable

from clingo import Control, Model, SolveResult

from ime_usp_class_scheduler.configuration import Configuration


class Solver(ABC):
    """An interface to configure, load, run and the underlying ASP solver."""

    @abstractmethod
    def __init__(self, configuration: Configuration) -> None:
        """Initialize and configure the underlying solver."""
        ...

    @abstractmethod
    def load(self, program: str) -> None:
        """Extends the underlying model with the string form of a logic program"""
        ...

    @abstractproperty
    def model(self) -> str:
        """Returns the string representation of the model."""
        ...

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


class DefaultSolver(Solver):
    """The default implementation of Solver.

    This implementation uses the Potassco clingo as the underlying solving
    mechanism.
    """

    def __init__(self, configuration: Configuration) -> None:
        """Initialize and configure the Potassco clingo solver."""
        self._control = Control()
        self._time_limit = configuration.clingo.time_limit
        self._model = ""

        # set clingo solving options
        self._control.configuration.solve.opt_mode = "optN"  # type: ignore[union-attr]
        self._control.configuration.solve.models = configuration.clingo.num_models  # type: ignore[union-attr]
        self._control.configuration.solve.parallel_mode = configuration.clingo.threads  # type: ignore[union-attr]

    def load(self, program: str) -> None:
        """Extends the underlying model with the string form of a logic program"""
        self._model += program + "\n"
        self._control.add(program)

    def model(self) -> str:
        """Returns the string representation of the model."""
        return self._model

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
        self._control.ground()
        with self._control.solve(on_model=on_model, async_=True) as handle:  # type: ignore[union-attr]
            handle.wait(self._time_limit)
            handle.cancel()
            result = handle.get()
            on_finish(result)
