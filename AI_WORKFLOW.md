# AI Workflow

## Purpose

This workflow fills behavioral health intake/authorization PDFs from a packet exported by the local desktop app.

The app collects raw patient/client data, therapist-entered clinical text, and source files such as PDFs, scans, benefits cards, and intake forms. The AI's job is to extract and reconcile the data, create a field-ready JSON, shorten clinical text to fit the measured PDF fields, and generate the completed PDFs.

The forms currently produced are:

- Demographic Form
- OAR Psychotherapy Form
- Psychotherapy Timeliness Record

The OAR form must be generated as a flattened PDF because its writable PDF fields are unreliable.

## AI Role

The AI is not the clinical decision-maker. It prepares form-ready documentation from the provided packet, preserves therapist-entered data, flags conflicts, lists missing information, and avoids inventing unsupported facts.

## Files To Load First

Load these files before processing a packet:

- `AI_WORKFLOW.md` - mandatory workflow and priority rules
- `field_maps/field_fit_spec.json` - source of truth for measured field widths
- `field_maps/field_fit_spec.md` - human-readable field fit summary
- `fill_forms.py` - PDF generation script
- `patient_input.example.json` - expected data structure

Use `AI_FORM_FILLING_RULES.md` only as a longer reference if the short workflow is not enough.

## Non-Negotiable Rules

- Never overwrite a locked field with lower-priority data.
- Never hard truncate text.
- Always report conflicts.
- Always report missing information.
- Save final deliverables in a patient-specific folder beside the source ZIP.
- Do not invent facts that are not supported by the packet or therapist-entered app data.
- Do not merge data from two different people.

## Source Priority

Use sources in this order:

1. App JSON: `patient_input.json`
2. Computer-generated/selectable-text PDFs
3. Images, photographed documents, scans, and OCR/visual extraction

## Locking Rules

Create a new `patient_input.field_ready.json`. Do not directly overwrite `patient_input.json`.

Stage 1: Fill from app JSON first.

- Treat app-entered fields as source material, especially therapist-entered clinical narrative fields.
- Ignore obvious placeholders such as `XXXX`, `XX/XX/XXXX`, `XXX-XXX-XXXX`, empty strings, and known test/demo text only when there is no reason to treat them as real.
- Once a field is filled from app JSON, mark it locked.

Stage 2: Fill from selectable-text PDFs.

- Determine which PDFs have computer-generated/selectable text.
- Extract text directly from those PDFs.
- Fill only fields that are still empty/unlocked.
- If a value conflicts with a locked app-JSON value, report the conflict and do not overwrite the locked value.

Stage 3: Fill from images/scans/OCR.

- Use image and scan data last.
- Fill only fields that are still empty/unlocked.
- If image-derived data conflicts with a locked value, report the conflict and do not overwrite the locked value.

## Conflict Policy

Always report conflicts before or during final output review. Include:

- the conflicting field
- each conflicting value
- which source contained each value
- which value was used, if any
- which values were left out because they were unsafe to merge

If identity, DOB, or insurance data appears to belong to a different person, do not merge it.

## Missing Information Policy

After all sources are processed, list missing information. Include fields that are required, clinically important, or useful for clean form completion but not supported by the packet.

For each missing item, state:

- the missing field
- where it would appear, if known
- whether it was left blank or defaulted
- why it was not filled

Common missing items include phone number, Medi-Cal/CIN, member/benefits ID, PCP phone, session dates, session count/frequency, timeliness dates/times, interpreter choice, urgent/delayed-access choice, signature image, and required clinical details not present in the packet.

## Field Fitting

Use `field_maps/field_fit_spec.json` as the source of truth.

For each candidate field value:

1. Use the field's `font`, `font_size`, `max_width_points`, and `lines`.
2. Measure the rendered width of the exact candidate string.
3. If it fits, keep it.
4. If it does not fit, rewrite it shorter while preserving meaning.
5. Measure again.
6. Repeat until it fits.

Do not hard truncate. Do not append `...` as a fitting strategy. Character counts in legacy files are examples only.

Narrative fields should be concise clinical summaries, not raw pasted paragraphs.

## PDF Generation

Generate PDFs from `patient_input.field_ready.json` using:

```powershell
python fill_forms.py --input patient_input.field_ready.json
```

The OAR must be flattened. Do not rely on the OAR's writable PDF fields.

## Output Folder

Create a patient-specific folder inside the exact directory that contains the ZIP packet. Use the ZIP file's parent folder as-is.

Example:

```text
Downloads/
  Client Packet - Example Name.zip
  Example Name/
    Client Packet - Example Name.zip
    manifest.json
    patient_input.json
    patient_input.field_ready.json
    review_notes.md
    Demographic Form - Example Name filled.pdf
    OAR Psychotherapy - Example Name flattened.pdf
    Psychotherapy Timeliness Record - Example Name filled.pdf
```

Do not create a parallel output location for final deliverables.

## Review Notes

Create `review_notes.md` in the patient folder. It must include:

- packet path
- source files reviewed
- extracted data used
- conflicts
- missing information
- notes about placeholder values ignored
- notes about any fields left blank or defaulted

## Final Response

Report:

- patient folder path
- generated PDF names
- conflicts
- missing information summary
- any field-fit or visual risks

