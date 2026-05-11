from pathlib import Path

from cover_letter_generator.models.text_parts import (
    TextPartKind,
    TextPartNonTech,
    Tech,
    TextPart,
    TextPartTech,
)
from cover_letter_generator.services.json_data_store import JsonDataStore


def test_json_data_store_tech_crud(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)

    store.add_tech(Tech(name="Python", text_parts=["FastAPI", "Automation"]))
    techs = store.load_techs()

    assert len(techs) == 1
    assert techs[0].name == "Python"
    assert techs[0].text_parts == ["FastAPI", "Automation"]

    assert store.update_tech(0, Tech(name="Django", text_parts=["Web"]))
    assert store.load_techs()[0].name == "Django"

    assert store.remove_tech(0)
    assert store.load_techs() == []


def test_json_data_store_text_part_crud(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)

    store.add_text_part(
        TextPart(
            text="Intro paragraph",
            name="Intro block",
            french_text="Paragraphe d'introduction",
        )
    )
    parts = store.load_text_parts()

    assert len(parts) == 1
    assert parts[0].text == "Intro paragraph"
    assert parts[0].name == "Intro block"
    assert parts[0].french_text == "Paragraphe d'introduction"

    assert store.update_text_part(0, TextPart(text="Updated intro"))
    assert store.load_text_parts()[0].text == "Updated intro"

    assert store.remove_text_part(0)
    assert store.load_text_parts() == []


def test_upsert_tech_by_name_updates_existing(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)
    store.add_tech(Tech(name="Python", text_parts=["FastAPI"]))

    result = store.upsert_tech_by_name(Tech(name="python", text_parts=["Flask"]))
    techs = store.load_techs()

    assert result == "modified"
    assert len(techs) == 1
    assert techs[0].name == "python"
    assert techs[0].text_parts == ["Flask"]


def test_upsert_text_part_by_text_deduplicates(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)
    store.add_text_part(TextPart(text="Intro"))

    result = store.upsert_text_part_by_text(TextPart(text="Intro"))
    parts = store.load_text_parts()

    assert result == "modified"
    assert len(parts) == 1


def test_json_data_store_persists_text_part_associations(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)
    store.add_text_part(
        TextPartNonTech(text="Intro", text_part_kind=TextPartKind.INTRO)
    )
    store.add_text_part(
        TextPartTech(text="Tech line", tech=Tech(name="Python"), always_include=True)
    )

    parts = store.load_text_parts()

    assert isinstance(parts[0], TextPartNonTech)
    assert parts[0].text_part_kind == TextPartKind.INTRO
    assert isinstance(parts[1], TextPartTech)
    assert parts[1].tech.name == "Python"
    assert parts[1].always_include is True


def test_json_data_store_persists_export_directory(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)

    target_dir = str(tmp_path / "exports")
    store.save_export_directory(target_dir)

    reloaded_store = JsonDataStore(base_dir=tmp_path)
    assert reloaded_store.load_export_directory() == target_dir


def test_json_data_store_overwrites_export_directory(tmp_path: Path) -> None:
    store = JsonDataStore(base_dir=tmp_path)

    first_dir = str(tmp_path / "first")
    second_dir = str(tmp_path / "second")
    store.save_export_directory(first_dir)
    store.save_export_directory(second_dir)

    assert store.load_export_directory() == second_dir
