"""Application entry point."""

from cover_letter_generator.app import CoverLetterApp


def main() -> None:
    app = CoverLetterApp()
    app.run()


if __name__ == "__main__":
    main()
