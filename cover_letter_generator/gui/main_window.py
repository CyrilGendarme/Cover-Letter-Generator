"""Main Tkinter window and widgets."""

import tkinter as tk
from tkinter import filedialog, ttk

from cover_letter_generator.models.text_parts import IntroOutroKind, IntroOutroTextPart, Tech, TextPart, TextPartTech
from cover_letter_generator.services.cover_letter_service import CoverLetterService
from cover_letter_generator.services.json_data_store import JsonDataStore


class MainWindow:
    """Builds and manages the main application window."""

    def __init__(self, service: CoverLetterService, data_store: JsonDataStore) -> None:
        self._service = service
        self._data_store = data_store
        self._root = tk.Tk()
        self._root.title("Cover Letter Generator")
        self._root.geometry("980x700")
        self._root.minsize(760, 560)

        self._position_name_var = tk.StringVar()
        self._position_company_var = tk.StringVar()
        self._status_var = tk.StringVar(value="Ready")

        self._tech_name_var = tk.StringVar()
        self._techs: list[Tech] = []

        self._text_parts: list[TextPart] = []
        self._text_part_association_var = tk.StringVar(value="none")
        self._text_part_enum_var = tk.StringVar(value=IntroOutroKind.BODY.value)
        self._text_part_tech_var = tk.StringVar(value="")
        self._selected_tech_part_vars: dict[int, tk.BooleanVar] = {}

        self._build_layout()
        self._load_configuration()

    def _build_layout(self) -> None:
        main = ttk.Frame(self._root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main, text="Cover Letter Generator", font=("Segoe UI", 20, "bold"))
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            main,
            text="Fill in the form and generate a first draft.",
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor=tk.W, pady=(0, 12))

        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)

        generator_tab = ttk.Frame(notebook, padding=8)
        configuration_tab = ttk.Frame(notebook, padding=8)

        notebook.add(generator_tab, text="Generator")
        notebook.add(configuration_tab, text="Configuration")

        self._build_generator_tab(generator_tab)
        self._build_configuration_tab(configuration_tab)

        status = ttk.Label(main, textvariable=self._status_var)
        status.pack(anchor=tk.W, pady=(8, 0))

    def _build_generator_tab(self, parent: ttk.Frame) -> None:
        screens = ttk.Notebook(parent)
        screens.pack(fill=tk.BOTH, expand=True)

        screen_1 = ttk.Frame(screens, padding=8)
        screen_2 = ttk.Frame(screens, padding=8)
        screen_3 = ttk.Frame(screens, padding=8)

        screens.add(screen_1, text="1) Job Description")
        screens.add(screen_2, text="2) Generation Setup")
        screens.add(screen_3, text="3) Output")

        self._build_screen_job_description(screen_1)
        self._build_screen_generation_setup(screen_2)
        self._build_screen_output(screen_3)

    def _build_screen_job_description(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        ttk.Label(parent, text="Paste job description").grid(row=0, column=0, sticky=tk.W)
        self._job_description = tk.Text(parent, height=12, wrap=tk.WORD)
        self._job_description.grid(row=1, column=0, sticky=tk.NSEW, pady=(4, 8))

        actions = ttk.Frame(parent)
        actions.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        ttk.Button(actions, text="Prepare matches", command=self._prepare_text_part_matches).pack(side=tk.LEFT)
        ttk.Button(actions, text="Clear", command=self._clear_job_description).pack(side=tk.LEFT, padx=(6, 0))

    def _build_screen_generation_setup(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

        self._add_labeled_entry(parent, "Job title", self._position_name_var, row=0)
        self._add_labeled_entry(parent, "Company name", self._position_company_var, row=1)

        ttk.Label(parent, text="TextPartTech items").grid(row=2, column=0, sticky=tk.NW, padx=(0, 8), pady=4)
        tech_parts_frame = ttk.LabelFrame(parent, text="Check the parts to include")
        tech_parts_frame.grid(row=2, column=1, sticky=tk.NSEW, pady=4)
        tech_parts_frame.columnconfigure(0, weight=1)
        tech_parts_frame.rowconfigure(0, weight=1)

        self._tech_parts_canvas = tk.Canvas(tech_parts_frame, borderwidth=0, highlightthickness=0)
        self._tech_parts_canvas.grid(row=0, column=0, sticky=tk.NSEW)

        tech_parts_scrollbar = ttk.Scrollbar(tech_parts_frame, orient=tk.VERTICAL, command=self._tech_parts_canvas.yview)
        tech_parts_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self._tech_parts_canvas.configure(yscrollcommand=tech_parts_scrollbar.set)

        self._tech_parts_check_frame = ttk.Frame(self._tech_parts_canvas)
        self._tech_parts_canvas_window = self._tech_parts_canvas.create_window((0, 0), window=self._tech_parts_check_frame, anchor="nw")
        self._tech_parts_check_frame.bind("<Configure>", self._on_tech_parts_frame_configure)
        self._tech_parts_canvas.bind("<Configure>", self._on_tech_parts_canvas_configure)

        actions = ttk.Frame(parent)
        actions.grid(row=3, column=1, sticky=tk.W, pady=(8, 0))
        ttk.Button(actions, text="Refresh matches", command=self._prepare_text_part_matches).pack(side=tk.LEFT)
        ttk.Button(actions, text="Generate text", command=self._on_generate).pack(side=tk.LEFT, padx=(6, 0))

    def _build_screen_output(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self._output = tk.Text(parent, wrap=tk.WORD)
        self._output.grid(row=0, column=0, sticky=tk.NSEW)

        actions = ttk.Frame(parent)
        actions.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        ttk.Button(actions, text="Copy", command=self._copy_output).pack(side=tk.LEFT)
        ttk.Button(actions, text="Export Word", command=self._export_word).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(actions, text="Export PDF", command=self._export_pdf).pack(side=tk.LEFT, padx=(6, 0))

    def _build_configuration_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)

        tech_frame = ttk.LabelFrame(parent, text="Tech Entities")
        tech_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))

        text_part_frame = ttk.LabelFrame(parent, text="TextPart Entities")
        text_part_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(6, 0))

        self._build_tech_editor(tech_frame)
        self._build_text_part_editor(text_part_frame)

    def _build_tech_editor(self, parent: ttk.LabelFrame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self._tech_list = tk.Listbox(parent, exportselection=False)
        self._tech_list.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, padx=8, pady=(8, 4))
        self._tech_list.bind("<<ListboxSelect>>", self._on_tech_selected)

        ttk.Label(parent, text="Name").grid(row=1, column=0, sticky=tk.W, padx=8)
        ttk.Entry(parent, textvariable=self._tech_name_var).grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=8)

        ttk.Label(parent, text="Associated text parts (one per line)").grid(row=3, column=0, sticky=tk.W, padx=8, pady=(8, 0))
        self._tech_text_parts = tk.Text(parent, height=8, wrap=tk.WORD)
        self._tech_text_parts.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=8, pady=(2, 8))

        buttons = ttk.Frame(parent)
        buttons.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=8, pady=(0, 8))
        ttk.Button(buttons, text="Load", command=self._load_configuration).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Add / Modify", command=self._on_upsert_tech).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(buttons, text="Remove", command=self._on_remove_tech).pack(side=tk.LEFT, padx=(6, 0))

    def _build_text_part_editor(self, parent: ttk.LabelFrame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self._text_part_list = tk.Listbox(parent, exportselection=False)
        self._text_part_list.grid(row=0, column=0, sticky=tk.NSEW, padx=8, pady=(8, 4))
        self._text_part_list.bind("<<ListboxSelect>>", self._on_text_part_selected)

        ttk.Label(parent, text="Text").grid(row=1, column=0, sticky=tk.W, padx=8)
        self._text_part_text = tk.Text(parent, height=12, wrap=tk.WORD)
        self._text_part_text.grid(row=2, column=0, sticky=tk.EW, padx=8, pady=(2, 8))

        ttk.Label(parent, text="Association type").grid(row=3, column=0, sticky=tk.W, padx=8)
        association_frame = ttk.Frame(parent)
        association_frame.grid(row=4, column=0, sticky=tk.W, padx=8, pady=(2, 6))
        ttk.Radiobutton(
            association_frame,
            text="None",
            value="none",
            variable=self._text_part_association_var,
            command=self._toggle_text_part_association_inputs,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            association_frame,
            text="Tech",
            value="tech",
            variable=self._text_part_association_var,
            command=self._toggle_text_part_association_inputs,
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Radiobutton(
            association_frame,
            text="Enum",
            value="enum",
            variable=self._text_part_association_var,
            command=self._toggle_text_part_association_inputs,
        ).pack(side=tk.LEFT, padx=(8, 0))

        enum_row = ttk.Frame(parent)
        enum_row.grid(row=5, column=0, sticky=tk.W, padx=8, pady=(0, 4))
        ttk.Label(enum_row, text="Enum value").pack(side=tk.LEFT)
        self._text_part_enum_combo = ttk.Combobox(
            enum_row,
            state="readonly",
            values=[item.value for item in IntroOutroKind],
            textvariable=self._text_part_enum_var,
            width=12,
        )
        self._text_part_enum_combo.pack(side=tk.LEFT, padx=(8, 0))

        tech_row = ttk.Frame(parent)
        tech_row.grid(row=6, column=0, sticky=tk.W, padx=8, pady=(0, 8))
        ttk.Label(tech_row, text="Tech key").pack(side=tk.LEFT)
        self._text_part_tech_combo = ttk.Combobox(
            tech_row,
            state="readonly",
            textvariable=self._text_part_tech_var,
            width=20,
        )
        self._text_part_tech_combo.pack(side=tk.LEFT, padx=(8, 0))

        buttons = ttk.Frame(parent)
        buttons.grid(row=7, column=0, sticky=tk.W, padx=8, pady=(0, 8))
        ttk.Button(buttons, text="Load", command=self._load_configuration).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Add / Modify", command=self._on_upsert_text_part).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(buttons, text="Remove", command=self._on_remove_text_part).pack(side=tk.LEFT, padx=(6, 0))
        self._toggle_text_part_association_inputs()

    def _load_configuration(self) -> None:
        self._techs = self._data_store.load_techs()
        self._text_parts = self._data_store.load_text_parts()
        self._refresh_tech_list()
        self._refresh_text_part_list()
        self._refresh_text_part_tech_keys()
        self._refresh_text_part_tech_candidates()
        self._status_var.set("Configuration loaded from JSON files")

    def _refresh_text_part_tech_keys(self) -> None:
        tech_names = [tech.name for tech in self._techs if tech.name.strip()]
        self._text_part_tech_combo["values"] = tech_names
        if tech_names and self._text_part_tech_var.get() not in tech_names:
            self._text_part_tech_var.set(tech_names[0])
        if not tech_names:
            self._text_part_tech_var.set("")

    def _refresh_text_part_tech_candidates(self) -> None:
        tech_parts = self._get_text_part_tech_items()
        current_states = {
            index: variable.get() for index, variable in self._selected_tech_part_vars.items()
        }
        self._selected_tech_part_vars = {
            index: tk.BooleanVar(value=current_states.get(index, False)) for index, _part in tech_parts
        }
        self._render_text_part_tech_checkboxes(tech_parts)

    def _refresh_tech_list(self) -> None:
        self._tech_list.delete(0, tk.END)
        for tech in self._techs:
            self._tech_list.insert(tk.END, f"{tech.name} ({len(tech.text_parts)} text parts)")

    def _refresh_text_part_list(self) -> None:
        self._text_part_list.delete(0, tk.END)
        for part in self._text_parts:
            preview = part.text.replace("\n", " ").strip()
            if len(preview) > 70:
                preview = f"{preview[:67]}..."
            label = self._format_text_part_association(part)
            self._text_part_list.insert(tk.END, f"[{label}] {preview or '<empty>'}")

    def _get_text_part_tech_items(self) -> list[tuple[int, TextPartTech]]:
        items: list[tuple[int, TextPartTech]] = []
        for index, part in enumerate(self._text_parts):
            if isinstance(part, TextPartTech):
                items.append((index, part))
        return items

    def _get_intro_parts(self) -> list[IntroOutroTextPart]:
        return [
            part for part in self._text_parts
            if isinstance(part, IntroOutroTextPart) and part.intro_outro == IntroOutroKind.INTRO
        ]

    def _get_outro_parts(self) -> list[IntroOutroTextPart]:
        return [
            part for part in self._text_parts
            if isinstance(part, IntroOutroTextPart) and part.intro_outro == IntroOutroKind.OUTRO
        ]

    def _render_text_part_tech_checkboxes(self, tech_parts: list[tuple[int, TextPartTech]]) -> None:
        for child in self._tech_parts_check_frame.winfo_children():
            child.destroy()

        if not tech_parts:
            ttk.Label(
                self._tech_parts_check_frame,
                text="No TextPartTech items configured yet.",
            ).pack(anchor=tk.W, padx=6, pady=6)
            return

        for index, part in tech_parts:
            label = f"{part.tech.name}: {self._truncate_text(part.text)}"
            ttk.Checkbutton(
                self._tech_parts_check_frame,
                text=label,
                variable=self._selected_tech_part_vars[index],
            ).pack(anchor=tk.W, padx=6, pady=2)

    def _truncate_text(self, text: str, limit: int = 80) -> str:
        cleaned = text.replace("\n", " ").strip()
        if len(cleaned) <= limit:
            return cleaned
        return f"{cleaned[: limit - 3]}..."

    def _format_text_part_association(self, part: TextPart) -> str:
        if isinstance(part, TextPartTech):
            return f"tech:{part.tech.name}"
        if isinstance(part, IntroOutroTextPart):
            return f"enum:{part.intro_outro.value}"
        return "none"

    def _on_tech_selected(self, _event: tk.Event) -> None:
        index = self._get_selected_index(self._tech_list)
        if index is None:
            return
        selected = self._techs[index]
        self._tech_name_var.set(selected.name)
        self._tech_text_parts.delete("1.0", tk.END)
        self._tech_text_parts.insert("1.0", "\n".join(selected.text_parts))

    def _on_text_part_selected(self, _event: tk.Event) -> None:
        index = self._get_selected_index(self._text_part_list)
        if index is None:
            return
        selected = self._text_parts[index]
        self._text_part_text.delete("1.0", tk.END)
        self._text_part_text.insert("1.0", selected.text)

        if isinstance(selected, TextPartTech):
            self._text_part_association_var.set("tech")
            self._text_part_tech_var.set(selected.tech.name)
        elif isinstance(selected, IntroOutroTextPart):
            self._text_part_association_var.set("enum")
            self._text_part_enum_var.set(selected.intro_outro.value)
        else:
            self._text_part_association_var.set("none")
        self._toggle_text_part_association_inputs()

    def _on_upsert_tech(self) -> None:
        name = self._tech_name_var.get().strip()
        if not name:
            self._status_var.set("Tech name is required")
            return
        text_parts = self._read_non_empty_lines(self._tech_text_parts)
        result = self._data_store.upsert_tech_by_name(Tech(name=name, text_parts=text_parts))
        self._load_configuration()
        self._status_var.set(f"{result.capitalize()} tech by key '{name}'")

    def _on_remove_tech(self) -> None:
        index = self._get_selected_index(self._tech_list)
        if index is None:
            self._status_var.set("Select a tech entity to remove")
            return
        success = self._data_store.remove_tech(index)
        if success:
            self._load_configuration()
            self._tech_name_var.set("")
            self._tech_text_parts.delete("1.0", tk.END)
            self._status_var.set("Removed tech entity")
        else:
            self._status_var.set("Could not remove selected tech")

    def _on_upsert_text_part(self) -> None:
        text = self._text_part_text.get("1.0", tk.END).strip()
        if not text:
            self._status_var.set("TextPart text is required")
            return

        association = self._text_part_association_var.get()
        if association == "tech":
            tech_key = self._text_part_tech_var.get().strip()
            if not tech_key:
                self._status_var.set("Select a tech key for TextPartTech association")
                return
            text_part: TextPart = TextPartTech(text=text, tech=Tech(name=tech_key))
        elif association == "enum":
            enum_value = self._text_part_enum_var.get().strip().lower()
            if enum_value not in {item.value for item in IntroOutroKind}:
                self._status_var.set("Select a valid enum value")
                return
            text_part = IntroOutroTextPart(text=text, intro_outro=IntroOutroKind(enum_value))
        else:
            text_part = TextPart(text=text)

        result = self._data_store.upsert_text_part_by_text(text_part)
        self._load_configuration()
        self._status_var.set(f"{result.capitalize()} text part by key")

    def _toggle_text_part_association_inputs(self) -> None:
        association = self._text_part_association_var.get()
        if association == "enum":
            self._text_part_enum_combo.configure(state="readonly")
            self._text_part_tech_combo.configure(state="disabled")
        elif association == "tech":
            self._text_part_enum_combo.configure(state="disabled")
            self._text_part_tech_combo.configure(state="readonly")
        else:
            self._text_part_enum_combo.configure(state="disabled")
            self._text_part_tech_combo.configure(state="disabled")

    def _on_remove_text_part(self) -> None:
        index = self._get_selected_index(self._text_part_list)
        if index is None:
            self._status_var.set("Select a text part entity to remove")
            return
        success = self._data_store.remove_text_part(index)
        if success:
            self._load_configuration()
            self._text_part_text.delete("1.0", tk.END)
            self._status_var.set("Removed text part")
        else:
            self._status_var.set("Could not remove selected text part")

    def _read_non_empty_lines(self, widget: tk.Text) -> list[str]:
        return [line.strip() for line in widget.get("1.0", tk.END).splitlines() if line.strip()]

    def _prepare_text_part_matches(self) -> None:
        job_description = self._job_description.get("1.0", tk.END).strip().lower()
        tech_parts = self._get_text_part_tech_items()
        match_count = 0
        for index, part in tech_parts:
            should_check = self._matches_job_description(job_description, part)
            self._selected_tech_part_vars[index].set(should_check)
            if should_check:
                match_count += 1
        self._status_var.set(f"Prepared {match_count} matching TextPartTech items")

    def _matches_job_description(self, job_description: str, part: TextPartTech) -> bool:
        if not job_description:
            return False

        tech_name = part.tech.name.strip().lower()
        if tech_name and tech_name in job_description:
            return True

        for tech in self._techs:
            if tech.name.strip().lower() != tech_name:
                continue
            for alias in tech.text_parts:
                if alias.strip().lower() in job_description:
                    return True
        return False

    def _on_tech_parts_frame_configure(self, _event: tk.Event) -> None:
        self._tech_parts_canvas.configure(scrollregion=self._tech_parts_canvas.bbox("all"))

    def _on_tech_parts_canvas_configure(self, event: tk.Event) -> None:
        self._tech_parts_canvas.itemconfigure(self._tech_parts_canvas_window, width=event.width)

    def _clear_job_description(self) -> None:
        self._job_description.delete("1.0", tk.END)
        for variable in self._selected_tech_part_vars.values():
            variable.set(False)
        self._status_var.set("Job description cleared")

    def _get_selected_index(self, listbox: tk.Listbox) -> int | None:
        selected = listbox.curselection()
        if not selected:
            return None
        return int(selected[0])

    def _add_labeled_entry(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        row: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky=tk.EW, pady=4)

    def _on_generate(self) -> None:
        selected_tech_parts = [
            self._text_parts[index]
            for index, variable in self._selected_tech_part_vars.items()
            if variable.get() and isinstance(self._text_parts[index], TextPartTech)
        ]
        text = self._service.compose_cover_letter(
            job_title=self._position_name_var.get().strip(),
            company=self._position_company_var.get().strip(),
            intro_parts=self._get_intro_parts(),
            tech_parts=selected_tech_parts,
            outro_parts=self._get_outro_parts(),
        )
        self._output.delete("1.0", tk.END)
        self._output.insert("1.0", text)
        self._status_var.set("Cover letter generated")

    def _on_clear(self) -> None:
        self._position_name_var.set("")
        self._position_company_var.set("")
        self._job_description.delete("1.0", tk.END)
        for variable in self._selected_tech_part_vars.values():
            variable.set(False)
        self._output.delete("1.0", tk.END)
        self._status_var.set("Generator form cleared")

    def _copy_output(self) -> None:
        text = self._output.get("1.0", tk.END).strip()
        if not text:
            self._status_var.set("No generated text to copy")
            return
        self._root.clipboard_clear()
        self._root.clipboard_append(text)
        self._status_var.set("Generated text copied to clipboard")

    def _export_word(self) -> None:
        text = self._output.get("1.0", tk.END).strip()
        if not text:
            self._status_var.set("No generated text to export")
            return

        path = filedialog.asksaveasfilename(
            title="Export Word",
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
        )
        if not path:
            return

        try:
            from docx import Document
        except ImportError:
            self._status_var.set("python-docx is not installed. Install dependencies first.")
            return

        document = Document()
        for paragraph in text.split("\n\n"):
            document.add_paragraph(paragraph)
        document.save(path)
        self._status_var.set(f"Word export complete: {path}")

    def _export_pdf(self) -> None:
        text = self._output.get("1.0", tk.END).strip()
        if not text:
            self._status_var.set("No generated text to export")
            return

        path = filedialog.asksaveasfilename(
            title="Export PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not path:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            self._status_var.set("reportlab is not installed. Install dependencies first.")
            return

        pdf = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        margin = 40
        y = height - margin
        for line in text.splitlines():
            if y <= margin:
                pdf.showPage()
                y = height - margin
            pdf.drawString(margin, y, line[:120])
            y -= 14
        pdf.save()
        self._status_var.set(f"PDF export complete: {path}")

    def start(self) -> None:
        self._root.mainloop()
