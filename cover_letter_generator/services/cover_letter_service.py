"""Business logic for cover letter generation."""

from __future__ import annotations

from cover_letter_generator.models.text_parts import IntroOutroKind, IntroOutroTextPart, TextPartTech


class CoverLetterService:
    """Builds a cover letter from persisted text parts."""

    def compose_cover_letter(
        self,
        job_title: str,
        company: str,
        intro_parts: list[IntroOutroTextPart],
        tech_parts: list[TextPartTech],
        outro_parts: list[IntroOutroTextPart],
    ) -> str:
        role = job_title or "the role"
        org = company or "your company"

        ordered_intro_parts = [part for part in intro_parts if part.intro_outro == IntroOutroKind.INTRO]
        ordered_outro_parts = [part for part in outro_parts if part.intro_outro == IntroOutroKind.OUTRO]

        rendered_intro = [self._render_text(part.text, role, org) for part in ordered_intro_parts]
        rendered_body = [part.text for part in tech_parts]
        rendered_outro = [self._render_text(part.text, role, org) for part in ordered_outro_parts]

        sections = rendered_intro + rendered_body + rendered_outro
        return "\n\n".join(section.strip() for section in sections if section.strip())

    def _render_text(self, text: str, job_title: str, company: str) -> str:
        return (
            text.replace("{job_title}", job_title)
            .replace("{company}", company)
            .replace("{company_name}", company)
        )
