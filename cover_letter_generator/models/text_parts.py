"""Text part models used by the cover letter generator."""

from dataclasses import dataclass, field
from enum import Enum


class TextPartKind(str, Enum):
    """Enum values for intro/outro style text part association."""

    INTRO = "intro"
    APPLICATION_REASON = "application_reason"
    PERSONNAL_PRESENTATION = "personal_presentation"
    OUTRO = "outro"
    SIGNATURE = "signature"


@dataclass
class Tech:
    """Represents a technology that can be associated with text."""

    name: str = ""
    text_parts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "text_parts": self.text_parts}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Tech":
        raw_text_parts = data.get("text_parts", [])
        text_parts = [str(item) for item in raw_text_parts] if isinstance(raw_text_parts, list) else []
        return cls(name=str(data.get("name", "")), text_parts=text_parts)


@dataclass
class TextPart:
    """Base text part."""

    text: str
    name: str = ""
    french_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "text",
            "text": self.text,
            "name": self.name,
            "french_text": self.french_text,
        }

    def identifier(self) -> str:
        return self.name or "text"

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TextPart":
        kind = str(data.get("kind", "text")).strip().lower()
        text = str(data.get("text", ""))
        name = str(data.get("name", ""))
        french_text = str(data.get("french_text", ""))

        if kind == "tech":
            raw_tech = data.get("tech", {})
            if isinstance(raw_tech, dict):
                tech = Tech.from_dict(raw_tech)
            else:
                tech = Tech(name=str(raw_tech))
            always_include = bool(data.get("always_include", False))
            return TextPartTech(
                text=text,
                name=name,
                french_text=french_text,
                tech=tech,
                always_include=always_include,
            )

        if kind == "non_tech":
            raw_enum = (
                str(data.get("text_part_kind", TextPartKind.INTRO.value))
                .strip()
                .lower()
            )
            enum_value = (
                TextPartKind(raw_enum)
                if raw_enum in {item.value for item in TextPartKind}
                else TextPartKind.INTRO
            )
            return TextPartNonTech(
                text=text,
                name=name,
                french_text=french_text,
                text_part_kind=enum_value,
            )

        return cls(text=text, name=name, french_text=french_text)


@dataclass
class TextPartNonTech(TextPart):
    """Text part that supports placeholder replacement."""

    text_part_kind: TextPartKind = TextPartKind.INTRO

    def replace_placeholder(self, placeholder: str, value: str) -> str:
        self.text = self.text.replace(placeholder, value)
        return self.text

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "non_tech",
            "text_part_kind": self.text_part_kind.value,
            "text": self.text,
            "name": self.name,
            "french_text": self.french_text,
        }

    def identifier(self) -> str:
        return self.name or self.text_part_kind.value


@dataclass
class TextPartTech(TextPart):
    """Text part associated with a specific technology."""

    tech: Tech = field(default_factory=Tech)
    always_include: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "tech",
            "text": self.text,
            "name": self.name,
            "french_text": self.french_text,
            "tech": self.tech.to_dict(),
            "always_include": self.always_include,
        }

    def identifier(self) -> str:
        return self.name or self.tech.name or "tech"
