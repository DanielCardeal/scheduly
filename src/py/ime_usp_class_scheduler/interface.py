from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path

from clingo import Control, Model, SolveResult

from ime_usp_class_scheduler.configuration import Configuration
from ime_usp_class_scheduler.console import console, log_info
from ime_usp_class_scheduler.constants import (
    CONSTRAINTS_DIR,
    HARD_CONSTRAINTS_DIR,
    INPUT_DIR,
    SOFT_CONSTRAINTS_DIR,
)
from ime_usp_class_scheduler.model import (
    IntoASP,
    ModelResult,
    TeacherData,
    WorkloadData,
    generate_full_availability,
)
from ime_usp_class_scheduler.parser import (
    ime_parse_schedule,
    ime_parse_workload,
    parse_courses,
    parse_curricula,
    parse_joint,
)
from ime_usp_class_scheduler.view import CliTabularView, ModelView


class SolverInterface(ABC):
    """An interface for the underlying clingo solver.

    The SolverInterface class is the sole responsible for running and
    displaying results of a clingo solution search.
    """

    _MODEL_BASE_PATHS = [
        CONSTRAINTS_DIR.joinpath(path).with_suffix(".lp")
        for path in ("aliases", "base")
    ]

    _model_viewer: ModelView

    def __init__(self, configuration: Configuration):
        self.configuration = configuration

        # Set clingo options
        self._control = Control()
        self._control.configuration.solve.opt_mode = "optN"  # type: ignore[union-attr]
        self._control.configuration.solve.models = configuration.clingo.num_models  # type: ignore[union-attr]
        self._control.configuration.solve.parallel_mode = configuration.clingo.threads  # type: ignore[union-attr]

        self.time_limit = configuration.clingo.time_limit
        self._best_models: deque[ModelResult] = deque(
            maxlen=configuration.clingo.num_models
        )

        # Build ASP program
        def header(header: str) -> str:
            return f"\n% --- {header.upper()} --- \n"

        program = ""

        self.raw_inputs = self._load_inputs()
        program += header("inputs")
        program += self.asp_inputs

        program += header("model")
        program += self._load_model()

        self.program = program
        self._control.add(self.program)

    @property
    def asp_inputs(self) -> str:
        """Return the ASP code representation of the raw input data."""
        return "\n".join((raw_input.into_asp() for raw_input in self.raw_inputs))

    @abstractmethod
    def _on_model(self, model: Model) -> None:
        """Callback for intercepting models generated from the ASP solver."""
        self._best_models.append(ModelResult(model.symbols(shown=True), model.cost))

    @abstractmethod
    def _on_finish(self, result: SolveResult) -> None:
        """Callback called once the search has concluded."""
        ...

    def run(self) -> None:
        """Begin searching for solutions using the Clingo solver."""
        self._control.ground()
        with self._control.solve(on_model=self._on_model, async_=True) as handle:  # type: ignore[union-attr]
            handle.wait(self.time_limit)
            # log_info(f"Reached the time limit of {self.time_limit} seconds.")
            # log_info("Stopping the solver...")
            handle.cancel()
            result = handle.get()
            self._on_finish(result)

    def save_model(self, output_path: Path) -> None:
        """Write compiled ASP model (inputs and constraints) to a file."""
        with open(output_path, "w") as f:
            f.write(self.program)

    def _load_inputs(self) -> list[IntoASP]:
        """
        Import data from INPUT_DIR using the appropriate parsers.

        This function might add some extra information that is implied by the
        data loaded from the parsers, for example, it adds full availability
        for teachers with no available teaching periods.
        """
        input_data: list[IntoASP] = []

        def input_fpath(fname: str) -> Path:
            return INPUT_DIR.joinpath(fname)

        try:
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
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Unable to find required input file {e.filename}.")

        # Add full availability for lecturers without availability information
        full_availability = generate_full_availability()

        lecturers = set()
        for teacher in input_data:
            match teacher:
                case WorkloadData(teacher_id=teacher_id):
                    lecturers.add(teacher_id)

        for idx, teacher in enumerate(input_data):
            if not isinstance(teacher, TeacherData):
                continue
            elif len(teacher.available_time) > 0:
                lecturers.remove(teacher.teacher_id)
            else:
                input_data[idx] = TeacherData(
                    teacher.teacher_id, full_availability, teacher.preferred_time
                )
                lecturers.remove(teacher.teacher_id)

        for teacher_id in lecturers:  # Teachers with no associated TeacherData
            input_data.append(TeacherData(teacher_id, full_availability, set()))

        return input_data

    def _load_model(self) -> str:
        """Load the ASP model (base + hard and soft constraints) based on user configuration."""
        model = ""

        # Load constraints
        paths = self._MODEL_BASE_PATHS.copy()
        paths += [
            HARD_CONSTRAINTS_DIR.joinpath(constraint_cfg.path)
            for constraint_cfg in self.configuration.constraints.hard
        ]
        paths += [
            SOFT_CONSTRAINTS_DIR.joinpath(constraint_cfg.path)
            for constraint_cfg in self.configuration.constraints.soft
        ]

        try:
            for path in paths:
                with open(path) as f:
                    model += f.read() + "\n"
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Unable to find constraint file {e.filename}.")

        # Setup weights and and priorities
        for soft_cfg in self.configuration.constraints.soft:
            weight = f"#const w_{soft_cfg.name} = {soft_cfg.weight}.\n"
            priority = f"#const p_{soft_cfg.name} = {soft_cfg.priority}.\n"
            model += weight + priority

        return model


class CliInterface(SolverInterface):
    """An implementation of the SolverInterface that is built for command-line
    environments.
    """

    def __init__(self, configuration: Configuration) -> None:
        super().__init__(configuration)
        self._model_viewer = CliTabularView()

    def _on_model(self, model: Model) -> None:
        """Callback for intercepting models generated from the ASP solver."""
        super()._on_model(model)
        log_info(f"Current optimization: {model.cost}")

    def _on_finish(self, result: SolveResult) -> None:
        """Callback called once the search has concluded."""
        console.rule("solving results")
        log_info(f"Solving status: {result}")
        log_info(f"Showing top {len(self._best_models)} results:")
        for model in self._best_models:
            self._model_viewer.show_model(model)

    def run(self) -> None:
        """Begin searching for solutions using the Clingo solver."""
        with console.status("[bold green]Searching for models..."):
            super().run()
