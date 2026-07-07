import argparse
import json
import sys
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, TextStringObject
from reportlab.pdfgen import canvas


BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DEMOGRAPHIC_MAP = BASE_DIR / "field_maps" / "demographic_2024.json"
OAR_MAP = BASE_DIR / "field_maps" / "oar_psychotherapy_2025.json"
FIELD_LIMITS = BASE_DIR / "field_maps" / "field_limits.json"
BUNDLED_DEMOGRAPHIC_TEMPLATE = BASE_DIR / "templates" / "demographic_template.pdf"
BUNDLED_OAR_TEMPLATE = BASE_DIR / "templates" / "oar_template.pdf"
BUNDLED_TIMELINESS_TEMPLATE = BASE_DIR / "templates" / "timeliness_template.pdf"
BUNDLED_SIGNATURE = BASE_DIR / "assets" / "provider_signature.png"
FORM_FONT_SIZE = 8


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_nested(data, dotted_key, default=""):
    current = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return "" if current is None else str(current)


def fit_text(value, max_chars=None):
    value = " ".join(str(value or "").split())
    # Field-ready text should already be shortened against measured rendered
    # width. Do not silently hard-truncate here; that hides clinical meaning.
    return value


def load_field_limits():
    if FIELD_LIMITS.exists():
        return load_json(FIELD_LIMITS)
    return {}


def limit_chars(field_limits, form_name, key, fallback=None):
    limit = field_limits.get(form_name, {}).get(key, {})
    return limit.get("max_chars", fallback)


def diagnosis_code_from_text(value):
    import re

    match = re.search(r"\bF\d{2}(?:\.\d{1,2}|[A-Z])?\b", str(value or ""), re.I)
    return match.group(0).upper() if match else ""


def diagnosis_label_without_code(value):
    import re

    return re.sub(r"^\s*F\d{2}(?:\.\d{1,2}|[A-Z])?\s*[-:]\s*", "", str(value or "")).strip()


def safe_name(name):
    return "".join(ch for ch in name if ch.isalnum() or ch in (" ", "-", "_")).strip() or "client"


def client_full_name(data):
    client = data.get("client", {})
    first = str(client.get("first_name", "")).strip()
    last = str(client.get("last_name", "")).strip()
    derived = " ".join(part for part in (first, last) if part).strip()
    return derived or str(client.get("full_name", "")).strip()


def resolve_output_dir(data):
    configured = str(data.get("paths", {}).get("output_dir", "")).strip()
    if not configured or "C:\\path\\to" in configured:
        return Path.home() / "Documents" / "FormFillerOutputs"
    return Path(configured)


