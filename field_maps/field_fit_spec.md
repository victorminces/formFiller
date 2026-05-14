# Field Fit Spec

Use this file for measured text fitting. Character counts below are examples based on sample strings; the controlling rule is to measure the actual candidate string against `max_width_points` before filling.

Never hard truncate. If text is too wide, rewrite it shorter and measure again.

## Demographic

| Data key | Kind | Font | Width pt | Lines | Example fit chars | Old max chars | Rule |
|---|---:|---:|---:|---:|---:|---:|---|
| `name_at_birth_first` | short | Helvetica 8 | 159.36 | 1 | 30 | 32 | measure actual string width |
| `name_at_birth_last` | short | Helvetica 8 | 175.09 | 1 | 34 | 35 | measure actual string width |
| `mothers_first_name` | short | Helvetica 8 | 430.44 | 1 | 95 | 89 | measure actual string width |
| `place_of_birth_country` | short | Helvetica 8 | 137.76 | 1 | 25 | 27 | measure actual string width |
| `place_of_birth_state` | short | Helvetica 8 | 164.62 | 1 | 31 | 33 | measure actual string width |
| `place_of_birth_county` | short | Helvetica 8 | 416.04 | 1 | 92 | 85 | measure actual string width |
| `primary_language` | short | Helvetica 8 | 160.01 | 1 | 30 | 32 | measure actual string width |
| `preferred_language` | short | Helvetica 8 | 170.51 | 1 | 33 | 34 | measure actual string width |
| `current_first_name` | short | Helvetica 8 | 289.06 | 1 | 62 | 59 | measure actual string width |
| `current_last_name` | short | Helvetica 8 | 289.06 | 1 | 62 | 59 | measure actual string width |
| `education` | short | Helvetica 8 | 90.73 | 1 | 17 | 18 | measure actual string width |
| `phone` | short | Helvetica 8 | 150.0 | 1 | 28 | 29 | measure actual string width |
| `address` | short | Helvetica 8 | 482.64 | 1 | 106 | 99 | measure actual string width |

## Oar

| Data key | Kind | Font | Width pt | Lines | Example fit chars | Old max chars | Rule |
|---|---:|---:|---:|---:|---:|---:|---|
| `client.full_name` | short | Helvetica-Bold 8 | 213.19 | 1 | 44 | 43 | measure actual string width |
| `client.age` | short | Helvetica 8 | 45.43 | 1 | 8 | 8 | measure actual string width |
| `client.dob` | short | Helvetica 8 | 52.04 | 1 | 10 | 10 | measure actual string width |
| `client.ethnicity` | short | Helvetica 7 | 202.87 | 1 | 49 | 46 | measure actual string width |
| `insurance.medi_cal_cin` | short | Helvetica 8 | 204.3 | 1 | 42 | 41 | measure actual string width |
| `client.living_with` | short | Helvetica 8 | 201.09 | 1 | 41 | 40 | measure actual string width |
| `N/A` | short | Helvetica 8 | 64.0 | 1 | 12 | 11 | measure actual string width |
| `clinical.primary_diagnosis` | short | Helvetica-Bold 8 | 110.47 | 1 | 20 | 21 | measure actual string width |
| `clinical.icd_code` | short | Helvetica-Bold 8 | 191.22 | 1 | 39 | 38 | measure actual string width |
| `clinical.other_diagnoses` | narrative | Helvetica 7.5 | 353.24 | 1 | 107 | 77 | measure actual string width |
| `clinical.current_symptoms` | narrative | Helvetica 7.5 | 537.55 | 1 | 159 | 118 | measure actual string width |
| `clinical.problem_list_date` | short | Helvetica 8 | 269.14 | 1 | 57 | 54 | measure actual string width |
| `clinical.significant_impairment` | narrative | Helvetica 7.4 | 393.68 | 1 | 120 | 87 | measure actual string width |
| `clinical.trauma_history` | narrative | Helvetica 7.4 | 469.46 | 1 | 141 | 104 | measure actual string width |
| `clinical.substance_use` | narrative | Helvetica 7.5 | 255.18 | 1 | 77 | 55 | measure actual string width |
| `clinical.substance_use_impact` | narrative | Helvetica 7.5 | 302.1 | 1 | 90 | 65 | measure actual string width |
| `clinical.interventions` | narrative | Helvetica 7.4 | 390.54 | 1 | 119 | 87 | measure actual string width |
| `clinical.sessions_begin_date` | short | Helvetica 8 | 102.24 | 1 | 19 | 19 | measure actual string width |
| `clinical.sessions_count` | short | Helvetica 8 | 72.36 | 1 | 13 | 13 | measure actual string width |
| `clinical.sessions_frequency` | short | Helvetica 8 | 177.48 | 1 | 36 | 36 | measure actual string width |
| `provider.name_license` | short | Helvetica 8 | 457.72 | 1 | 100 | 94 | measure actual string width |
| `provider.phone` | short | Helvetica 8 | 317.92 | 1 | 74 | 64 | measure actual string width |
| `provider.date` | short | Helvetica 8 | 145.26 | 1 | 26 | 28 | measure actual string width |

