from cover_letter_generator.models.text_parts import IntroOutroKind, IntroOutroTextPart, Tech, TextPart, TextPartTech


def test_text_part_stores_text() -> None:
    part = TextPart(text="Hello")
    assert part.text == "Hello"


def test_intro_outro_replace_placeholder() -> None:
    part = IntroOutroTextPart(text="Hello {name}")
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


def test_intro_outro_serialization_roundtrip() -> None:
    part = IntroOutroTextPart(text="Hello", intro_outro=IntroOutroKind.OUTRO)

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert isinstance(restored, IntroOutroTextPart)
    assert restored.intro_outro == IntroOutroKind.OUTRO


def test_text_part_tech_deserialization_roundtrip() -> None:
    part = TextPartTech(text="Built APIs", tech=Tech(name="Python"))

    payload = part.to_dict()
    restored = TextPart.from_dict(payload)

    assert isinstance(restored, TextPartTech)
    assert restored.tech.name == "Python"