def fill_demographic(data, output_dir):
    form_map = load_json(DEMOGRAPHIC_MAP)
    field_limits = load_field_limits()
    configured_template = str(data.get("paths", {}).get("demographic_template", "")).strip()
    template = Path(configured_template) if configured_template and "C:\\path\\to" not in configured_template else BUNDLED_DEMOGRAPHIC_TEMPLATE
    output = output_dir / f"Demographic Form - {safe_name(client_full_name(data))} filled.pdf"

    reader = PdfReader(str(template))
    writer = PdfWriter()
    writer.append(reader)

    client = data["client"]
    values = {}
    for data_key, field_name in form_map["text_fields"].items():
        if data_key == "date_of_completion":
            value = data.get("provider", {}).get("date", "")
        elif data_key == "full_name":
            value = client_full_name(data)
        elif data_key == "current_first_name":
            value = "" if client.get("same_first_name") else client.get("first_name", "")
        elif data_key == "current_last_name":
            value = "" if client.get("same_last_name") else client.get("last_name", "")
        elif data_key == "current_middle_name":
            value = "" if client.get("same_middle_name") else client.get("middle_name", "")
        else:
            value = client.get(data_key, "")
        if value:
            values[field_name] = fit_text(value, limit_chars(field_limits, "demographic", data_key))

    phone = client.get("phone", "")
    phone_type = client.get("phone_type", "").lower()
    if phone:
        if phone_type == "business":
            values["Text1a"] = fit_text(phone, limit_chars(field_limits, "demographic", "phone"))
        elif phone_type == "home":
            values["Text1b"] = fit_text(phone, limit_chars(field_limits, "demographic", "phone"))
        else:
            values["Text1"] = fit_text(phone, limit_chars(field_limits, "demographic", "phone"))

    client = data["client"]
    suffixes = set(client.get("suffix_at_birth", []) or [])
    ethnicity_options = set(client.get("ethnicity_options", []) or [])
    use_ethnicity_options = bool(ethnicity_options)
    race_options = set(client.get("race_options", []) or [])
    special_population = set(client.get("special_population_services", []) or [])
    court_status = set(client.get("court_status", []) or [])
    hispanic_status = client.get("hispanic_latino_status", "")
    gender_identity = client.get("gender_identity", "").lower()
    sexual_orientation = client.get("sexual_orientation", "").lower()
    checkbox_rules = {
        "suffix_jr": "JR" in suffixes,
        "suffix_sr": "SR" in suffixes,
        "suffix_ii": "II" in suffixes,
        "suffix_iii": "III" in suffixes,
        "suffix_iv": "IV" in suffixes,
        "suffix_v": "V" in suffixes,
        "suffix_vi": "VI" in suffixes,
        "ethnicity_amerasian": "Amerasian" in ethnicity_options,
        "ethnicity_american_native": "American Native" in ethnicity_options,
        "ethnicity_asian_indian": "Asian Indian" in ethnicity_options,
        "ethnicity_black": "Black" in ethnicity_options,
        "ethnicity_cambodian": "Cambodian" in ethnicity_options,
        "ethnicity_chinese": "Chinese" in ethnicity_options,
        "ethnicity_dominican": "Dominican" in ethnicity_options,
        "ethnicity_filipino": "Filipino" in ethnicity_options,
        "ethnicity_guamanian": "Guamanian" in ethnicity_options,
        "ethnicity_hawaiian_native": "Hawaiian Native" in ethnicity_options,
        "ethnicity_hispanic_or_latino": "Hispanic or Latino" in ethnicity_options or (not use_ethnicity_options and "Hispanic" in client.get("ethnicity", "")),
        "ethnicity_japanese": "Japanese" in ethnicity_options,
        "ethnicity_korean": "Korean" in ethnicity_options,
        "ethnicity_laotian": "Laotian" in ethnicity_options,
        "ethnicity_mexican": "Mexican/Mexican American" in ethnicity_options or (not use_ethnicity_options and "Mexican" in client.get("ethnicity", "")),
        "ethnicity_middle_eastern_north_african": "Middle Eastern or North African" in ethnicity_options,
        "ethnicity_multiple": "Multiple" in ethnicity_options,
        "ethnicity_not_hispanic_or_latino": "Not Hispanic or Latino" in ethnicity_options,
        "ethnicity_other": "Other" in ethnicity_options,
        "ethnicity_other_asian": "Other Asian" in ethnicity_options,
        "ethnicity_other_pacific_islander": "Other Pacific Islander" in ethnicity_options,
        "ethnicity_samoan": "Samoan" in ethnicity_options,
        "ethnicity_unknown_not_reported": "Unknown/Not Reported" in ethnicity_options,
        "ethnicity_vietnamese": "Vietnamese" in ethnicity_options,
        "ethnicity_white_caucasian": "White/Caucasian" in ethnicity_options,
        "hispanic_yes": hispanic_status.lower() == "yes",
        "hispanic_no": hispanic_status.lower() == "no",
        "hispanic_unknown_not_reported": "unknown" in hispanic_status.lower(),
        "same_first_name": bool(client.get("same_first_name")),
        "same_last_name": bool(client.get("same_last_name")),
        "same_middle_name": bool(client.get("same_middle_name")),
        "no_special_population_services": "No" in special_population or not special_population,
        "special_population_aot": "Assisted Outpatient Treatment" in special_population,
        "special_population_iep": "IEP required services" in special_population,
        "special_population_governors_homeless": "Governor's Homeless Initiative" in special_population,
        "special_population_welfare_to_work": "Welfare-to-Work" in special_population,
        "discharge_acute": bool(client.get("discharge_acute")),
        "discharge_home": client.get("patient_status", "").lower() == "discharged home",
        "discharge_unknown_not_reported": bool(client.get("discharge_unknown_not_reported")) or "unknown" in client.get("patient_status", "").lower(),
        "discharge_facility": client.get("patient_status", "").lower() == "discharged to a facility" or bool(client.get("discharge_facility")),
        "not_currently_enrolled": bool(client.get("not_currently_enrolled")),
        "court_temporary_conservatorship": "Temporary Conservatorship" in court_status,
        "court_lanterman_petris_short": "Lanterman-Petris-Short" in court_status,
        "court_murphy": "Murphy" in court_status,
        "court_probate": "Probate" in court_status,
        "court_pc_2974": "PC 2974" in court_status,
        "court_representative_payee": "Representative Payee Without Conservatorship" in court_status,
        "court_juvenile_dependent": "Juvenile Court Dependent" in court_status,
        "court_juvenile_status_offender": "Juvenile Ward Status Offender" in court_status,
        "court_juvenile_offender": "Juvenile Ward Juvenile Offender" in court_status,
        "court_status_not_applicable": "Not Applicable" in court_status,
        "court_status_unknown_not_reported": "Unknown/Not Reported" in court_status or not court_status,
        "phone_mobile": client.get("phone_type", "").lower() == "mobile",
        "phone_business": client.get("phone_type", "").lower() == "business",
        "phone_home": client.get("phone_type", "").lower() == "home",
        "do_not_call": bool(client.get("do_not_call")),
        "do_not_leave_message": bool(client.get("do_not_leave_message")),
        "address_physical": True,
        "address_mailing": True,
        "race_alaskan_native": "Alaskan Native" in race_options,
        "race_american_indian": "American Indian" in race_options,
        "race_asian_indian": "Asian Indian" in race_options,
        "race_black_african_american": "Black/African American" in race_options,
        "race_cambodian": "Cambodian" in race_options,
        "race_chinese": "Chinese" in race_options,
        "race_filipino": "Filipino" in race_options,
        "race_guamanian": "Guamanian" in race_options,
        "race_hawaiian": "Hawaiian" in race_options,
        "race_hmong": "Hmong" in race_options,
        "race_japanese": "Japanese" in race_options,
        "race_korean": "Korean" in race_options,
        "race_laotian": "Laotian" in race_options,
        "race_mien": "Mien" in race_options,
        "race_middle_eastern_north_african": "Middle Eastern or North African" in race_options,
        "race_multiracial": "Multiracial" in race_options,
        "race_native_hawaiian": "Native Hawaiian" in race_options,
        "race_not_asked": "Not Asked" in race_options,
        "race_other": "Other" in race_options,
        "race_other_asian": "Other Asian" in race_options,
        "race_other_pacific_islander": "Other Pacific Islander" in race_options,
        "race_prefer_not_to_answer": "Prefer not to answer" in race_options,
        "race_samoan": "Samoan" in race_options,
        "race_unknown": "Unknown" in race_options,
        "race_vietnamese": "Vietnamese" in race_options,
        "race_white_caucasian": "White/Caucasian" in race_options,
        "marital_divorced": client.get("marital_status", "").lower() == "divorced",
        "marital_domestic_partnership": client.get("marital_status", "").lower() == "domestic partnership",
        "marital_married": client.get("marital_status", "").lower() == "married",
        "marital_never_married": client.get("marital_status", "").lower() in {"never married", "single"},
        "marital_separated": client.get("marital_status", "").lower() == "separated",
        "marital_unknown": client.get("marital_status", "").lower() == "unknown",
        "marital_widowed": client.get("marital_status", "").lower() == "widowed",
        "sex_male": client.get("sex", "").lower() == "male",
        "sex_female": client.get("sex", "").lower() == "female",
        "sex_not_listed": client.get("sex", "").lower() in {"intersex", "unknown", "prefer not to answer", "not listed"},
        "gender_identity_nonbinary": "non-binary" in gender_identity or "nonbinary" in gender_identity,
        "gender_identity_male": gender_identity == "male",
        "gender_identity_female": gender_identity == "female",
        "gender_identity_transgender": gender_identity == "transgender",
        "gender_identity_transgender_male": "transgender male" in gender_identity,
        "gender_identity_transgender_female": "transgender female" in gender_identity,
        "gender_identity_genderqueer": "genderqueer" in gender_identity,
        "gender_identity_questioning": "questioning" in gender_identity,
        "gender_identity_prefer_not_to_answer": "prefer not" in gender_identity,
        "gender_identity_other": gender_identity == "other",
        "gender_identity_unknown": "unknown" in gender_identity,
        "sexual_orientation_heterosexual": "heterosexual" in sexual_orientation or "straight" in sexual_orientation,
        "sexual_orientation_gay": sexual_orientation == "gay",
        "sexual_orientation_prefer_not_to_answer": "prefer not" in sexual_orientation,
        "sexual_orientation_lesbian": "lesbian" in sexual_orientation,
        "sexual_orientation_questioning": "questioning" in sexual_orientation,
        "sexual_orientation_transgender": "transgender" in sexual_orientation,
        "sexual_orientation_bisexual": "bisexual" in sexual_orientation,
        "sexual_orientation_declined": "declined" in sexual_orientation,
        "sexual_orientation_unknown": "unknown" in sexual_orientation,
        "military_no": client.get("military_status", "").lower() == "no",
        "veteran_no": client.get("veteran_status", "").lower() == "no",
    }

    for data_key, field_name in form_map["checkbox_fields"].items():
        if checkbox_rules.get(data_key, False):
            if data_key in {"military_no", "veteran_no"}:
                values[field_name] = "/No"
            else:
                values[field_name] = "/Yes"

    for page in writer.pages:
        for annot_ref in page.get("/Annots") or []:
            annot = annot_ref.get_object()
            if annot.get("/FT") == "/Tx":
                field_name = str(annot.get("/T", ""))
                annot[NameObject("/DA")] = TextStringObject(f"/Helv {FORM_FONT_SIZE} Tf 0 g")
        writer.update_page_form_field_values(page, values, auto_regenerate=True)
        set_individual_button_appearances(page, values)

    acroform = writer._root_object.get("/AcroForm")
    if acroform:
        acroform.update({
            NameObject("/DA"): TextStringObject(f"/Helv {FORM_FONT_SIZE} Tf 0 g"),
            NameObject("/NeedAppearances"): BooleanObject(True),
        })
        if client.get("military_status", "").lower() == "no":
            set_button_group_state(acroform, "Military Status", "No")
        if client.get("veteran_status", "").lower() == "no":
            set_button_group_state(acroform, "Veteran Status", "No")

    with output.open("wb") as f:
        writer.write(f)
    return output


