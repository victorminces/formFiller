# Legacy Field Length Limits

This report is retained for historical reference. The current source of truth is `field_fit_spec.json` / `field_fit_spec.md`.

Do not use these values as hard truncation limits. Current workflow requires measuring the actual candidate string against each field's writable width, then rewriting text shorter if needed.

Original calculated caps were based on measured PDF field widths using Helvetica and then reduced by 10% for character-width variability. Checkbox fields are excluded.

Narrative means prose-style content. It does not mean the underlying PDF field is multiline.

## Metadata

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|

## Demographic

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `name_at_birth_first` | First Name at Birth | short | 8 | 159.36 | 30 |
| `name_at_birth_last` | Last Name at Birth | short | 8 | 175.09 | 34 |
| `mothers_first_name` | Mothers First Name | short | 8 | 430.44 | 95 |
| `place_of_birth_country` | Place of Birth  Country | short | 8 | 137.76 | 25 |
| `place_of_birth_state` | Place of Birth  State | short | 8 | 164.62 | 31 |
| `place_of_birth_county` | Place of Birth  County | short | 8 | 416.04 | 92 |
| `primary_language` | Primary Language | short | 8 | 160.01 | 30 |
| `preferred_language` | Preferred Language | short | 8 | 170.51 | 33 |
| `current_first_name` | Current First Name Same as First Name at Birth | short | 8 | 289.06 | 62 |
| `current_last_name` | Current Last Name Same as Last Name at Birth | short | 8 | 289.06 | 62 |
| `education` | Highest Completed Education Level Not Currently Enrolled | short | 8 | 90.73 | 17 |
| `phone` | Text1a | short | 8 | 150 | 28 |
| `address` | Address Physical Mailing | short | 8 | 482.64 | 106 |

## Oar

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `client.full_name` | Client Name | short | 8 | 213.19 | 44 |
| `client.age` | Age | short | 8 | 45.43 | 8 |
| `client.dob` | DOB | short | 8 | 52.04 | 10 |
| `client.ethnicity` | Client Ethnicity | short | 7 | 202.87 | 49 |
| `insurance.medi_cal_cin` | MediCal | short | 8 | 204.3 | 42 |
| `client.living_with` | Liv ng Situation Homeless Alone ILF BC SNF Other w th whom | short | 8 | 201.09 | 41 |
| `clinical.primary_diagnosis` | Primary DSMICD Diagnosis with Specifier | short | 8 | 110.47 | 20 |
| `clinical.icd_code` | ICD Code | short | 8 | 191.22 | 39 |
| `clinical.other_diagnoses` | Other D agnoses Mental  Phys cal Health | narrative | 7.5 | 353.24 | 107 |
| `clinical.current_symptoms` | Current Symptoms List the frequency and durat on that result n impairment | narrative | 7.5 | 537.55 | 159 |
| `clinical.problem_list_date` | Problem List Rev ewedupdated No changes Date | short | 8 | 269.14 | 57 |
| `clinical.significant_impairment` | Explain Significant Impairment | narrative | 7.4 | 393.68 | 120 |
| `clinical.trauma_history` | History of Trauma andor Abuse Yes No If Yes explain | narrative | 7.4 | 469.46 | 141 |
| `clinical.substance_use` | Substance Use No History Current Drugs of choice | narrative | 7.5 | 255.18 | 77 |
| `clinical.substance_use_impact` | If current substance use describe impact on funct oning | narrative | 7.5 | 302.1 | 90 |
| `clinical.interventions` | List Interventions CBT DBT etc | narrative | 7.4 | 390.54 | 119 |
| `clinical.sessions_begin_date` | Begin Date of Sessions - Psychotherapy | short | 8 | 98 | 19 |
| `clinical.sessions_count` | Number of Sessions - Psychotherapy | short | 8 | 68 | 12 |
| `clinical.sessions_frequency` | Frequency - Psychotherapy | short | 8 | 173 | 35 |
| `provider.name_license` | NameLicensure | short | 8 | 457.72 | 100 |
| `provider.phone` | Phone | short | 8 | 317.92 | 74 |
| `provider.date` | Date | short | 8 | 145.26 | 26 |
| `clinical.justice_system_involvement_explain` | Justice System Involvement - If Yes explain | short | 7.5 | 288 | 70 |
| `clinical.interpreter_language` | Interpreter language | short | 7.5 | 274 | 55 |
| `clinical.group_participants` | Group Therapy Number of participants | short | 8 | 82 | 18 |
| `clinical.group_topic` | Group Topic | short | 8 | 214 | 45 |
| `clinical.group_sessions_begin_date` | Begin Date of Sessions - Group Psychotherapy | short | 8 | 98 | 19 |
| `clinical.group_sessions_count` | Number of Sessions - Group Psychotherapy | short | 8 | 68 | 12 |
| `clinical.group_sessions_frequency` | Frequency - Group Psychotherapy | short | 8 | 173 | 35 |
| `clinical.other_service_name` | Other Service | short | 8 | 145 | 30 |
| `clinical.other_sessions_begin_date` | Begin Date of Sessions - Other | short | 8 | 98 | 19 |
| `clinical.other_sessions_count` | Number of Sessions - Other | short | 8 | 68 | 12 |
| `clinical.other_sessions_frequency` | Frequency - Other | short | 8 | 173 | 35 |
| `clinical.team_conference_begin_date` | Begin Date of Sessions - Team Conference | short | 8 | 98 | 19 |
| `clinical.team_conference_units` | Number of Sessions - Team Conference | short | 8 | 68 | 12 |
| `clinical.team_conference_frequency` | Frequency - Team Conference | short | 8 | 173 | 35 |
| `clinical.tcm_begin_date` | Begin Date of Sessions - Targeted Case Management | short | 8 | 98 | 19 |
| `clinical.tcm_units` | Number of Sessions - Targeted Case Management | short | 8 | 68 | 12 |
| `clinical.tcm_frequency` | Frequency - Targeted Case Management | short | 8 | 173 | 35 |
| `clinical.tcm_medical_explain` | TCM Medical Explain | short | 8 | 448 | 95 |
| `clinical.tcm_social_explain` | TCM Social Explain | short | 8 | 454 | 98 |
| `clinical.tcm_educational_explain` | TCM Educational Explain | short | 8 | 433 | 93 |
| `clinical.tcm_other_explain` | TCM Other Services Explain | short | 8 | 419 | 89 |
| `provider.fax` | Fax | short | 8 | 149 | 33 |
| `provider.group_practice_name` | If Group Practice, Name of Group | short | 8 | 390 | 86 |

