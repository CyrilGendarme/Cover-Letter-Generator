"""Business logic for cover letter generation."""

from __future__ import annotations

from cover_letter_generator.models.text_parts import (
    TextPartKind,
    TextPartNonTech,
    TextPartTech,
)

class CoverLetterService:
    """Builds a cover letter from persisted text parts."""

    def compose_cover_letter(
        self,
        job_title: str,
        company: str,
        intro_parts: list[TextPartNonTech] | None = None,
        tech_parts: list[TextPartTech] | None = None,
        outro_parts: list[TextPartNonTech] | None = None,
        non_tech_parts: list[TextPartNonTech] | None = None,
        language: str = "english",
    ) -> str:
        role = job_title or "the role"
        org = company or "your company"
        tech_parts = tech_parts or []
        selected_language = language.strip().lower() or "english"

        if non_tech_parts is None:
            non_tech_parts = (intro_parts or []) + (outro_parts or [])

        pre_body_kinds = [
            TextPartKind.INTRO,
            TextPartKind.APPLICATION_REASON,
            TextPartKind.PERSONNAL_PRESENTATION,
        ]
        post_body_kinds = [TextPartKind.OUTRO, TextPartKind.SIGNATURE]

        ordered_pre_body_parts: list[TextPartNonTech] = []
        for kind in pre_body_kinds:
            ordered_pre_body_parts.extend(
                [part for part in non_tech_parts if part.text_part_kind == kind]
            )

        ordered_post_body_parts: list[TextPartNonTech] = []
        for kind in post_body_kinds:
            ordered_post_body_parts.extend(
                [part for part in non_tech_parts if part.text_part_kind == kind]
            )

        rendered_pre_body = [
            self._render_text(
                self._select_text(part.text, part.french_text, selected_language),
                role,
                org,
            )
            for part in ordered_pre_body_parts
            if self._select_text(part.text, part.french_text, selected_language).strip()
        ]
        rendered_body = []
        for part in tech_parts:
            content = self._select_text(part.text, part.french_text, selected_language)
            if not content.strip():
                continue
            label = part.name.strip()
            if label:
                rendered_body.append(f"- {label}: {content}")
            else:
                rendered_body.append(f"- {content}")
        rendered_post_body = [
            self._render_text(
                self._select_text(part.text, part.french_text, selected_language),
                role,
                org,
            )
            for part in ordered_post_body_parts
            if self._select_text(part.text, part.french_text, selected_language).strip()
        ]

        sections = rendered_pre_body + rendered_body + rendered_post_body
        return "\n\n".join(section for section in sections if section.strip())

    def _render_text(self, text: str, job_title: str, company: str) -> str:
        return (
            text.replace("{job_title}", job_title)
            .replace("{company}", company)
            .replace("{company_name}", company)
            .replace("[POSITION NAME]", job_title)
            .replace("[COMPANY NAME]", company)
        )

    def _select_text(self, english_text: str, french_text: str, language: str) -> str:
        if language == "french":
            return french_text or english_text
        return english_text