def set_individual_button_appearances(page, values):
    for annot_ref in page.get("/Annots") or []:
        annot = annot_ref.get_object()
        if annot.get("/FT") != "/Btn":
            continue
        field_name = str(annot.get("/T", ""))
        if field_name not in values or values[field_name] in {"", None}:
            continue
        normal = (annot.get("/AP") or {}).get("/N")
        states = set(normal.keys()) if hasattr(normal, "keys") else set()
        selected = next((state for state in states if str(state) != "/Off"), NameObject("/Yes"))
        annot[NameObject("/V")] = selected
        annot[NameObject("/AS")] = selected
        for kid_ref in annot.get("/Kids") or []:
            kid = kid_ref.get_object()
            kid_normal = (kid.get("/AP") or {}).get("/N")
            kid_states = set(kid_normal.keys()) if hasattr(kid_normal, "keys") else set()
            kid_selected = next((state for state in kid_states if str(state) != "/Off"), selected)
            kid[NameObject("/V")] = kid_selected
            kid[NameObject("/AS")] = kid_selected


def set_button_group_state(acroform, field_name, state_name):
    target_state = NameObject(f"/{state_name}")
    for field_ref in acroform.get("/Fields") or []:
        field = field_ref.get_object()
        if str(field.get("/T", "")) != field_name:
            continue
        field[NameObject("/V")] = target_state
        for kid_ref in field.get("/Kids") or []:
            kid = kid_ref.get_object()
            normal = (kid.get("/AP") or {}).get("/N")
            states = set(normal.keys()) if hasattr(normal, "keys") else set()
            selected = target_state if target_state in states else NameObject("/Off")
            kid[NameObject("/AS")] = selected
            kid[NameObject("/V")] = selected


