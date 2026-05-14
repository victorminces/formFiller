# AI Form Filling Rules

For packet processing, read `AI_WORKFLOW.md` first. This file is the longer reference. The measured field-fit source of truth is `field_maps/field_fit_spec.json`.

This file is the standing workflow for filling the bundled therapy intake forms from a raw packet exported by the local app. It is intended for this AI and for any other AI that receives the app output.

## Core Rule

The app exports raw material. It is not responsible for shortening clinical text. The AI must extract, reconcile, clinically compress, and produce field-ready text before generating the PDFs.

Never hard truncate text. Do not blindly cut text to a character count. If a field is too long, rewrite it shorter while preserving the clinical meaning. Use ellipses only when quoting a source excerpt, not as a fitting strategy.

## Required Workflow

1. Extract text/data from every source file in the packet, including PDFs and images.
2. Treat app-entered fields in `patient_input.json` as source material, especially therapist-entered clinical narrative fields.
3. Ignore obvious placeholders such as `XXXX`, `XX/XX/XXXX`, `XXX-XXX-XXXX`, empty strings, and known test/demo text only when the packet gives no reason to treat them as real.
4. Compare sources before filling. If identity, DOB, insurance ID, address, diagnosis, dates, or other important fields conflict, stop and flag the conflict clearly.
5. Choose the primary client record only when the source evidence is coherent. Do not merge data from a conflicting person.
6. Build a field-ready JSON from the raw packet. This field-ready JSON should contain concise final wording, not raw narrative dumps.
7. Fill PDFs from the field-ready JSON.
8. Put all generated PDFs and review artifacts in a patient-specific output folder for that run.
9. Use flattened output for forms whose writable fields render unreliably, especially the OAR.
10. After generating the forms, provide a post-execution review that lists conflicts and missing information.
11. Render or visually inspect final PDFs when possible. Check that text stays inside the intended area and does not overlap labels, section headers, checkboxes, or adjacent fields.

## Patient Folder Policy

Each run must produce a patient-specific folder inside the exact directory that contains the ZIP packet. Use the ZIP file's parent folder as-is. Do not create a separate Downloads folder, workspace output folder, or any other parallel location for final deliverables.

Recommended folder contents:

- original ZIP packet or pointer to it
- extracted source files
- `patient_input.raw.json`
- `patient_input.field_ready.json`
- `review_notes.md`
- generated PDFs

If the app generates PDFs into a shared output directory, copy the final PDFs into the patient-specific folder beside the ZIP after generation.

## Conflict Policy

Always report conflicts before filling. State:

- which source files conflict
- which fields conflict
- which value appears in each source
- which source, if any, was used
- which values were left blank because they were unsafe to merge

Example: if an intake PDF is for one client but a benefits card image is for a different person, do not put the card ID on the intake client forms.

## Missing Information Policy

Always list missing information after generating forms. Include fields that were required, clinically important, or useful for clean form completion but were not supported by the source packet or therapist-entered app fields.

For each missing item, state:

- the missing field
- where it would appear, if known
- whether it was left blank or defaulted
- why it was not filled

Common missing items include phone number, Medi-Cal/CIN, member/benefits ID, PCP phone, session dates, session count/frequency, timeliness dates/times, interpreter choice, urgent/delayed-access choice, signature image, and any required clinical detail not present in the packet.

## Fitting Policy

Use `field_maps/field_fit_spec.json` as the source of truth for fitting text. It contains the writable width in PDF points, font, font size, line count, and example fit capacity for every mapped field.

Character counts are examples only, not cutting instructions. The controlling rule is measured rendered width.

For each field:

- Keep short fields factual and compact.
- Use abbreviations only when common and clinically clear.
- Remove filler words, repetition, and source-document phrasing.
- Prefer semicolons over long clauses when space is tight.
- Preserve risk, trauma, diagnosis, impairment, and substance-use meaning.
- Leave blank if the source does not support a value.
- Measure candidate text against the field's `max_width_points` before filling.
- If a candidate is too wide, rewrite it shorter and measure again.

If a narrative field has more source material than fits, synthesize the clinically relevant points into the target size. Do not paste raw paragraphs.

## PDF Findings

The writable PDF widgets are unreliable for layout decisions. The inspected PDF fields are generally not marked multiline, even when the form visually looks narrative. The OAR should be treated as a flattened coordinate-overlay form.

For the current bundled templates:

- Demographic form: AcroForm fields can be used, but field text still must be concise.
- OAR Psychotherapy form: use flattened overlay. Do not trust writable PDF field behavior.
- Timeliness form: AcroForm fields can be used, but comments must be concise.

## OAR Writable Areas and Writing Rules

The OAR page size is letter, 612 x 792 points. Coordinates are PDF points from the bottom-left. Width/height come from inspected field rectangles unless noted. The current filler draws single-line text unless the PDF generation step is explicitly upgraded to wrapped flattened text. Detailed measured-width values for all fields are in `field_maps/field_fit_spec.json` and summarized in `field_maps/field_fit_spec.md`.

