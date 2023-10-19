from abc import ABC, abstractmethod
from typing import Callable, Optional

from clingo import Control, Model, SolveResult

from ime_usp_class_scheduler.configuration import Configuration
from ime_usp_class_scheduler.log import LOG_WARN
from ime_usp_class_scheduler.model.input import InputDataset, TeacherScheduleData


class Solver(ABC):
    """An interface to configure, load, run and the underlying ASP solver."""

    def __init__(self) -> None:
        """Initialize and configure the underlying solver."""
        self.dataset: Optional[InputDataset] = None
        self._model = ""

    @property
    def program(self) -> str:
        """Returns the string representation of the program."""

        def header(header: str) -> str:
            return f"% --- {header.upper()} ---\n"

        program = ""
        program += header("inputs")
        if self.dataset:
            program += self.dataset.into_str()
        else:
            program += "% No input added yet"

        program += "\n" + header("model")
        program += self._model
        return program

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

    def load_input(self, dataset: InputDataset) -> None:
        """Loads an input dataset into the solver.

        This function can add extra information to the dataset in case of
        incomplete or missing data.
        """
        # Add TeacherScheduleData for course lecturers missing in InputDataset.
        for workload in dataset.workloads:
            for teacher_id in workload.teachers_id:
                if not [t for t in dataset.schedules if t.teacher_id == teacher_id]:
                    teacher = TeacherScheduleData(teacher_id)
                    dataset.schedules.append(teacher)
        self.dataset = dataset

    def load_model(self, model: str) -> None:
        """Loads a string representation of the model into the solver."""
        self._model = model


class CliSolver(Solver):
    """An implementation of Solver aimed at CLI applications."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize and configure the Potassco clingo solver."""
        super().__init__()
        self.configuration = configuration

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
        control.configuration.solve.models = self.configuration.clingo.num_models  # type: ignore[union-attr]
        control.configuration.solve.parallel_mode = self.configuration.clingo.threads  # type: ignore[union-attr]

        if self.dataset is None:
            LOG_WARN("Running the solver without any inputs.")

        control.add(self.program)
        control.ground()

        with control.solve(on_model=on_model, async_=True) as handle:  # type: ignore[union-attr]
            handle.wait(self.configuration.clingo.time_limit)
            handle.cancel()
            result = handle.get()
            on_finish(result)