def draw_mark(c, x, y, size):
    c.rect(x, y, size, size, fill=1, stroke=0)


def draw_text(c, item, data):
    value = item.get("literal", get_nested(data, item.get("key", "")))
    if item.get("key") == "client.full_name":
        value = client_full_name(data)
    elif item.get("key") == "client.ethnicity":
        options = data.get("client", {}).get("ethnicity_options") or []
        value = "; ".join(str(item) for item in options) if options else value
    elif item.get("key") == "clinical.primary_diagnosis":
        value = diagnosis_label_without_code(value)
    elif item.get("key") == "clinical.icd_code" and not value:
        value = diagnosis_code_from_text(get_nested(data, "clinical.primary_diagnosis", ""))
    field_limits = data.get("_field_limits", {})
    limit_key = item.get("key") or item.get("literal", "")
    value = fit_text(value, limit_chars(field_limits, "oar", limit_key, item.get("max_chars")))
    font = "Helvetica-Bold" if item.get("bold") else "Helvetica"
    c.setFont(font, float(item.get("size", 8)))
    c.drawString(float(item["x"]), float(item["y"]), value)


def should_draw_mark(item, data):
    key = item.get("key", "")
    client = data.get("client", {})
    clinical = data.get("clinical", {})
    suicidal = clinical.get("suicidal", {})
    homicidal = clinical.get("homicidal", {})
    has_medications = any(str(clinical.get(key, "")).strip() for key in (
        "medication_1_name",
        "medication_2_name",
        "medication_3_name",
        "medications",
    ))
    request_type = clinical.get("request_type", "Initial Request").lower()
    sex = client.get("sex", "").lower()
    living = client.get("living_situation", "").lower()
    regional_center = str(data.get("regional_center_client") or clinical.get("regional_center_client") or "No").lower()
    cfwb = str(data.get("cfwb_referral") or ("Yes" if clinical.get("cfwb_referral_yes") else "No")).lower()
    justice = str(data.get("justice_system_involvement") or ("Yes" if clinical.get("justice_system_involvement_yes") else "N/A")).lower()
    problem_status = clinical.get("problem_list_status", "Reviewed/updated").lower()
    substance = clinical.get("substance_use", "").lower()
    trauma_present = bool(clinical.get("trauma_yes")) or bool(clinical.get("trauma_history"))

    rules = {
        "initial_request": "continuing" not in request_type,
        "continuing_request": "continuing" in request_type,
        "gender_male": sex == "male",
        "gender_female": sex == "female",
        "gender_other": sex in {"other", "intersex", "unknown", "prefer not to answer"},
        "living_homeless": living == "homeless",
        "living_alone": living == "alone",
        "living_ilf": living == "ilf",
        "living_board_care": living in {"board and care", "b&c"},
        "living_snf": living == "snf",
        "living_other": living == "other",
        "regional_center_yes": regional_center == "yes",
        "regional_center_no": regional_center == "no",
        "employment_employed": clinical.get("employment_status", "").lower() == "employed",
        "employment_student": clinical.get("employment_status", "").lower() == "student",
        "employment_homemaker": clinical.get("employment_status", "").lower() == "homemaker",
        "employment_retired": clinical.get("employment_status", "").lower() == "retired",
        "employment_unemployed": clinical.get("employment_status", "").lower() == "unemployed",
        "employment_seeking_work": clinical.get("employment_status", "").lower() == "seeking work",
        "employment_not_in_labor_force": clinical.get("employment_status", "").lower() == "not in labor force",
        "employment_unknown": clinical.get("employment_status", "").lower() == "unknown",
        "employment_other": clinical.get("employment_status", "").lower() == "other",
        "justice_na": justice in {"n/a", "na", "no"},
        "justice_yes": justice == "yes",
        "cfwb_yes": cfwb == "yes",
        "cfwb_no": cfwb == "no",
        "problem_list_reviewed": "review" in problem_status,
        "problem_list_no_changes": "no change" in problem_status,
        "impairment_social_yes": bool(clinical.get("impairment_social")),
        "impairment_social_no": not bool(clinical.get("impairment_social")),
        "impairment_occupational_yes": bool(clinical.get("impairment_occupational")),
        "impairment_occupational_no": not bool(clinical.get("impairment_occupational")),
        "impairment_other_yes": bool(clinical.get("impairment_activities")),
        "impairment_other_no": not bool(clinical.get("impairment_activities")),
        "deterioration_yes": bool(clinical.get("impairment_deterioration")),
        "deterioration_no": not bool(clinical.get("impairment_deterioration")),
        "developmental_yes": bool(clinical.get("impairment_developmental")),
        "developmental_no": not bool(clinical.get("impairment_developmental")),
        "trauma_yes": trauma_present,
        "trauma_no": not trauma_present,
        "substance_no": substance.startswith("no"),
        "substance_history": substance.startswith("history"),
        "substance_current": substance.startswith("current"),
        "suicidal_no": bool(suicidal.get("no")),
        "suicidal_ideation": bool(suicidal.get("ideation")),
        "suicidal_plan": bool(suicidal.get("plan")),
        "suicidal_intent": bool(suicidal.get("intent")),
        "suicidal_history_of_harm": bool(suicidal.get("history_of_harm")),
        "homicidal_no": bool(homicidal.get("no")),
        "homicidal_ideation": bool(homicidal.get("ideation")),
        "homicidal_plan": bool(homicidal.get("plan")),
        "homicidal_intent": bool(homicidal.get("intent")),
        "homicidal_history_of_harm": bool(homicidal.get("history_of_harm")),
        "no_medications": (bool(clinical.get("no_medications")) or clinical.get("medications", "").lower().startswith("no")) and not has_medications,
        "interpreter_no": clinical.get("interpreter_needed", "No").lower() == "no" and not clinical.get("interpreter_needed_yes"),
        "interpreter_yes": clinical.get("interpreter_needed", "").lower() == "yes" or bool(clinical.get("interpreter_needed_yes")),
        "group_therapy": any(str(clinical.get(key, "")).strip() for key in (
            "group_therapy",
            "group_participants",
            "group_topic",
            "group_sessions_begin_date",
            "group_sessions_count",
            "group_sessions_frequency",
        )),
        "tcm_medical": bool(clinical.get("tcm_medical")) or bool(str(clinical.get("tcm_medical_explain", "")).strip()),
        "tcm_social": bool(clinical.get("tcm_social")) or bool(str(clinical.get("tcm_social_explain", "")).strip()),
        "tcm_educational": bool(clinical.get("tcm_educational")) or bool(str(clinical.get("tcm_educational_explain", "")).strip()),
        "tcm_other": bool(clinical.get("tcm_other")) or bool(str(clinical.get("tcm_other_explain", "")).strip()),
    }
    return rules.get(key, False)


