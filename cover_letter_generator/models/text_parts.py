"""Text part models used by the cover letter generator."""

from dataclasses import dataclass, field
from enum import Enum


class IntroOutroKind(str, Enum):
    """Enum values for intro/outro style text part association."""

    INTRO = "intro"
    OUTRO = "outro"
    BODY = "body"


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

    def to_dict(self) -> dict[str, object]:
        return {"kind": "text", "text": self.text}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TextPart":
        kind = str(data.get("kind", "text")).strip().lower()
        text = str(data.get("text", ""))

        if kind == "tech":
            raw_tech = data.get("tech", {})
            if isinstance(raw_tech, dict):
                tech = Tech.from_dict(raw_tech)
            else:
                tech = Tech(name=str(raw_tech))
            return TextPartTech(text=text, tech=tech)

        if kind == "intro_outro":
            raw_enum = str(data.get("intro_outro", IntroOutroKind.BODY.value)).strip().lower()
            enum_value = IntroOutroKind(raw_enum) if raw_enum in {item.value for item in IntroOutroKind} else IntroOutroKind.BODY
            return IntroOutroTextPart(text=text, intro_outro=enum_value)

        return cls(text=text)


@dataclass
class IntroOutroTextPart(TextPart):
    """Text part that supports placeholder replacement."""

    intro_outro: IntroOutroKind = IntroOutroKind.BODY

    def replace_placeholder(self, placeholder: str, value: str) -> str:
        self.text = self.text.replace(placeholder, value)
        return self.text

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "intro_outro",
            "intro_outro": self.intro_outro.value,
            "text": self.text,
        }


@dataclass
class TextPartTech(TextPart):
    """Text part associated with a specific technology."""

    tech: Tech

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "tech",
            "text": self.text,
            "tech": self.tech.to_dict(),
        }
