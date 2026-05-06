from pathlib import Path

from cover_letter_generator.models.text_parts import IntroOutroKind, IntroOutroTextPart, Tech, TextPart, TextPartTech
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

    store.add_text_part(TextPart(text="Intro paragraph"))
    parts = store.load_text_parts()

    assert len(parts) == 1
    assert parts[0].text == "Intro paragraph"

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
    store.add_text_part(IntroOutroTextPart(text="Intro", intro_outro=IntroOutroKind.INTRO))
    store.add_text_part(TextPartTech(text="Tech line", tech=Tech(name="Python")))

    parts = store.load_text_parts()

    assert isinstance(parts[0], IntroOutroTextPart)
    assert parts[0].intro_outro == IntroOutroKind.INTRO
    assert isinstance(parts[1], TextPartTech)
    assert parts[1].tech.name == "Python"
