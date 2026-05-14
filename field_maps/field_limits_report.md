# Legacy Field Length Limits

This report is retained for historical reference. The current source of truth is `field_fit_spec.json` / `field_fit_spec.md`.

Do not use these values as hard truncation limits. Current workflow requires measuring the actual candidate string against each field's writable width, then rewriting text shorter if needed.

Original calculated caps were based on measured PDF field widths using Helvetica and then reduced by 10% for character-width variability. Checkbox fields are excluded.

Narrative means prose-style content. It does not mean the underlying PDF field is multiline.

## Demographic

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `name_at_birth_first` | First Name at Birth | short | 8 | 159.36 | 32 |
| `name_at_birth_last` | Last Name at Birth | short | 8 | 175.09 | 35 |
| `mothers_first_name` | Mothers First Name | short | 8 | 430.44 | 89 |
| `place_of_birth_country` | Place of Birth  Country | short | 8 | 137.76 | 27 |
| `place_of_birth_state` | Place of Birth  State | short | 8 | 164.62 | 33 |
| `place_of_birth_county` | Place of Birth  County | short | 8 | 416.04 | 85 |
| `primary_language` | Primary Language | short | 8 | 160.01 | 32 |
| `preferred_language` | Preferred Language | short | 8 | 170.51 | 34 |
| `current_first_name` | Current First Name Same as First Name at Birth | short | 8 | 289.06 | 59 |
| `current_last_name` | Current Last Name Same as Last Name at Birth | short | 8 | 289.06 | 59 |
| `education` | Highest Completed Education Level Not Currently Enrolled | short | 8 | 90.73 | 18 |
| `phone` | Text1a | short | 8 | 150.0 | 29 |
| `address` | Address Physical Mailing | short | 8 | 482.64 | 99 |

## Oar

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `client.full_name` | Client Name | short | 8.0 | 213.19 | 43 |
| `client.age` | Age | short | 8.0 | 45.43 | 8 |
| `client.dob` | DOB | short | 8.0 | 52.04 | 10 |
| `client.ethnicity` | Client Ethnicity | short | 7.0 | 202.87 | 46 |
| `insurance.medi_cal_cin` | MediCal | short | 8.0 | 204.3 | 41 |
| `client.living_with` | Liv ng Situation Homeless Alone ILF BC SNF Other w th whom | short | 8.0 | 201.09 | 40 |
| `N/A` |  | short | 8.0 | 64 | 11 |
| `clinical.primary_diagnosis` | Primary DSMICD Diagnosis with Specifier | short | 8.0 | 110.47 | 21 |
| `clinical.icd_code` | ICD Code | short | 8.0 | 191.22 | 38 |
| `clinical.other_diagnoses` | Other D agnoses Mental  Phys cal Health | narrative | 7.5 | 353.24 | 77 |
| `clinical.current_symptoms` | Current Symptoms List the frequency and durat on that result n impairment | narrative | 7.5 | 537.55 | 118 |
| `clinical.problem_list_date` | Problem List Rev ewedupdated No changes Date | short | 8.0 | 269.14 | 54 |
| `clinical.significant_impairment` | Explain Significant Impairment | narrative | 7.4 | 393.68 | 87 |
| `clinical.trauma_history` | History of Trauma andor Abuse Yes No If Yes explain | narrative | 7.4 | 469.46 | 104 |
| `clinical.substance_use` | Substance Use No History Current Drugs of choice | narrative | 7.5 | 255.18 | 55 |
| `clinical.substance_use_impact` | If current substance use describe impact on funct oning | narrative | 7.5 | 302.1 | 65 |
| `clinical.interventions` | List Interventions CBT DBT etc | narrative | 7.4 | 390.54 | 87 |
| `clinical.sessions_begin_date` | Begin Date of SessionsPsychotherapy max 1 per day max 12 total | short | 8.0 | 102.24 | 19 |
| `clinical.sessions_count` | Number of SessionsPsychotherapy max 1 per day max 12 total | short | 8.0 | 72.36 | 13 |
| `clinical.sessions_frequency` | Frequency Number of Sessions per WeekMonthYearPsychotherapy max 1 per day max 12 total | short | 8.0 | 177.48 | 36 |
| `provider.name_license` | NameLicensure | short | 8.0 | 457.72 | 94 |
| `provider.phone` | Phone | short | 8.0 | 317.92 | 64 |
| `provider.date` | Date | short | 8.0 | 145.26 | 28 |

## Timeliness

| Data key | PDF field | Kind | Font size | Width | Max chars |
|---|---:|---:|---:|---:|---:|
| `client.full_name` | Clien Clientt Name | short | 8 | 170.28 | 34 |
| `insurance.medi_cal_cin` | MediCal | short | 8 | 111.0 | 21 |
| `client.dob` | DOB | short | 8 | 69.0 | 13 |
| `clinical.referral_source` | Dropdown1 | short | 8 | 303.89 | 62 |
| `clinical.first_contact_date` | Date3_af_date | short | 8 | 51.49 | 10 |
| `clinical.first_contact_time` | Time | short | 8 | 46.56 | 8 |
| `clinical.first_appointment_offered_date` | Date4_af_date | short | 8 | 51.82 | 10 |
| `clinical.first_appointment_offered_time` | Time_2 | short | 8 | 46.68 | 8 |
| `clinical.first_appointment_rendered_date` | Date5_af_date | short | 8 | 50.29 | 10 |
| `clinical.first_appointment_rendered_time` | Time_3 | short | 8 | 46.68 | 8 |
| `clinical.follow_up_offered_date` | Date6_af_date | short | 8 | 51.83 | 10 |
| `clinical.follow_up_offered_time` | Time_4 | short | 8 | 46.68 | 8 |
| `clinical.follow_up_rendered_date` | Date7_af_date | short | 8 | 50.67 | 10 |
| `clinical.follow_up_rendered_time` | Time_5 | short | 8 | 46.68 | 8 |
| `clinical.timeliness_comments` | Text13 | narrative | 8 | 501.47 | 103 |
| `provider.name_license` | Text10 | short | 8 | 286.74 | 58 |
| `provider.date` | Date1_af_date | short | 8 | 92.76 | 18 |
| `reserved.Text2` | Text2 | short | 8 | 258.22 | 53 |
| `reserved.Text3` | Text3 | narrative | 8 | 417.29 | 85 |
