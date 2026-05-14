# PDF Mapping Coverage Audit

Goal: the app should collect data once and generate the Demographic, OAR Psychotherapy, and Psychotherapy Timeliness PDFs directly.

Current direct path:

`gui_qt.py` UI fields -> `collect_data()` JSON -> `apply_workflow_defaults()` / `normalize_app_data()` -> `fill_forms.py` -> generated PDFs.

## Status Summary

- Demographic: app fields that appear on the current demographic form are mapped through `field_maps/demographic_2024.json` and `fill_demographic()`.
- OAR Psychotherapy: app fields that appear on the current OAR form are mapped through `field_maps/oar_psychotherapy_2025.json` and `fill_oar_flattened()`.
- Timeliness: app fields that appear on the current timeliness form are mapped in `fill_timeliness()`. This works, but it is still hardcoded in Python rather than a JSON map.
- Output/source-file fields are workflow controls, not PDF fields.
- Group therapy, TCM, and other-service UI fields were removed because they are not part of the current desired workflow.

## Demographic Form Coverage

Mapped text fields:

| App/JSON field | PDF target |
|---|---|
| `provider.date` | Date of Completion (`Text4`) |
| `client.full_name` | Client Name (`Text3`) |
| `client.name_at_birth_first` | First Name at Birth |
| `client.name_at_birth_middle` | Middle Name at Birth |
| `client.name_at_birth_last` | Last Name at Birth |
| `client.first_name` | Current First Name |
| `client.middle_name` | Current Middle Name |
| `client.last_name` | Current Last Name |
| `client.mothers_first_name` | Mother's First Name |
| `client.place_of_birth_country` | Place of Birth - Country |
| `client.place_of_birth_state` | Place of Birth - State |
| `client.place_of_birth_county` | Place of Birth - County |
| `client.primary_language` | Primary Language |
| `client.preferred_language` | Preferred Language |
| `client.social_security_number` | Social Security Number |
| `client.education` | Highest Completed Education Level |
| `client.phone` | Phone line matching `client.phone_type` |
| `client.address` | Address |
| `client.aliases` | List any Aliases |
| `client.legal_class_admission` | Legal Class at Admission |
| `client.discharge_facility` | Discharged to a Facility detail |
| `client.responsible_under_18_count` | Persons under 18 responsibility count |
| `client.responsible_over_17_count` | Persons over 17 responsibility count |

Mapped checkbox/radio fields:

| App/JSON field | PDF target |
|---|---|
| `client.suffix_at_birth` | JR/SR/II/III/IV/V/VI checkboxes |
| `client.ethnicity_options` | Ethnicity checkboxes |
| `client.hispanic_latino_status` | Hispanic/Latino Yes/No/Unknown |
| `client.same_first_name` | Same as First Name at Birth |
| `client.same_last_name` | Same as Last Name at Birth |
| `client.same_middle_name` | Same as Middle Name at Birth |
| `client.special_population_services` | Special Population Services checkboxes |
| `client.discharge_acute` | Acute 24-hour discharge checkbox |
| `client.patient_status` | Discharged Home / Facility / Unknown |
| `client.not_currently_enrolled` | Not Currently Enrolled |
| `client.court_status` | Conservatorship/Court Status checkboxes |
| `client.phone_type` | Mobile / Business / Home |
| `client.do_not_call` | Do Not Call |
| `client.do_not_leave_message` | Do Not Leave Message |
| `client.address_physical` | Physical |
| `client.address_mailing` | Mailing |
| `client.race_options` | Race checkboxes |
| `client.marital_status` | Marital status checkboxes |
| `client.sex` | Male / Female / Not Listed |
| `client.gender_identity` | Gender identity checkboxes |
| `client.sexual_orientation` | Sexual orientation checkboxes |
| `client.military_status` | Military Yes/No radio group |
| `client.veteran_status` | Veteran Yes/No radio group |

Known visual item:

- The address field should keep the full address. If a viewer cuts it visually, fix rendering/flattening; do not shorten the data by default.

## OAR Psychotherapy Coverage

Mapped identity/referral fields:

| App/JSON field | PDF target |
|---|---|
| `clinical.request_type` | Initial / Continuing request |
| `client.full_name` | Client Name |
| `client.sex` | Gender M/F/O |
| `client.age` | Age |
| `client.dob` | DOB |
| `client.ethnicity` | Client Ethnicity text |
| `insurance.medi_cal_cin` | Medi-Cal # |
| `client.living_situation` | Living Situation checkboxes |
| `client.living_with` | Other living situation detail |
| `clinical.regional_center_client` | Regional Center Yes/No |
| `clinical.employment_status` | Employment/School Status checkboxes |
| `clinical.justice_system_involvement_yes` | Justice System Yes/N/A |
| `clinical.justice_system_involvement_explain` | Justice detail |
| `clinical.cfwb_referral_yes` | CFWB Yes/No |
| `clinical.cfwb_psw` | PSW name/number |
| `clinical.cws_history` | CWS/CFWB history detail |

Mapped clinical fields:

