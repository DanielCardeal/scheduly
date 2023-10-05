from __future__ import annotations

from abc import ABC, abstractmethod

from clingo import SymbolType
from rich.table import Table

from ime_usp_class_scheduler.model import (
    ClassData,
    ConflictData,
    JointedData,
    ModelResult,
    Period,
    Weekday,
)
from ime_usp_class_scheduler.terminal import CONSOLE


class ModelView(ABC):
    """Objects that are capable of displaying a clingo.Model"""

    classes: set[ClassData]
    conflicts: set[ConflictData]
    jointed: dict[str, str]

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def show_model(self, model: ModelResult) -> None:
        """Displays a model."""
        ...

    def _update_model(self, model: ModelResult) -> None:
        """Load new model information into the object."""
        self.classes = set()
        self.conflicts = set()
        self.jointed = dict()

        for symbol in model.symbols:
            if symbol.type is not SymbolType.Function:
                continue
            match symbol.name:
                case "class":
                    self.classes.add(ClassData.from_asp(symbol))
                case "joint":
                    jointed_classes = JointedData.from_asp(symbol)
                    self.jointed[
                        jointed_classes.course_id_a
                    ] = jointed_classes.course_id_b
                    self.jointed[
                        jointed_classes.course_id_b
                    ] = jointed_classes.course_id_a
                case "conflict":
                    self.conflicts.add(ConflictData.from_asp(symbol))
                case _:
                    pass


class CliTabularView(ModelView):
    """Model viewer that displays models as pretty CLI tables."""

    def __init__(self) -> None:
        super().__init__()
        self.schedule: dict[Weekday, dict[Period, set[str]]] = {}
        self._clear_schedule()

    def _clear_schedule(self) -> None:
        """Remove all classes from the schedule."""
        self.schedule = {day: {period: set() for period in Period} for day in Weekday}

    def _update_model(self, model: ModelResult) -> None:
        """Load new model information into the object."""
        super()._update_model(model)
        self._clear_schedule()
        for class_ in self.classes:
            if class_.course_id not in self.jointed:
                self.schedule[class_.weekday][class_.period].add(class_.course_id)
                continue

            # Pretty printing jointed classes:
            # - The first of the jointed classes that is found is added to the
            #   schedule to mark it has been seen.
            # - The second of the jointed class that is found removes the first
            #   one and adds the pretty version (macXXX - macYYY) to the schedule
            jointed_class = self.jointed[class_.course_id]
            if jointed_class not in self.schedule[class_.weekday][class_.period]:
                # First jointed class found
                self.schedule[class_.weekday][class_.period].add(class_.course_id)
            else:
                # Second jointed class found
                self.schedule[class_.weekday][class_.period].remove(jointed_class)
                self.schedule[class_.weekday][class_.period].add(
                    f"{class_.course_id} - {jointed_class}"
                )

    def show_model(self, model: ModelResult) -> None:
        """Displays the model as a pretty CLI table."""
        self._update_model(model)

        headers = ["Period", *[str(w) for w in Weekday]]
        table = Table(
            *headers,
            title=f"Optimization: {model.cost}",
        )
        for p in Period:
            row = [str(p)]
            for w in Weekday:
                row.append("\n".join(self.schedule[w][p]))
            table.add_row(*row)

        CONSOLE.print(table)
