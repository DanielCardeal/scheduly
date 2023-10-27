from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from clingo import SymbolType
from rich.box import ROUNDED
from rich.table import Table

from ime_usp_class_scheduler.log import CONSOLE
from ime_usp_class_scheduler.model.common import Period, Weekday
from ime_usp_class_scheduler.model.output import (
    ClassData,
    ConflictData,
    JointedData,
    ModelResult,
)

MAX_OFFERING_GROUP_LENGTH = 20


class ModelView(ABC):
    """Objects that are capable of displaying a clingo.Model"""

    classes: set[ClassData]
    conflicts: set[ConflictData]
    jointed: dict[tuple[str, str], str]

    def __init__(self) -> None:
        super().__init__()
        self.schedule: dict[Weekday, dict[Period, set[str]]] = {}
        self.symbols: dict[str, list[list[Any]]] = {}
        self._clear_schedule()

    @abstractmethod
    def show_model(self, model: ModelResult) -> None:
        """Displays a model."""
        ...

    def _clear_schedule(self) -> None:
        """Remove all classes from the schedule."""
        self.schedule = {day: {period: set() for period in Period} for day in Weekday}
        self.symbols = {}

    def _update_schedule(self, model: ModelResult) -> None:
        """Load new model information into the object."""
        self._clear_schedule()
        self.classes = set()
        self.conflicts = set()
        self.jointed = dict()

        for symbol in model.symbols:
            if symbol.type is not SymbolType.Function:
                continue
            match symbol.name:
                case "class":
                    self.classes.add(ClassData.from_asp(symbol))
                case "_joint":
                    jointed_classes = JointedData.from_asp(symbol)
                    self.jointed[
                        (jointed_classes.course_id_a, jointed_classes.offering_group)
                    ] = jointed_classes.course_id_b
                    self.jointed[
                        (jointed_classes.course_id_b, jointed_classes.offering_group)
                    ] = jointed_classes.course_id_a


class CliTabularView(ModelView):
    """Model viewer that displays models as pretty CLI tables."""

    def _update_schedule(self, model: ModelResult) -> None:
        super()._update_schedule(model)

        for class_ in self.classes:
            class_str = f"{class_.course_id} ({class_.offering_group[:MAX_OFFERING_GROUP_LENGTH]})"
            if (class_.course_id, class_.offering_group) in self.jointed:
                class_str += " *"
            self.schedule[class_.weekday][class_.period].add(class_str)

    def show_model(self, model: ModelResult) -> None:
        """Displays the model as a pretty CLI table."""
        self._update_schedule(model)

        headers = ["Period", *[str(w) for w in Weekday]]
        table = Table(
            *headers,
            title=f"Optimization: {model.cost}",
            box=ROUNDED,
            show_lines=True,
        )
        for p in Period:
            row = [str(p)]
            for w in Weekday:
                row.append("\n".join(self.schedule[w][p]))
            table.add_row(*row)

        CONSOLE.print(table)
        CONSOLE.print()