| App/JSON field | PDF target |
|---|---|
| `clinical.primary_diagnosis` | Primary DSM/ICD Diagnosis |
| `clinical.icd_code` | ICD Code, derived from diagnosis if needed |
| `clinical.other_diagnoses` | Other Diagnoses |
| `clinical.current_symptoms` | Current Symptoms |
| `clinical.problem_list_status` | Reviewed/updated / No changes |
| `clinical.problem_list_date` | Problem List Date |
| `clinical.impairment_social` | Social/Relational Yes/No |
| `clinical.impairment_occupational` | Occupational/Academic Yes/No |
| `clinical.impairment_activities` | Other Activities Yes/No |
| `clinical.impairment_deterioration` | Deterioration Yes/No |
| `clinical.impairment_developmental` | Under-21 developmental progress Yes/No |
| `clinical.significant_impairment` | Explain Significant Impairment |
| `clinical.trauma_yes` / `clinical.trauma_history` | Trauma Yes/No and explanation |
| `clinical.substance_use` | Substance Use No/History/Current |
| `clinical.drugs_of_choice` | Drug(s) of choice |
| `clinical.substance_use_impact` | Current substance-use impact |
| `clinical.risk.suicidal` | Suicidal risk checkboxes |
| `clinical.risk.homicidal` | Homicidal risk checkboxes |
| `clinical.no_medications` | No Medications |
| `clinical.medication_1_name` | Medication 1 name |
| `clinical.medication_1_dosage` | Medication 1 dosage |
| `clinical.medication_2_name` | Medication 2 name |
| `clinical.medication_2_dosage` | Medication 2 dosage |
| `clinical.interventions` | Interventions |
| `clinical.interpreter_needed_yes` / `clinical.interpreter_needed` | Interpreter Yes/No |
| `clinical.interpreter_language` | Interpreter language |
| `clinical.sessions_begin_date` | Psychotherapy begin date |
| `clinical.sessions_count` | Psychotherapy number of sessions |
| `clinical.sessions_frequency` | Psychotherapy frequency |

Mapped provider fields:

| App/JSON field | PDF target |
|---|---|
| `provider.name_license` | Name/Licensure |
| `provider.phone` | Phone |
| `provider.fax` | Fax |
| `paths.signature_image` | Provider signature image |
| `provider.date` | Provider date |
| `provider.group_practice_name` | Group practice name |
| `provider.waive_verbal_notification` | Waive verbal notification checkbox |

Intentional OAR limitation:

- `clinical.medication_3_name` and `clinical.medication_3_dosage` are collected but the current OAR medication table only has two visible medication slots in the mapped area.

## Timeliness Coverage

Mapped fields in `fill_timeliness()`:

| App/JSON field | PDF target |
|---|---|
| `client.full_name` | Client Name |
| `insurance.medi_cal_cin` | Medi-Cal |
| `client.dob` | DOB |
| `clinical.first_contact_date` | First contact date |
| `clinical.first_contact_time` | First contact time |
| `clinical.referral_source` | Referral source |
| `clinical.first_appointment_offered_date` | First appointment offered date |
| `clinical.first_appointment_offered_time` | First appointment offered time |
| `clinical.first_appointment_rendered_date` | First appointment rendered date |
| `clinical.first_appointment_rendered_time` | First appointment rendered time |
| `clinical.follow_up_offered_date` | Follow-up offered date |
| `clinical.follow_up_offered_time` | Follow-up offered time |
| `clinical.follow_up_rendered_date` | Follow-up rendered date |
| `clinical.follow_up_rendered_time` | Follow-up rendered time |
| `clinical.timeliness_comments` / `clinical.delay_reason` | Timeliness comments |
| `provider.name_license` | Provider name/licensure |
| `provider.date` | Provider date |
| `clinical.urgent_request` | Urgent/non-urgent checkbox logic |
| `clinical.delayed_access` | Delayed access checkbox logic |
| `clinical.follow_up_delayed_access` | Follow-up delay checkbox logic |
| `clinical.extended_wait_clinically_appropriate` | Extended-wait checkbox logic |

Cleanup still recommended:

- Move the timeliness mapping from hardcoded Python field names into a JSON map, like Demographic and OAR. Direct generation works now, but JSON mapping would make future audits easier.

## Workflow Fields With No PDF Target

These fields support export/generation, not a printed PDF field:

- `paths.output_dir`
- attachment/source-file list

These insurance fields are collected for packets/source review but do not currently appear on the three generated PDFs:

- `insurance.benefits_id`
- `insurance.member_number`
- `insurance.plan_name`
- `insurance.effective_date`
- `insurance.pcp_name`
- `insurance.pcp_address`
- `insurance.pcp_phone`

## Verification Rule

For future app changes, do not add a UI field unless it is one of:

1. Mapped to a PDF target in this audit.
2. Explicitly marked as workflow-only.
3. Explicitly marked as collected-but-not-on-current-forms.

Before considering the app complete for a form version, generate test PDFs and visually inspect:

- all checkboxes/radio groups,
- all dates/times,
- address rendering,
- narrative text fitting,
- medication and risk sections,
- timeliness offered/rendered/follow-up date relationships.