def build_overlay(page_width, page_height, page_index, oar_map, data):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFillColorRGB(0, 0, 0)

    for item in oar_map["marks"]:
        if int(item["page"]) == page_index and should_draw_mark(item, data):
            draw_mark(c, float(item["x"]), float(item["y"]), float(item.get("size", 4.6)))

    for item in oar_map["text"]:
        if int(item["page"]) == page_index:
            draw_text(c, item, data)

    signature_path = str(data.get("paths", {}).get("signature_image", "")).strip()
    signature = Path(signature_path) if signature_path and "C:\\path\\to" not in signature_path else BUNDLED_SIGNATURE
    if page_index == 1 and signature.exists():
        c.drawImage(str(signature), 132.0, 310.5, width=78.0, height=20.0, mask="auto")

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def fill_oar_flattened(data, output_dir):
    oar_map = load_json(OAR_MAP)
    data = {**data, "_field_limits": load_field_limits()}
    diagnosis_code = diagnosis_code_from_text(get_nested(data, "clinical.primary_diagnosis", ""))
    if diagnosis_code and not get_nested(data, "clinical.icd_code", ""):
        data.setdefault("clinical", {})["icd_code"] = diagnosis_code
    configured_template = str(data.get("paths", {}).get("oar_template", "")).strip()
    template = Path(configured_template) if configured_template and "C:\\path\\to" not in configured_template else BUNDLED_OAR_TEMPLATE
    output = output_dir / f"OAR Psychotherapy - {safe_name(client_full_name(data))} flattened.pdf"

    reader = PdfReader(str(template))
    writer = PdfWriter()

    for index, page in enumerate(reader.pages):
        overlay = build_overlay(float(page.mediabox.width), float(page.mediabox.height), index, oar_map, data)
        page.merge_page(overlay)
        if "/Annots" in page:
            del page["/Annots"]
        writer.add_page(page)

    root = writer._root_object
    if "/AcroForm" in root:
        del root["/AcroForm"]

    with output.open("wb") as f:
        writer.write(f)
    return output


