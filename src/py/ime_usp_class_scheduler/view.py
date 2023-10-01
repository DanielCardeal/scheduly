from __future__ import annotations

from abc import ABC, abstractmethod

from clingo import Model, SymbolType
from tabulate import tabulate

from ime_usp_class_scheduler.model.data import (
    ClassData,
    ConflictData,
    JointedData,
    Period,
    Weekday,
)


class ModelView(ABC):
    """Objects that are capable of displaying a clingo.Model"""

    classes: set[ClassData]
    conflicts: set[ConflictData]
    jointed: set[JointedData]

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def show_model(self, model: Model) -> None:
        """Displays a model."""
        ...

    def _update_model(self, model: Model) -> None:
        """Load new model information into the object."""
        self.classes: set[ClassData] = set()
        self.conflicts: set[ConflictData] = set()
        self.jointed: set[JointedData] = set()

        for symbol in model.symbols(shown=True):
            if symbol.type is not SymbolType.Function:
                continue
            match symbol.name:
                case "class":
                    self.classes.add(ClassData.from_asp(symbol))
                case "jointed":
                    self.jointed.add(JointedData.from_asp(symbol))
                case "conflict":
                    self.conflicts.add(ConflictData.from_asp(symbol))
                case _:
                    pass


class TabulateView(ModelView):
    """Base class for model viewers using the `tabulate` package."""

    def __init__(self) -> None:
        super().__init__()
        self.schedule: dict[Weekday, dict[Period, list[str]]] = {}
        self._clear_schedule()

    def _clear_schedule(self) -> None:
        """Remove all classes from the schedule."""
        self.schedule = {day: {period: [] for period in Period} for day in Weekday}

    def _update_model(self, model: Model) -> None:
        """Load new model information into the object."""
        super()._update_model(model)
        self._clear_schedule()
        for c in self.classes:
            self.schedule[c.weekday][c.period].append(c.course_id)


class CliTabulateView(TabulateView):
    """Model viewer that displays models as pretty CLI tables."""

    def show_model(self, model: Model) -> None:
        """Displays the model as a pretty CLI table."""
        self._update_model(model)
        print(f'Optimization: {",".join([str(cost) for cost in model.cost])}')
        print()

        header = ["Period", *[str(w) for w in Weekday]]
        body = []
        for p in Period:
            row = [str(p)]
            for w in Weekday:
                row.append("\n".join(self.schedule[w][p]))
            body.append(row)

        print(tabulate(body, headers=header, tablefmt="fancy_grid"))
