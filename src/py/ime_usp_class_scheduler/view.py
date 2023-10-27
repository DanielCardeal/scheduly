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
    jointed: set[JointedData]

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
        self.jointed = set()

        for symbol in model.symbols:
            if symbol.type is not SymbolType.Function:
                continue
            match symbol.name:
                case "class":
                    self.classes.add(ClassData.from_asp(symbol))
                case "_joint":
                    self.jointed.add(JointedData.from_asp(symbol))


class CliTabularView(ModelView):
    """Model viewer that displays models as pretty CLI tables."""

    def _update_schedule(self, model: ModelResult) -> None:
        super()._update_schedule(model)

        # Get a mapping from (course, offering) -> set of jointed classes
        joint_mapping: dict[tuple[str, str], set[str]] = dict()
        for j in self.jointed:
            seen_a = (j.course_id_a, j.offering_group) in joint_mapping
            seen_b = (j.course_id_b, j.offering_group) in joint_mapping
            if not seen_a and not seen_b:
                s = {j.course_id_a, j.course_id_b}
                joint_mapping[(j.course_id_a, j.offering_group)] = s
                joint_mapping[(j.course_id_b, j.offering_group)] = s
            elif seen_a and not seen_b:
                s = joint_mapping[(j.course_id_a, j.offering_group)]
                joint_mapping[(j.course_id_b, j.offering_group)] = s
                s.add(j.course_id_b)
            elif not seen_a and not seen_b:
                s = joint_mapping[(j.course_id_b, j.offering_group)]
                joint_mapping[(j.course_id_a, j.offering_group)] = s
                s.add(j.course_id_a)
            elif seen_a and seen_b:
                # Both exist: unify both the sets into one set
                s1 = joint_mapping[(j.course_id_a, j.offering_group)]
                s2 = joint_mapping[(j.course_id_b, j.offering_group)]
                s1.update(s2)
                for course_id in s2:
                    joint_mapping[(course_id, j.offering_group)] = s1

        # Fill the schedule, marking already added classes in the `courses` dict:
        # courses[course_id, offering group, weekday, period] = was already added?
        courses: dict[tuple[str, str, int, int], bool] = dict()
        for class_ in self.classes:
            if (
                class_.course_id,
                class_.offering_group,
                class_.weekday,
                class_.period,
            ) in courses:
                # Ignores already added classes
                continue

            class_str: str
            if (class_.course_id, class_.offering_group) in joint_mapping:
                # Dealing with a jointed class
                jointed_classes = joint_mapping[class_.course_id, class_.offering_group]
                class_str = " - ".join(jointed_classes)
                for course_id in jointed_classes:
                    courses[
                        course_id,
                        class_.offering_group,
                        class_.weekday,
                        class_.period,
                    ] = True
            else:
                # Non jointed classes
                class_str = f"{class_.course_id}"
                courses[
                    class_.course_id,
                    class_.offering_group,
                    class_.weekday,
                    class_.period,
                ] = True

            class_str += f" ({class_.offering_group[:MAX_OFFERING_GROUP_LENGTH]})"
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
