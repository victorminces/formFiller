# Reusable OAR + Demographic PDF Workflow

## AI Instructions

If an AI is processing a packet, read `AI_WORKFLOW.md` first. It is the mandatory short workflow for source priority, field locking, conflict reporting, missing information, measured text fitting, and output folder placement.

Use `field_maps/field_fit_spec.json` as the source of truth for measured PDF field fitting. `AI_FORM_FILLING_RULES.md` is a longer reference.

This folder is designed to be copied into another Codex account or workspace.
It describes a reusable workflow for extracting client data from files and filling
the Demographic and OAR PDFs.

Keep client files and generated PDFs in secure locations. Do not put real client
data into the example JSON file unless the workspace is appropriate for PHI.

## Folder Contents

- `fill_forms.py`  
  Main reusable Python program. It reads structured client/provider data from JSON,
  fills the Demographic form with AcroForm fields, and fills the OAR as a flattened
  visual PDF.

- `patient_input.example.json`  
  Example input structure. Replace `XXXX` placeholders with real data for each client.

- `field_maps/demographic_2024.json`  
  Maps normalized data keys to the Demographic form's fillable field names.

- `field_maps/oar_psychotherapy_2025.json`  
  Maps normalized data keys to exact page coordinates for the flattened OAR overlay.

- `render_pdf_screenshot.js`  
  Renders a PDF to a PNG screenshot using Edge/Chromium so the final output can be
  visually checked.

- `requirements.txt`  
  Python dependencies.

## High-Level Workflow

1. Put the blank form templates somewhere accessible.
   - Demographic form PDF
   - OAR Psychotherapy PDF

2. Gather client source material.
   - Images of IDs/cards/messages
   - Scanned PDFs
   - Text PDFs
   - User-provided descriptions
   - Spreadsheets or exports

3. Extract the data into `patient_input.json`.
   - Use `patient_input.example.json` as the structure.
   - If the source PDF has selectable text, extract text directly.
   - If the source is scanned/image-based, inspect/OCR the image and manually confirm uncertain values.

4. Run the form filler.
   ```powershell
   python fill_forms.py --input patient_input.json
   ```

5. Render the final OAR PDF to an image.
   ```powershell
   node render_pdf_screenshot.js "C:\path\to\OAR flattened.pdf" "C:\path\to\oar_check.png"
   ```

6. Visually inspect the screenshot.
   - Confirm all checkboxes are in the right places.
   - Confirm text is not clipped, overlapping, or too small.
   - Condense text in `patient_input.json` if needed and rerun.

## Intake Data Categories

Extract and normalize these categories from all source files.

### Identity

- Legal name
- First / middle / last name
- DOB
- Age
- Sex
- Gender identity
- Sexual orientation
- Ethnicity/race
- Primary/preferred language
- Place of birth
- Mother's first name

### Contact

- Address
- Phone
- Living situation
- Lives with whom
- Marital status
- Education
- Military/veteran status

### Insurance

- Medi-Cal CIN
- Benefits ID
- Plan/member number
- Effective date
- PCP name/address/phone

### Clinical OAR

- Primary diagnosis
- ICD code
- Other diagnoses/medical conditions
- Current symptoms
- Significant impairment
- Trauma history
- Substance use
- Suicide/homicide risk
- Interventions
- Requested service type
- Begin date
- Number of sessions
- Frequency

## Why The OAR Is Flattened

The OAR PDF has unreliable fillable fields. Some narrative fields are visually
single-line even when the metadata suggests they can be multiline. Acrobat and
browser PDF viewers may also render field appearances differently.

For the OAR, the reliable approach is:

1. Use the blank PDF as a background.
2. Draw text directly at exact coordinates.
3. Draw checkbox marks directly.
4. Remove PDF form fields/annotations.
5. Render the PDF to an image and visually inspect it.

This creates a visually stable PDF for fax/mail/upload workflows.

## Text-Fit Strategy

The field map includes a `max_chars` value for constrained fields. The program
will truncate long text with `...`, but the preferred workflow is to provide
condensed clinical wording in the input JSON.

Good OAR wording is short:

- Diagnosis: `MDD, recurrent, severe`
- Symptoms: `Daily severe depression/grief; SI/desire; low motivation; impaired self-care/ADLs.`
- Impairment: `Impaired ADLs/social/medical/role function; poor self-care; likely deterioration without care.`
- Trauma: `Mother died of cancer within past year; caregiver/best friend. Trauma/grief noted.`
- Interventions: `CBT/DBT-informed therapy; safety planning; grief/trauma support; care coordination.`

If a field looks crowded in the rendered image, shorten the input text first.
