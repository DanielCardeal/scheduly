from __future__ import annotations

from clingo import Model, SolveResult

from ime_usp_class_scheduler.interface.configuration import Configuration
from ime_usp_class_scheduler.interface.SolverInterface import SolverInterface


class CliInterface(SolverInterface):

    def __init__(self, configuration: Configuration) -> None:
        super().__init__(configuration)

    def on_model(self, model: Model) -> None:
        """Callback for intercepting models generated from the ASP solver."""
        pass

    def on_finish(self, result: SolveResult) -> None:
        """Callback called once the search has concluded."""
        print("Best schedules found:")
        for model in self.last_models:
            self.viewer.show_model(model)
