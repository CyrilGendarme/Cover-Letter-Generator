# Cover-Letter-Generator

Python desktop application scaffold with a GUI for generating cover letter drafts.

## Project Structure

```text
.
|-- cover_letter_generator/
|   |-- __init__.py
|   |-- app.py
|   |-- main.py
|   |-- gui/
|   |   |-- __init__.py
|   |   `-- main_window.py
|   |-- models/
|   |   |-- __init__.py
|   |   `-- text_parts.py
|   `-- services/
|       |-- __init__.py
|       |-- cover_letter_service.py
|       `-- json_data_store.py
|-- data/
|   |-- techs.json
|   `-- text_parts.json
|-- tests/
|   |-- test_cover_letter_service.py
|   |-- test_json_data_store.py
|   `-- test_text_parts.py
`-- pyproject.toml
```

## Quick Start

1. Create and activate a virtual environment.
2. Install the project in editable mode:

```bash
pip install -e .
```

3. Run the desktop app:

```bash
cover-letter-generator
```

Alternative run command:

```bash
python -m cover_letter_generator.main
```

## Run Tests

```bash
pip install -e .[dev]
pytest
```

## Notes

- GUI layer is in `cover_letter_generator/gui`.
- Business logic is in `cover_letter_generator/services`.
- `CoverLetterApp` in `cover_letter_generator/app.py` wires dependencies.
- The `Configuration` tab lets you load/add/modify/remove `Tech` and `TextPart` entities.
- Persistence is JSON-based in `data/techs.json` and `data/text_parts.json`.

## Generator Workflow (3 Screens)

1. Screen 1 - Job Description:
	- Paste a job description.
	- Click `Extract keywords` to prefill a checkable keyword list.
2. Screen 2 - Generation Setup:
	- Fill position name and company name.
	- Select language (`English` or `French`).
	- Review selected key techs.
3. Screen 3 - Output:
	- Generated text ready to copy/paste.
	- Export buttons for Word (`.docx`) and PDF (`.pdf`).