## Timeliness

| Data key | Kind | Font | Width pt | Lines | Example fit chars | Old max chars | Rule |
|---|---:|---:|---:|---:|---:|---:|---|
| `client.full_name` | short | Helvetica 8 | 170.28 | 1 | 33 | 34 | measure actual string width |
| `insurance.medi_cal_cin` | short | Helvetica 8 | 111.0 | 1 | 20 | 21 | measure actual string width |
| `client.dob` | short | Helvetica 8 | 69.0 | 1 | 13 | 13 | measure actual string width |
| `clinical.referral_source` | short | Helvetica 8 | 303.89 | 1 | 68 | 62 | measure actual string width |
| `clinical.first_contact_date` | short | Helvetica 8 | 51.49 | 1 | 10 | 10 | measure actual string width |
| `clinical.first_contact_time` | short | Helvetica 8 | 46.56 | 1 | 8 | 8 | measure actual string width |
| `clinical.first_appointment_offered_date` | short | Helvetica 8 | 51.82 | 1 | 10 | 10 | measure actual string width |
| `clinical.first_appointment_offered_time` | short | Helvetica 8 | 46.68 | 1 | 9 | 8 | measure actual string width |
| `clinical.first_appointment_rendered_date` | short | Helvetica 8 | 50.29 | 1 | 9 | 10 | measure actual string width |
| `clinical.first_appointment_rendered_time` | short | Helvetica 8 | 46.68 | 1 | 9 | 8 | measure actual string width |
| `clinical.follow_up_offered_date` | short | Helvetica 8 | 51.83 | 1 | 10 | 10 | measure actual string width |
| `clinical.follow_up_offered_time` | short | Helvetica 8 | 46.68 | 1 | 9 | 8 | measure actual string width |
| `clinical.follow_up_rendered_date` | short | Helvetica 8 | 50.67 | 1 | 9 | 10 | measure actual string width |
| `clinical.follow_up_rendered_time` | short | Helvetica 8 | 46.68 | 1 | 9 | 8 | measure actual string width |
| `clinical.timeliness_comments` | narrative | Helvetica 8 | 501.47 | 1 | 140 | 103 | measure actual string width |
| `provider.name_license` | short | Helvetica 8 | 286.74 | 1 | 61 | 58 | measure actual string width |
| `provider.date` | short | Helvetica 8 | 92.76 | 1 | 17 | 18 | measure actual string width |
| `reserved.Text2` | short | Helvetica 8 | 258.22 | 1 | 55 | 53 | measure actual string width |
| `reserved.Text3` | narrative | Helvetica 8 | 417.29 | 1 | 117 | 85 | measure actual string width |
