from __future__ import annotations

from clingo import Model, SolveResult

from ime_usp_class_scheduler.console import console, log_info
from ime_usp_class_scheduler.interface.configuration import Configuration
from ime_usp_class_scheduler.interface.SolverInterface import SolverInterface
from ime_usp_class_scheduler.view import CliTabulateView, ModelView


class CliInterface(SolverInterface):
    """An implementation of the SolverInterface that is built for command-line
    environments.
    """

    _model_viewer: CliTabulateView

    def __init__(self, configuration: Configuration) -> None:
        super().__init__(configuration)
        self._model_viewer = CliTabulateView()

    @property
    def model_viewer(self) -> ModelView:
        """Returns the model viewer for the given interface"""
        return self._model_viewer

    def on_model(self, model: Model) -> None:
        """Callback for intercepting models generated from the ASP solver."""
        log_info(f"Current optimization: {model.cost}")

    def on_finish(self, result: SolveResult) -> None:
        """Callback called once the search has concluded."""
        print("Best schedules found:")
        for model in self.last_models:
            self.model_viewer.show_model(model)

    def run(self) -> None:
        """Begin searching for solutions using the Clingo solver."""
        with console.status("[bold green]Searching for models..."):
            super().run()