## Timeliness

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `client.full_name` | Clien Clientt Name | short | 8 | 170.28 | 33 |
| `insurance.medi_cal_cin` | MediCal | short | 8 | 111 | 20 |
| `client.dob` | DOB | short | 8 | 69 | 13 |
| `clinical.referral_source` | Dropdown1 | short | 8 | 303.89 | 68 |
| `clinical.first_contact_date` | Date3_af_date | short | 8 | 51.49 | 10 |
| `clinical.first_contact_time` | Time | short | 8 | 46.56 | 8 |
| `clinical.first_appointment_offered_date` | Date4_af_date | short | 8 | 51.82 | 10 |
| `clinical.first_appointment_offered_time` | Time_2 | short | 8 | 46.68 | 9 |
| `clinical.first_appointment_rendered_date` | Date5_af_date | short | 8 | 50.29 | 9 |
| `clinical.first_appointment_rendered_time` | Time_3 | short | 8 | 46.68 | 9 |
| `clinical.follow_up_offered_date` | Date6_af_date | short | 8 | 51.83 | 10 |
| `clinical.follow_up_offered_time` | Time_4 | short | 8 | 46.68 | 9 |
| `clinical.follow_up_rendered_date` | Date7_af_date | short | 8 | 50.67 | 9 |
| `clinical.follow_up_rendered_time` | Time_5 | short | 8 | 46.68 | 9 |
| `clinical.timeliness_comments` | Text13 | narrative | 8 | 501.47 | 140 |
| `provider.name_license` | Text10 | short | 8 | 286.74 | 61 |
| `provider.date` | Date1_af_date | short | 8 | 92.76 | 17 |
| `reserved.Text2` | Text2 | short | 8 | 258.22 | 55 |
| `reserved.Text3` | Text3 | narrative | 8 | 417.29 | 117 |
