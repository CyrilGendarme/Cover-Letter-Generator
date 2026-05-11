from cover_letter_generator.models.text_parts import (
    TextPartKind,
    TextPartNonTech,
    Tech,
    TextPart,
    TextPartTech,
)

def test_text_part_stores_text() -> None:
    part = TextPart(text="Hello")
    assert part.text == "Hello"


def test_text_part_name_roundtrip() -> None:
    part = TextPart(text="Hello", name="custom", french_text="Bonjour")

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert restored.name == "custom"
    assert restored.french_text == "Bonjour"


def test_text_part_kind_replace_placeholder() -> None:
    part = TextPartNonTech(text="Hello {name}")
    result = part.replace_placeholder("{name}", "Cyril")

    assert result == "Hello Cyril"
    assert part.text == "Hello Cyril"


def test_text_part_tech_links_tech() -> None:
    part = TextPartTech(text="Experienced with Python", tech=Tech(name="Python"))

    assert part.tech.name == "Python"


def test_tech_serialization_roundtrip() -> None:
    tech = Tech(name="Python", text_parts=["Automation", "Data"])

    payload = tech.to_dict()
    restored = Tech.from_dict(payload)

    assert restored.name == "Python"
    assert restored.text_parts == ["Automation", "Data"]


def test_text_part_serialization_roundtrip() -> None:
    part = TextPart(text="Sample text")

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert restored.text == "Sample text"


def test_text_part_kind_serialization_roundtrip() -> None:
    part = TextPartNonTech(text="Hello", text_part_kind=TextPartKind.OUTRO)

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert isinstance(restored, TextPartNonTech)
    assert restored.text_part_kind == TextPartKind.OUTRO


def test_text_part_tech_deserialization_roundtrip() -> None:
    part = TextPartTech(
        text="Built APIs",
        name="Backend APIs",
        french_text="J'ai construit des API",
        tech=Tech(name="Python"),
        always_include=True,
    )

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert isinstance(restored, TextPartTech)
    assert restored.tech.name == "Python"
    assert restored.always_include is True
    assert restored.identifier() == "Backend APIs"
    assert restored.french_text == "J'ai construit des API"


def test_identifier_fallbacks() -> None:
    tech_part = TextPartTech(text="X", tech=Tech(name="Python"))
    non_tech_part = TextPartNonTech(text="Y", text_part_kind=TextPartKind.OUTRO)

    assert tech_part.identifier() == "Python"
    assert non_tech_part.identifier() == "outro"