| Field | Page | Writable area | Lines to use | Target | Writing rule |
|---|---:|---:|---:|---:|---|
| `client.full_name` | 1 | x 99.4, y 602.2, w 213.2, h 15.1 | 1 | measure width | Legal full name only. |
| `client.age` | 1 | x 444.3, y 602.2, w 45.4, h 15.1 | 1 | measure width | Age as digits. |
| `client.dob` | 1 | x 523.1, y 602.2, w 52.0, h 15.1 | 1 | measure width | MM/DD/YYYY. |
| `client.ethnicity` | 1 | x 109.7, y 585.8, w 202.9, h 15.2 | 1 | measure width | Use compact demographic label. |
| `insurance.medi_cal_cin` | 1 | x 370.9, y 585.8, w 204.3, h 15.2 | 1 | measure width | Use CIN/ID only if source belongs to this client. |
| `client.living_with` | 1 | x 374.1, y 569.3, w 201.1, h 15.5 | 1 | measure width | Brief living arrangement. |
| `clinical.primary_diagnosis` | 1 | x 219.4, y 429.8, w 110.5, h 15.6 | 1 | measure width | Diagnosis label without ICD code; e.g. `PTSD, chronic`. |
| `clinical.icd_code` | 1 | x 383.9, y 429.8, w 191.2, h 15.6 | 1 | measure width | ICD code only; e.g. `F43.12`. |
| `clinical.other_diagnoses` | 1 | x 221.9, y 413.6, w 353.2, h 15.1 | 1 | measure width | Other mental/physical conditions only. Avoid long history. |
| `clinical.current_symptoms` | 1 | x 37.2, y 370.6, w 537.6, h 16.6 PDF widget; visual row can support about 2 compact lines if flattened wrapping is available | 1 with current filler; 2 only with wrapped overlay | measure width | Symptoms plus frequency/duration. Do not include impairment details here. Verify by rendered string width, not raw character count. |
| `clinical.problem_list_date` | 1 | x 306.0, y 354.0, w 269.1, h 15.5 | 1 | measure width | Date only, MM/DD/YYYY. |
| `clinical.significant_impairment` | 1 | x 181.4, y 227.3, w 393.7, h 19.7 | 1 | measure width | Functional impairment caused by symptoms. |
| `clinical.trauma_history` | 1 | x 105.3, y 198.4, w 469.5, h 14.3 | 1 | measure width | Trauma exposure only, no symptom list. |
| `clinical.substance_use` | 1 | x 320.0, y 181.8, w 255.2, h 15.5 | 1 | measure width | Substance status only; e.g. `Denies alcohol, tobacco, recreational drugs.` |
| `clinical.substance_use_impact` | 1 | x 273.1, y 165.5, w 302.1, h 15.2 | 1 | measure width | Impact only; if denied, use `No substance-use impact reported.` |
| `clinical.interventions` | 2 | x 184.3, y 725.6, w 390.5, h 15.5 | 1 | measure width | Planned interventions/modalities only. |
| `clinical.sessions_begin_date` | 2 | x 218.0, y 574.6, w 102.2, h 27.8 | 1 | 10 chars | Date only. |
| `clinical.sessions_count` | 2 | x 322.4, y 574.6, w 72.4, h 27.8 | 1 | 3 chars | Number only. |
| `clinical.sessions_frequency` | 2 | x 397.0, y 574.6, w 177.5, h 27.8 | 1 | 36 chars | Compact frequency, e.g. `1x/week`. |
| `provider.name_license` | 2 | x 117.1, y 351.5, w 457.7, h 15.2 | 1 | 94 chars | Provider name and license. |
| `provider.phone` | 2 | x 77.2, y 334.9, w 317.9, h 15.5 | 1 | 18 chars | Phone number. |
| `provider.date` | 2 | x 429.3, y 307.8, w 145.3, h 25.8 | 1 | 10 chars | Date only. |

### OAR Narrative Targets

Use these as field-ready wording patterns:

- `clinical.current_symptoms`: `Anxiety/depressed mood, irritability, intrusive memories, nightmares, low energy, poor concentration, withdrawal, emotional numbing; most days.`
- `clinical.significant_impairment`: `Emotional distress impairs daily tasks, relationships, support-seeking, and ability to work.`
- `clinical.trauma_history`: `Domestic violence in prior relationship; fled Guatemala due to violence.`
- `clinical.substance_use`: `Denies alcohol, tobacco, and recreational drugs.`
- `clinical.substance_use_impact`: `No substance-use impact reported.`
- `clinical.interventions`: `Trauma-focused CBT/supportive therapy, coping skills, safety/risk monitoring.`

## Demographic Writable Areas and Writing Rules

The Demographic form uses AcroForm fields. These inspected fields are not marked multiline. Keep each value short and factual.

