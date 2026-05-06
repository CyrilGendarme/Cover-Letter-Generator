from cover_letter_generator.models.text_parts import IntroOutroKind, IntroOutroTextPart, Tech, TextPartTech
from cover_letter_generator.services.cover_letter_service import CoverLetterService


def test_compose_cover_letter_orders_intro_body_outro() -> None:
    service = CoverLetterService()

    result = service.compose_cover_letter(
        job_title="Python Developer",
        company="Acme Corp",
        intro_parts=[
            IntroOutroTextPart(
                text="Applying for {job_title} at {company}.",
                intro_outro=IntroOutroKind.INTRO,
            )
        ],
        tech_parts=[
            TextPartTech(text="Built automation tools.", tech=Tech(name="Python")),
            TextPartTech(text="Improved delivery lead times.", tech=Tech(name="Docker")),
        ],
        outro_parts=[
            IntroOutroTextPart(
                text="Thank you for considering my application for {job_title} at {company_name}.",
                intro_outro=IntroOutroKind.OUTRO,
            )
        ],
    )

    assert result.startswith("Applying for Python Developer at Acme Corp.")
    assert "Built automation tools." in result
    assert "Improved delivery lead times." in result
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

    assert result == "Built APIs."
