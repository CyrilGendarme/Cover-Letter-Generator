"""Application bootstrap and lifecycle wiring."""

from cover_letter_generator.gui.main_window import MainWindow
from cover_letter_generator.services.cover_letter_service import CoverLetterService
from cover_letter_generator.services.json_data_store import JsonDataStore


class CoverLetterApp:
    """Coordinates app dependencies and starts the UI."""

    def __init__(self) -> None:
        service = CoverLetterService()
        data_store = JsonDataStore()
        self._window = MainWindow(service=service, data_store=data_store)

    def run(self) -> None:
        self._window.start()
