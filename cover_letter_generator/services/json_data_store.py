"""Simple JSON persistence for Tech and TextPart entities."""

from __future__ import annotations

import json
from pathlib import Path

from cover_letter_generator.models.text_parts import Tech, TextPart


class JsonDataStore:
    """Persists model lists in JSON files."""

    def __init__(self, base_dir: Path | None = None) -> None:
        root_dir = Path(__file__).resolve().parents[2]
        self._data_dir = base_dir or (root_dir / "data")
        self._techs_file = self._data_dir / "techs.json"
        self._text_parts_file = self._data_dir / "text_parts.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if not self._techs_file.exists():
            self._write_json(self._techs_file, [])
        if not self._text_parts_file.exists():
            self._write_json(self._text_parts_file, [])

    def _read_json(self, path: Path) -> list[dict[str, object]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                raw = json.load(file)
        except (json.JSONDecodeError, OSError):
            return []
        return raw if isinstance(raw, list) else []

    def _write_json(self, path: Path, payload: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def load_techs(self) -> list[Tech]:
        return [Tech.from_dict(item) for item in self._read_json(self._techs_file)]

    def save_techs(self, techs: list[Tech]) -> None:
        self._write_json(self._techs_file, [tech.to_dict() for tech in techs])

    def add_tech(self, tech: Tech) -> None:
        techs = self.load_techs()
        techs.append(tech)
        self.save_techs(techs)

    def upsert_tech_by_name(self, tech: Tech) -> str:
        techs = self.load_techs()
        target = tech.name.strip().lower()
        for index, existing in enumerate(techs):
            if existing.name.strip().lower() == target:
                techs[index] = tech
                self.save_techs(techs)
                return "modified"
        techs.append(tech)
        self.save_techs(techs)
        return "added"

    def update_tech(self, index: int, tech: Tech) -> bool:
        techs = self.load_techs()
        if index < 0 or index >= len(techs):
            return False
        techs[index] = tech
        self.save_techs(techs)
        return True

    def remove_tech(self, index: int) -> bool:
        techs = self.load_techs()
        if index < 0 or index >= len(techs):
            return False
        techs.pop(index)
        self.save_techs(techs)
        return True

    def load_text_parts(self) -> list[TextPart]:
        return [TextPart.from_dict(item) for item in self._read_json(self._text_parts_file)]

    def save_text_parts(self, text_parts: list[TextPart]) -> None:
        self._write_json(self._text_parts_file, [part.to_dict() for part in text_parts])

    def add_text_part(self, text_part: TextPart) -> None:
        text_parts = self.load_text_parts()
        text_parts.append(text_part)
        self.save_text_parts(text_parts)

    def upsert_text_part_by_text(self, text_part: TextPart) -> str:
        text_parts = self.load_text_parts()
        target = text_part.text.strip()
        for index, existing in enumerate(text_parts):
            if existing.text.strip() == target:
                text_parts[index] = text_part
                self.save_text_parts(text_parts)
                return "modified"
        text_parts.append(text_part)
        self.save_text_parts(text_parts)
        return "added"

    def update_text_part(self, index: int, text_part: TextPart) -> bool:
        text_parts = self.load_text_parts()
        if index < 0 or index >= len(text_parts):
            return False
        text_parts[index] = text_part
        self.save_text_parts(text_parts)
        return True

    def remove_text_part(self, index: int) -> bool:
        text_parts = self.load_text_parts()
        if index < 0 or index >= len(text_parts):
            return False
        text_parts.pop(index)
        self.save_text_parts(text_parts)
        return True
