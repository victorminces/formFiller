# ChatGPT Extraction Prompt For FormFiller

Use this prompt with ChatGPT when uploading patient images, screenshots, PDFs, exported data, or typed notes. The output is designed to be pasted into FormFiller using **Paste Extracted Text**.

```text
You are extracting patient information for three forms:
1. Demographic Form
2. Outpatient Authorization Request (OAR) Psychotherapy form
3. Psychotherapy Timeliness Record

Read all uploaded images/PDFs/screenshots/text carefully. Extract only information supported by the documents or by the user’s notes. If a value is uncertain, write "(uncertain)" after it. If a value is missing, leave it blank.

Important:
- Output plain labeled text only.
- Use exactly the labels below.
- One field per line.
- Do not output JSON.
- Do not add explanations.
- Condense OAR clinical fields so they fit in very small PDF fields.
- If required OAR clinical data is missing, add follow-up questions at the bottom under "Questions to ask:".

Text length limits:
- Primary diagnosis: max 30 characters if possible.
- Other diagnoses: max 65 characters.
- Current symptoms: max 90 characters.
- Significant impairment: max 90 characters.
- Trauma history: max 90 characters.
- Interventions: max 90 characters.
- Frequency: max 25 characters.

Use concise clinical wording. Examples:
- Primary diagnosis: MDD, recurrent, severe
- Current symptoms: Daily depression/grief; SI/desire; low motivation; impaired self-care/ADLs.
- Significant impairment: Impaired ADLs/social/medical/role function; poor self-care; deterioration likely.
- Trauma history: Mother died of cancer within past year; trauma/grief noted.
- Interventions: CBT/DBT-informed therapy; safety planning; grief/trauma support; care coordination.

Return these labels exactly:

Full name:
First name:
Last name:
First name at birth:
Last name at birth:
DOB:
Age:
Sex:
Gender identity:
Sexual orientation:
Ethnicity:
Race:
Primary language:
Preferred language:
Birth country:
Birth state:
Birth county/city:
Mother's first name:
Address:
Client phone:
Phone type:
Living situation:
Lives with:
Education:
Marital status:
Military status:
Veteran status:
Medi-Cal CIN:
Benefits ID:
Member number:
Plan name:
Effective date:
PCP name:
PCP address:
PCP phone:
Primary diagnosis:
ICD code:
Other diagnoses:
Current symptoms:
Problem list date:
Significant impairment:
Trauma history:
Substance use:
Substance use impact:
Suicidal no:
Suicidal ideation:
Suicidal plan:
Suicidal intent:
Suicidal history of harm:
Homicidal no:
Homicidal ideation:
Homicidal plan:
Homicidal intent:
Homicidal history of harm:
Interventions:
Interpreter needed:
Sessions begin date:
Number of sessions:
Frequency:
Referral source:
First contact date:
First contact time:
First appointment offered date:
First appointment offered time:
First appointment rendered date:
First appointment rendered time:
Follow-up offered date:
Follow-up offered time:
Follow-up rendered date:
Follow-up rendered time:
Urgent request:
Delayed access:
Delay reason:
Timeliness comments:
Provider name/license:
Provider phone:
Provider date:

Questions to ask:
```