def fill_timeliness(data, output_dir):
    field_limits = load_field_limits()
    configured_template = str(data.get("paths", {}).get("timeliness_template", "")).strip()
    template = Path(configured_template) if configured_template and "C:\\path\\to" not in configured_template else BUNDLED_TIMELINESS_TEMPLATE
    output = output_dir / f"Psychotherapy Timeliness Record - {safe_name(client_full_name(data))} filled.pdf"

    client = data.get("client", {})
    insurance = data.get("insurance", {})
    clinical = data.get("clinical", {})
    provider = data.get("provider", {})
    first_contact_date = clinical.get("first_contact_date") or clinical.get("sessions_begin_date", "")
    first_contact_time = clinical.get("first_contact_time") or "09:00"
    offered_date = clinical.get("first_appointment_offered_date") or first_contact_date
    offered_time = clinical.get("first_appointment_offered_time") or first_contact_time
    rendered_date = clinical.get("first_appointment_rendered_date") or first_contact_date
    rendered_time = clinical.get("first_appointment_rendered_time") or first_contact_time
    follow_up_offered_date = clinical.get("follow_up_offered_date") or rendered_date
    follow_up_offered_time = clinical.get("follow_up_offered_time") or rendered_time
    follow_up_rendered_date = clinical.get("follow_up_rendered_date") or rendered_date
    follow_up_rendered_time = clinical.get("follow_up_rendered_time") or rendered_time

    values = {
        "Clien Clientt Name": fit_text(client_full_name(data), limit_chars(field_limits, "timeliness", "client.full_name")),
        "MediCal": fit_text(insurance.get("medi_cal_cin", ""), limit_chars(field_limits, "timeliness", "insurance.medi_cal_cin")),
        "DOB": fit_text(client.get("dob", ""), limit_chars(field_limits, "timeliness", "client.dob")),
        "Date3_af_date": fit_text(first_contact_date, limit_chars(field_limits, "timeliness", "clinical.first_contact_date")),
        "Time": fit_text(first_contact_time, limit_chars(field_limits, "timeliness", "clinical.first_contact_time")),
        "Dropdown1": fit_text(clinical.get("referral_source", "Self"), limit_chars(field_limits, "timeliness", "clinical.referral_source")),
        "Date4_af_date": fit_text(offered_date, limit_chars(field_limits, "timeliness", "clinical.first_appointment_offered_date")),
        "Time_2": fit_text(offered_time, limit_chars(field_limits, "timeliness", "clinical.first_appointment_offered_time")),
        "Date5_af_date": fit_text(rendered_date, limit_chars(field_limits, "timeliness", "clinical.first_appointment_rendered_date")),
        "Time_3": fit_text(rendered_time, limit_chars(field_limits, "timeliness", "clinical.first_appointment_rendered_time")),
        "Date6_af_date": fit_text(follow_up_offered_date, limit_chars(field_limits, "timeliness", "clinical.follow_up_offered_date")),
        "Time_4": fit_text(follow_up_offered_time, limit_chars(field_limits, "timeliness", "clinical.follow_up_offered_time")),
        "Date7_af_date": fit_text(follow_up_rendered_date, limit_chars(field_limits, "timeliness", "clinical.follow_up_rendered_date")),
        "Time_5": fit_text(follow_up_rendered_time, limit_chars(field_limits, "timeliness", "clinical.follow_up_rendered_time")),
        "Text13": fit_text(clinical.get("timeliness_comments") or clinical.get("delay_reason", ""), limit_chars(field_limits, "timeliness", "clinical.timeliness_comments")),
        "Text10": fit_text(provider.get("name_license", ""), limit_chars(field_limits, "timeliness", "provider.name_license")),
        "Date1_af_date": fit_text(provider.get("date", ""), limit_chars(field_limits, "timeliness", "provider.date")),
        "Text2": fit_text("", limit_chars(field_limits, "timeliness", "reserved.Text2")),
        "Text3": fit_text("", limit_chars(field_limits, "timeliness", "reserved.Text3")),
    }

    delayed_access = str(clinical.get("delayed_access", "No")).lower()
    delayed = delayed_access in {"yes", "y", "true", "1"}
    checkbox_values = {
        "Check Box46": "/Yes",
        "Check Box45": "/Yes" if str(clinical.get("urgent_request", "Yes")).lower() in {"yes", "y", "true", "1"} else "",
        "Check Box48": "/Yes",
        "Check Box50": "/Yes",
        "Check Box44": "/Yes" if not delayed else "",
        "Check Box52": "/Yes",
        "Check Box54": "/Yes",
        "Check Box42": "/Yes" if not delayed else "",
        "Check Box40": "/Yes",
        "Check Box57": "/Yes",
    }
    all_values = {**values, **{key: value for key, value in checkbox_values.items() if value}}

    reader = PdfReader(str(template))
    writer = PdfWriter()
    writer.append(reader)

    for page in writer.pages:
        for annot_ref in page.get("/Annots") or []:
            annot = annot_ref.get_object()
            if annot.get("/FT") == "/Tx":
                annot[NameObject("/DA")] = TextStringObject(f"/Helv {FORM_FONT_SIZE} Tf 0 g")
        writer.update_page_form_field_values(page, all_values, auto_regenerate=True)
        for annot_ref in page.get("/Annots") or []:
            annot = annot_ref.get_object()
            if annot.get("/T") in all_values and annot.get("/FT") == "/Btn":
                annot[NameObject("/V")] = NameObject("/Yes")
                annot[NameObject("/AS")] = NameObject("/Yes")

    acroform = writer._root_object.get("/AcroForm")
    if acroform:
        acroform.update({
            NameObject("/DA"): TextStringObject(f"/Helv {FORM_FONT_SIZE} Tf 0 g"),
            NameObject("/NeedAppearances"): BooleanObject(True),
        })

    with output.open("wb") as f:
        writer.write(f)
    return output


def main():
    parser = argparse.ArgumentParser(description="Fill Demographic and OAR PDFs from structured JSON input.")
    parser.add_argument("--input", required=True, help="Path to patient_input.json")
    parser.add_argument("--skip-demographic", action="store_true")
    parser.add_argument("--skip-oar", action="store_true")
    parser.add_argument("--skip-timeliness", action="store_true")
    args = parser.parse_args()

    data = load_json(args.input)
    output_dir = resolve_output_dir(data)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    if not args.skip_demographic:
        outputs.append(fill_demographic(data, output_dir))
    if not args.skip_oar:
        outputs.append(fill_oar_flattened(data, output_dir))
    if not args.skip_timeliness:
        outputs.append(fill_timeliness(data, output_dir))

    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
