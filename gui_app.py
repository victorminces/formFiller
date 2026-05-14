import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from fill_forms import fill_demographic, fill_oar_flattened


APP_DIR = Path(__file__).resolve().parent


def load_example():
    return json.loads((APP_DIR / "patient_input.example.json").read_text(encoding="utf-8"))


def set_nested(data, dotted_key, value):
    current = data
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def get_nested(data, dotted_key, default=""):
    current = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return "" if current is None else str(current)


FIELDS = [
    ("Paths", [
        ("paths.demographic_template", "Demographic template PDF", "file"),
        ("paths.oar_template", "OAR template PDF", "file"),
        ("paths.output_dir", "Output folder", "folder"),
    ]),
    ("Client", [
        ("client.full_name", "Full legal name", "text"),
        ("client.first_name", "First name", "text"),
        ("client.last_name", "Last name", "text"),
        ("client.name_at_birth_first", "First name at birth", "text"),
        ("client.name_at_birth_last", "Last name at birth", "text"),
        ("client.dob", "DOB", "text"),
        ("client.age", "Age", "text"),
        ("client.sex", "Sex", "text"),
        ("client.gender_identity", "Gender identity", "text"),
        ("client.sexual_orientation", "Sexual orientation", "text"),
        ("client.ethnicity", "Ethnicity", "text"),
        ("client.primary_language", "Primary language", "text"),
        ("client.preferred_language", "Preferred language", "text"),
        ("client.place_of_birth_country", "Birth country", "text"),
        ("client.place_of_birth_state", "Birth state", "text"),
        ("client.place_of_birth_county", "Birth county/city", "text"),
        ("client.mothers_first_name", "Mother's first name", "text"),
        ("client.address", "Address", "text"),
        ("client.phone", "Client phone", "text"),
        ("client.phone_type", "Phone type", "text"),
        ("client.living_situation", "Living situation", "text"),
        ("client.living_with", "Lives with", "text"),
        ("client.education", "Education", "text"),
        ("client.marital_status", "Marital status", "text"),
        ("client.military_status", "Military status", "text"),
        ("client.veteran_status", "Veteran status", "text"),
    ]),
    ("Insurance", [
        ("insurance.medi_cal_cin", "Medi-Cal CIN", "text"),
        ("insurance.benefits_id", "Benefits ID", "text"),
        ("insurance.member_number", "Member number", "text"),
        ("insurance.plan_name", "Plan name", "text"),
        ("insurance.effective_date", "Effective date", "text"),
        ("insurance.pcp_name", "PCP name", "text"),
        ("insurance.pcp_address", "PCP address", "text"),
        ("insurance.pcp_phone", "PCP phone", "text"),
    ]),
    ("Clinical", [
        ("clinical.primary_diagnosis", "Primary diagnosis", "text"),
        ("clinical.icd_code", "ICD code", "text"),
        ("clinical.other_diagnoses", "Other diagnoses", "text"),
        ("clinical.current_symptoms", "Current symptoms", "wide"),
        ("clinical.problem_list_date", "Problem list date", "text"),
        ("clinical.significant_impairment", "Significant impairment", "wide"),
        ("clinical.trauma_history", "Trauma history", "wide"),
        ("clinical.substance_use", "Substance use", "text"),
        ("clinical.substance_use_impact", "Substance use impact", "text"),
        ("clinical.interventions", "Interventions", "wide"),
        ("clinical.interpreter_needed", "Interpreter needed", "text"),
        ("clinical.sessions_begin_date", "Sessions begin date", "text"),
        ("clinical.sessions_count", "Number of sessions", "text"),
        ("clinical.sessions_frequency", "Frequency", "text"),
    ]),
    ("Risk", [
        ("clinical.suicidal.no", "Suicidal: no", "bool"),
        ("clinical.suicidal.ideation", "Suicidal: ideation", "bool"),
        ("clinical.suicidal.plan", "Suicidal: plan", "bool"),
        ("clinical.suicidal.intent", "Suicidal: intent", "bool"),
        ("clinical.suicidal.history_of_harm", "Suicidal: history of harm", "bool"),
        ("clinical.homicidal.no", "Homicidal: no", "bool"),
        ("clinical.homicidal.ideation", "Homicidal: ideation", "bool"),
        ("clinical.homicidal.plan", "Homicidal: plan", "bool"),
        ("clinical.homicidal.intent", "Homicidal: intent", "bool"),
        ("clinical.homicidal.history_of_harm", "Homicidal: history of harm", "bool"),
    ]),
    ("Provider", [
        ("provider.name_license", "Provider name/license", "text"),
        ("provider.phone", "Provider phone", "text"),
        ("provider.date", "Provider date", "text"),
    ]),
]


class ScrollFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OAR + Demographic Form Filler")
        self.geometry("980x760")
        self.data = load_example()
        self.vars = {}
        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Load JSON", command=self.load_json).pack(side="left", padx=4)
        ttk.Button(top, text="Save JSON", command=self.save_json).pack(side="left", padx=4)
        ttk.Button(top, text="Generate PDFs", command=self.generate).pack(side="left", padx=4)
        ttk.Button(top, text="Quit", command=self.destroy).pack(side="right", padx=4)

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True, padx=8, pady=8)
        row = 0
        for section, fields in FIELDS:
            label = ttk.Label(sf.inner, text=section, font=("Segoe UI", 12, "bold"))
            label.grid(row=row, column=0, columnspan=4, sticky="w", pady=(12, 4))
            row += 1
            for key, label_text, kind in fields:
                ttk.Label(sf.inner, text=label_text).grid(row=row, column=0, sticky="w", padx=4, pady=3)
                if kind == "bool":
                    var = tk.BooleanVar(value=bool(get_nested(self.data, key, False)))
                    widget = ttk.Checkbutton(sf.inner, variable=var)
                    widget.grid(row=row, column=1, sticky="w", padx=4, pady=3)
                else:
                    var = tk.StringVar(value=get_nested(self.data, key))
                    width = 82 if kind == "wide" else 48
                    widget = ttk.Entry(sf.inner, textvariable=var, width=width)
                    widget.grid(row=row, column=1, sticky="we", padx=4, pady=3)
                    if kind == "file":
                        ttk.Button(sf.inner, text="Browse", command=lambda v=var: self.pick_file(v)).grid(row=row, column=2, padx=4)
                    elif kind == "folder":
                        ttk.Button(sf.inner, text="Browse", command=lambda v=var: self.pick_folder(v)).grid(row=row, column=2, padx=4)
                self.vars[key] = var
                row += 1

        sf.inner.columnconfigure(1, weight=1)

    def collect_data(self):
        data = load_example()
        for key, var in self.vars.items():
            set_nested(data, key, var.get())
        return data

    def pick_file(self, var):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if path:
            var.set(path)

    def pick_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        self.data = json.loads(Path(path).read_text(encoding="utf-8"))
        for key, var in self.vars.items():
            var.set(get_nested(self.data, key, False if isinstance(var, tk.BooleanVar) else ""))

    def save_json(self):
        data = self.collect_data()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def generate(self):
        try:
            data = self.collect_data()
            output_dir = Path(data["paths"]["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)
            outputs = [fill_demographic(data, output_dir), fill_oar_flattened(data, output_dir)]
            messagebox.showinfo("PDFs generated", "\n".join(str(p) for p in outputs))
        except Exception as exc:
            messagebox.showerror("Generation failed", str(exc))


if __name__ == "__main__":
    App().mainloop()