| Field | Page | Writable area | Lines | Target | Rule |
|---|---:|---:|---:|---:|---|
| `name_at_birth_first` | 1 | x 138.4, y 646.9, w 159.4, h 22.4 | 1 | 32 chars | First name at birth. |
| `name_at_birth_last` | 1 | x 400.2, y 646.6, w 175.1, h 22.4 | 1 | 35 chars | Last name at birth. |
| `mothers_first_name` | 1 | x 144.8, y 583.4, w 430.4, h 21.7 | 1 | 89 chars | Mother's first name only if requested. |
| `place_of_birth_country` | 1 | x 159.2, y 559.8, w 137.8, h 21.9 | 1 | 27 chars | Country. |
| `place_of_birth_state` | 1 | x 410.7, y 559.8, w 164.6, h 21.9 | 1 | 33 chars | State/province/city if source gives it. |
| `place_of_birth_county` | 1 | x 159.2, y 536.3, w 416.0, h 21.7 | 1 | 85 chars | County only if source gives it. |
| `primary_language` | 1 | x 137.0, y 512.6, w 160.0, h 22.4 | 1 | 32 chars | Primary language. |
| `preferred_language` | 1 | x 404.8, y 512.6, w 170.5, h 22.4 | 1 | 34 chars | Preferred language. |
| `current_first_name` | 1 | x 286.2, y 201.6, w 289.1, h 22.2 | 1 | 59 chars | Current first name. |
| `current_last_name` | 1 | x 286.2, y 178.4, w 289.1, h 21.6 | 1 | 59 chars | Current last name. |
| `education` | 2 | x 218.2, y 643.3, w 90.7, h 22.3 | 1 | 18 chars | Use compact level, e.g. `Primary` or `Less than HS`. |
| `phone` | 2 | x 97.7, y 410.9, w 150.0, h 16.8 | 1 | 29 chars | Phone number only. |
| `address` | 2 | x 92.8, y 369.9, w 482.6, h 18.6 | 1 | 99 chars | One-line address. |

## Timeliness Writable Areas and Writing Rules

The Timeliness form uses AcroForm fields. These fields are not marked multiline. Comments must be concise.

| Field | Page | Writable area | Lines | Target | Rule |
|---|---:|---:|---:|---:|---|
| `client.full_name` | 1 | x 107.3, y 646.8, w 170.3, h 28.8 | 1 | 34 chars | Full name. |
| `insurance.medi_cal_cin` | 1 | x 352.0, y 646.8, w 111.0, h 28.8 | 1 | 21 chars | CIN/ID only if source belongs to this client. |
| `client.dob` | 1 | x 523.4, y 646.8, w 69.0, h 28.8 | 1 | 10 chars | MM/DD/YYYY. |
| `clinical.referral_source` | 1 | x 102.7, y 597.4, w 303.9, h 14.1 | 1 | 62 chars | Referral source. |
| `clinical.first_contact_date` | 1 | x 228.7, y 580.1, w 51.5, h 13.0 | 1 | 10 chars | Date only. |
| `clinical.first_contact_time` | 1 | x 397.6, y 580.0, w 46.6, h 12.7 | 1 | 8 chars | Time only. |
| `clinical.first_appointment_offered_date` | 1 | x 282.6, y 522.6, w 51.8, h 12.0 | 1 | 10 chars | Date only. |
| `clinical.first_appointment_offered_time` | 1 | x 397.5, y 522.5, w 46.7, h 11.7 | 1 | 8 chars | Time only. |
| `clinical.first_appointment_rendered_date` | 1 | x 284.1, y 509.4, w 50.3, h 11.7 | 1 | 10 chars | Date only. |
| `clinical.first_appointment_rendered_time` | 1 | x 397.4, y 509.7, w 46.7, h 11.6 | 1 | 8 chars | Time only. |
| `clinical.follow_up_offered_date` | 1 | x 231.3, y 410.9, w 51.8, h 11.4 | 1 | 10 chars | Date only. |
| `clinical.follow_up_offered_time` | 1 | x 397.3, y 410.9, w 46.7, h 11.9 | 1 | 8 chars | Time only. |
| `clinical.follow_up_rendered_date` | 1 | x 243.6, y 397.2, w 50.7, h 11.7 | 1 | 10 chars | Date only. |
| `clinical.follow_up_rendered_time` | 1 | x 397.4, y 396.8, w 46.7, h 11.6 | 1 | 8 chars | Time only. |
| `clinical.timeliness_comments` | 1 | x 78.3, y 351.5, w 501.5, h 16.1 | 1 | 103 chars | Only delay/access comments. |
| `provider.name_license` | 1 | x 157.5, y 176.6, w 286.7, h 15.3 | 1 | 58 chars | Provider name/license. |
| `provider.date` | 1 | x 486.0, y 176.2, w 92.8, h 20.0 | 1 | 10 chars | Date only. |

## Output Review Checklist

Before considering a form complete:

- No field contains raw intake paragraphs.
- No field was hard truncated.
- Conflicts were reported and unsafe conflicting values were left blank.
- Missing information was listed, including fields left blank or defaulted.
- Narrative fields were rewritten to field-ready wording.
- OAR output is flattened.
- Text does not visibly run into labels, section headers, checkboxes, borders, or adjacent fields.
- If any text cannot fit without losing essential meaning, report the limitation instead of forcing it into the form.
