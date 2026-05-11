from cover_letter_generator.models.text_parts import (
    TextPartKind,
    TextPartNonTech,
    Tech,
    TextPartTech,
)
from cover_letter_generator.services.cover_letter_service import CoverLetterService


def test_compose_cover_letter_orders_intro_body_outro() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Python Developer",
        company="Acme Corp",
        intro_parts=[
            TextPartNonTech(
                text="Applying for {job_title} at {company}.",
                text_part_kind=TextPartKind.INTRO,
            )
        ],
        tech_parts=[
            TextPartTech(text="Built automation tools.", tech=Tech(name="Python")),
            TextPartTech(
                text="Improved delivery lead times.", tech=Tech(name="Docker")
            ),
        ],
        outro_parts=[
            TextPartNonTech(
                text="Thank you for considering my application for {job_title} at {company_name}.",
                text_part_kind=TextPartKind.OUTRO,
            )
        ],
    )

    assert result.startswith("Applying for Python Developer at Acme Corp.")
    assert "- Built automation tools." in result
    assert "- Improved delivery lead times." in result
    assert result.endswith("Thank you for considering my application for Python Developer at Acme Corp.")


def test_compose_cover_letter_skips_empty_sections() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Python Developer",
        company="Acme Corp",
        intro_parts=[],
        tech_parts=[TextPartTech(text="Built APIs.", tech=Tech(name="Python"))],
        outro_parts=[],
    )

    assert result == "- Built APIs."


def test_compose_cover_letter_replaces_bracket_placeholders() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Backend Engineer",
        company="Globex",
        intro_parts=[
            TextPartNonTech(
                text="Applying for [POSITION NAME] at [COMPANY NAME].",
                text_part_kind=TextPartKind.INTRO,
            )
        ],
        tech_parts=[],
        outro_parts=[],
    )

    assert result == "Applying for Backend Engineer at Globex."


def test_compose_cover_letter_includes_all_non_tech_kinds() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Data Engineer",
        company="Initech",
        tech_parts=[],
        non_tech_parts=[
            TextPartNonTech(text="Intro", text_part_kind=TextPartKind.INTRO),
            TextPartNonTech(
                text="Reason for applying",
                text_part_kind=TextPartKind.APPLICATION_REASON,
            ),
            TextPartNonTech(
                text="Personal presentation",
                text_part_kind=TextPartKind.PERSONNAL_PRESENTATION,
            ),
            TextPartNonTech(text="Outro", text_part_kind=TextPartKind.OUTRO),
            TextPartNonTech(text="Signature", text_part_kind=TextPartKind.SIGNATURE),
        ],
    )

    assert "Intro" in result
    assert "Reason for applying" in result
    assert "Personal presentation" in result
    assert "Outro" in result
    assert "Signature" in result


def test_compose_cover_letter_formats_named_tech_part_bullet() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Software Engineer",
        company="Acme",
        tech_parts=[
            TextPartTech(
                name="Cloud",
                text="Built and operated distributed services.",
                tech=Tech(name="AWS"),
            )
        ],
        non_tech_parts=[],
    )

    assert result == "- Cloud: Built and operated distributed services."


def test_compose_cover_letter_renders_french_text_when_selected() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Developpeur Python",
        company="Acme",
        tech_parts=[
            TextPartTech(
                name="Cloud",
                text="Built and operated distributed services.",
                french_text="J'ai concu et exploite des services distribues.",
                tech=Tech(name="AWS"),
            )
        ],
        non_tech_parts=[
            TextPartNonTech(
                text="Applying for [POSITION NAME] at [COMPANY NAME].",
                french_text="Je postule au poste de [POSITION NAME] chez [COMPANY NAME].",
                text_part_kind=TextPartKind.INTRO,
            )
        ],
        language="french",
    )

    assert "Je postule au poste de Developpeur Python chez Acme." in result
    assert "- Cloud: J'ai concu et exploite des services distribues." in result


def test_compose_cover_letter_french_falls_back_to_english_when_missing() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Backend Engineer",
        company="Globex",
        tech_parts=[TextPartTech(text="Built APIs.", tech=Tech(name="Python"))],
        non_tech_parts=[
            TextPartNonTech(
                text="Applying for [POSITION NAME] at [COMPANY NAME].",
                text_part_kind=TextPartKind.INTRO,
            )
        ],
        language="french",
    )

    assert result == "Applying for Backend Engineer at Globex.\n\n- Built APIs."


def test_compose_cover_letter_preserves_trailing_newline_in_text_part() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Developer",
        company="Acme",
        tech_parts=[TextPartTech(text="Built APIs.", tech=Tech(name="Python"))],
        non_tech_parts=[
            TextPartNonTech(
                text="Intro with one extra line after this paragraph.\n",
                text_part_kind=TextPartKind.INTRO,
            )
        ],
    )

    assert (
        result == "Intro with one extra line after this paragraph.\n\n\n- Built APIs."
    )
