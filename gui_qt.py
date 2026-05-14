import json
import os
import re
import sys
import traceback
import ctypes
import subprocess
import shutil
import zipfile
from ctypes import wintypes
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDialog,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from reportlab.pdfbase.pdfmetrics import stringWidth

from fill_forms import fill_demographic, fill_oar_flattened, fill_timeliness


APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
LOG_PATH = Path.home() / "Documents" / "FormFillerOutputs" / "form_filler_error.log"
FIELD_FIT_SPEC_PATH = APP_DIR / "field_maps" / "field_fit_spec.json"
REQUIRED_FIELDS_PATH = APP_DIR / "field_maps" / "required_fields.json"

DEFAULT_REQUIRED_FIELDS = {
    "client.first_name": "Required: Client first name",
    "client.last_name": "Required: Client last name",
    "client.dob": "Required: DOB",
    "client.ethnicity_options": "Required: Client ethnicity",
    "insurance.medi_cal_cin": "Required: Medi-Cal number",
    "clinical.request_type": "Required on OAR: Request type",
    "clinical.primary_diagnosis": "Required on OAR: Primary DSM/ICD Diagnosis with Specifier",
    "clinical.current_symptoms": "Required on OAR: Current Symptoms",
    "clinical.problem_list_status": "Required on OAR: Problem List Status",
    "clinical.problem_list_date": "Required on OAR: Problem List Date",
    "clinical.significant_impairment": "Required on OAR: Explain Significant Impairment",
    "clinical.substance_use": "Required on OAR: Substance Use",
    "clinical.risk.suicidal": "Required on OAR: Suicidal Risk",
    "clinical.risk.homicidal": "Required on OAR: Homicidal Risk",
    "clinical.sessions_begin_date": "Required on OAR: Begin Date of Sessions",
    "clinical.sessions_count": "Required on OAR: Number of Sessions",
    "clinical.sessions_frequency": "Required on OAR: Frequency",
    "clinical.first_contact_date": "Required on Timeliness: Date of First Contact",
    "clinical.first_contact_time": "Required on Timeliness: Time of First Contact",
    "provider.name_license": "Required: Provider Name/Licensure",
    "provider.phone": "Required: Provider Phone",
    "provider.date": "Required: Provider/Form Date",
}

EXTENDED_TEXT_FIELDS = {
    "clinical.other_diagnoses",
    "clinical.current_symptoms",
    "clinical.significant_impairment",
    "clinical.trauma_history",
    "clinical.substance_use",
    "clinical.substance_use_impact",
    "clinical.interventions",
    "clinical.delay_reason",
    "clinical.timeliness_comments",
}

DATE_FIELDS = {
    "client.dob",
    "insurance.effective_date",
    "clinical.problem_list_date",
    "clinical.sessions_begin_date",
    "clinical.group_sessions_begin_date",
    "clinical.other_sessions_begin_date",
    "clinical.team_conference_begin_date",
    "clinical.tcm_begin_date",
    "clinical.first_contact_date",
    "clinical.first_appointment_offered_date",
    "clinical.first_appointment_rendered_date",
    "clinical.follow_up_offered_date",
    "clinical.follow_up_rendered_date",
    "clinical.access_closure_date",
    "provider.date",
}

TIME_FIELDS = {
    "clinical.first_contact_time",
    "clinical.first_appointment_offered_time",
    "clinical.first_appointment_rendered_time",
    "clinical.follow_up_offered_time",
    "clinical.follow_up_rendered_time",
}

TIME_CHOICES = [
    "8:00 am", "8:30 am", "9:00 am", "9:30 am", "10:00 am", "10:30 am",
    "11:00 am", "11:30 am", "12:00 pm", "12:30 pm", "1:00 pm", "1:30 pm",
    "2:00 pm", "2:30 pm", "3:00 pm", "3:30 pm", "4:00 pm", "4:30 pm",
    "5:00 pm", "5:30 pm",
]

CHECK_CHOICES = {
    "clinical.request_type": ["Initial Request", "Continuing Request"],
    "clinical.problem_list_status": ["Reviewed/updated", "No changes"],
    "client.hispanic_latino_status": ["Yes", "No", "Unknown/Not reported"],
}

NON_EDITABLE_CHOICE_FIELDS = {
    "clinical.primary_diagnosis",
    "clinical.employment_status",
    "clinical.sessions_count",
    "clinical.sessions_frequency",
    "clinical.referral_source",
    "clinical.delay_reason",
    "clinical.access_closure_reason",
    "client.sex",
    "client.gender_identity",
    "client.sexual_orientation",
    "client.hispanic_latino_status",
    "client.patient_status",
    "client.marital_status",
}

REQUIRED_STYLE = "color: #111; background-color: #fff1f0; border: 1px solid #d93025;"
BASE_INPUT_STYLE = "color: #111; background-color: #fff;"
COMBO_POPUP_STYLE = "QComboBox { color: #111; background-color: #fff; } QComboBox QAbstractItemView { color: #111; background-color: #fff; selection-color: #111; selection-background-color: #dbeafe; }"
CHECK_INDICATOR_STYLE = """
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #d0d0d0;
    background-color: #ffffff;
}
QCheckBox::indicator {
    border-radius: 4px;
}
QRadioButton::indicator {
    border-radius: 10px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #2f80ed;
    border: 2px solid #ffffff;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 2px solid #7db7ff;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    background-color: #6a6a6a;
    border: 2px solid #9a9a9a;
}
"""
CHOICE_GROUP_STYLE = f"QCheckBox, QRadioButton {{ color: #fff; background: transparent; border: none; padding: 2px; }} {CHECK_INDICATOR_STYLE}"
CHOICE_GROUP_REQUIRED_STYLE = f"QWidget {{ background-color: #fff1f0; border: 1px solid #d93025; }} QCheckBox, QRadioButton {{ color: #111; background: transparent; border: none; padding: 2px; }} {CHECK_INDICATOR_STYLE}"
CHECKGROUP_STYLE = f"QCheckBox {{ color: #fff; background: transparent; border: none; padding: 2px; }} {CHECK_INDICATOR_STYLE}"
CHECKGROUP_REQUIRED_STYLE = CHECKGROUP_STYLE
COUNTER_OK_STYLE = "color: #5f6368;"
COUNTER_BAD_STYLE = "color: #d93025; font-weight: 700;"
APP_STYLE = """
QMainWindow, QWidget {
    background-color: #1f1f1f;
    color: #f5f5f5;
}
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: #1f1f1f;
}
QLabel {
    color: #f5f5f5;
}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #777777;
    border-radius: 4px;
    padding: 4px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111111;
    selection-background-color: #dbeafe;
    selection-color: #111111;
}
QPushButton {
    background-color: #3a3a3a;
    color: #f5f5f5;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 10px;
}
QPushButton:hover {
    background-color: #4a4a4a;
}
QCheckBox, QRadioButton {
    color: #f5f5f5;
    background-color: transparent;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #d0d0d0;
    background-color: #ffffff;
}
QCheckBox::indicator {
    border-radius: 4px;
}
QRadioButton::indicator {
    border-radius: 10px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #2f80ed;
    border: 2px solid #ffffff;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 2px solid #7db7ff;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    background-color: #6a6a6a;
    border: 2px solid #9a9a9a;
}
QListWidget {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #777777;
}
QCalendarWidget QWidget {
    background-color: #ffffff;
    color: #111111;
}
"""

DIAGNOSIS_CHOICES = [
    "",
    # Common outpatient behavioral-health diagnoses first.
    "F43.10 - PTSD, unspecified",
    "F43.12 - PTSD, chronic",
    "F43.11 - PTSD, acute",
    "F41.1 - Generalized anxiety disorder",
    "F41.0 - Panic disorder",
    "F41.9 - Anxiety disorder, unspecified",
    "F33.0 - MDD, recurrent, mild",
    "F33.1 - MDD, recurrent, moderate",
    "F33.2 - MDD, recurrent, severe without psychotic features",
    "F33.3 - MDD, recurrent, severe with psychotic symptoms",
    "F32.0 - MDD, single episode, mild",
    "F32.1 - MDD, single episode, moderate",
    "F32.2 - MDD, single episode, severe without psychotic features",
    "F32.3 - MDD, single episode, severe with psychotic symptoms",
    "F43.23 - Adj d/o mixed anx/dep",
    "F43.21 - Adj d/o depressed mood",
    "F43.22 - Adj d/o anxiety",
    "F90.0 - ADHD, predominantly inattentive type",
    "F90.1 - ADHD, predominantly hyperactive/impulsive type",
    "F90.2 - ADHD, combined type",
    "F90.9 - ADHD, unspecified type",
    "F31.9 - Bipolar d/o, unspecified",
    "F31.32 - Bipolar d/o, current episode depressed, moderate",
    "F25.9 - Schizoaffective d/o, unspecified",
    "F29 - Psychosis, unspecified",

    # Depressive disorders.
    "F32.0 - MDD, single episode, mild",
    "F32.1 - MDD, single episode, moderate",
    "F32.2 - MDD, single episode, severe without psychotic features",
    "F32.3 - MDD, single episode, severe with psychotic symptoms",
    "F32.4 - MDD, single episode, in partial remission",
    "F32.5 - MDD, single episode, in full remission",
    "F32.9 - MDD, single episode, unspecified",
    "F33.0 - MDD, recurrent, mild",
    "F33.1 - MDD, recurrent, moderate",
    "F33.2 - MDD, recurrent, severe without psychotic features",
    "F33.3 - MDD, recurrent, severe with psychotic symptoms",
    "F33.40 - MDD, recurrent, in remission, unspecified",
    "F33.41 - MDD, recurrent, in partial remission",
    "F33.42 - MDD, recurrent, in full remission",
    "F33.9 - MDD, recurrent, unspecified",
    "F34.1 - Persistent depressive disorder (dysthymia)",
    "F32.A - Depression, unspecified",
    "F39 - Unspecified mood disorder",

    # Trauma, stressor-related, and adjustment disorders.
    "F43.0 - Acute stress reaction",
    "F43.10 - PTSD, unspecified",
    "F43.11 - PTSD, acute",
    "F43.12 - PTSD, chronic",
    "F43.20 - Adjustment disorder, unspecified",
    "F43.21 - Adjustment disorder with depressed mood",
    "F43.22 - Adjustment disorder with anxiety",
    "F43.23 - Adjustment disorder with mixed anxiety and depressed mood",
    "F43.24 - Adjustment disorder with disturbance of conduct",
    "F43.25 - Adjustment disorder with mixed disturbance of emotions and conduct",
    "F43.29 - Adjustment disorder with other symptoms",

    # Anxiety, OCD, and related disorders.
    "F40.00 - Agoraphobia, unspecified",
    "F40.01 - Agoraphobia with panic disorder",
    "F40.10 - Social phobia, unspecified",
    "F40.11 - Social phobia, generalized",
    "F40.218 - Other animal type phobia",
    "F40.228 - Other natural environment type phobia",
    "F40.231 - Fear of injections and transfusions",
    "F40.232 - Fear of other medical care",
    "F40.233 - Fear of injury",
    "F40.240 - Claustrophobia",
    "F40.248 - Other situational type phobia",
    "F40.298 - Other specified phobia",
    "F40.9 - Phobic anxiety disorder, unspecified",
    "F41.0 - Panic disorder",
    "F41.1 - Generalized anxiety disorder",
    "F41.3 - Other mixed anxiety disorders",
    "F41.8 - Other specified anxiety disorders",
    "F41.9 - Anxiety disorder, unspecified",
    "F42.2 - Mixed obsessional thoughts and acts",
    "F42.3 - Hoarding disorder",
    "F42.4 - Excoriation disorder",
    "F42.8 - Other obsessive-compulsive disorder",
    "F42.9 - Obsessive-compulsive disorder, unspecified",

    # Bipolar and related disorders.
    "F31.11 - Bipolar d/o, current episode manic without psychotic features, mild",
    "F31.12 - Bipolar d/o, current episode manic without psychotic features, moderate",
    "F31.13 - Bipolar d/o, current episode manic without psychotic features, severe",
    "F31.2 - Bipolar d/o, current episode manic severe with psychotic features",
    "F31.31 - Bipolar d/o, current episode depressed, mild",
    "F31.32 - Bipolar d/o, current episode depressed, moderate",
    "F31.4 - Bipolar d/o, current episode depressed, severe without psychotic features",
    "F31.5 - Bipolar d/o, current episode depressed, severe with psychotic features",
    "F31.61 - Bipolar d/o, current episode mixed, mild",
    "F31.62 - Bipolar d/o, current episode mixed, moderate",
    "F31.63 - Bipolar d/o, current episode mixed, severe without psychotic features",
    "F31.64 - Bipolar d/o, current episode mixed, severe with psychotic features",
    "F31.70 - Bipolar d/o, currently in remission, most recent episode unspecified",
    "F31.71 - Bipolar d/o, in partial remission, most recent episode hypomanic",
    "F31.72 - Bipolar d/o, in full remission, most recent episode hypomanic",
    "F31.73 - Bipolar d/o, in partial remission, most recent episode manic",
    "F31.74 - Bipolar d/o, in full remission, most recent episode manic",
    "F31.75 - Bipolar d/o, in partial remission, most recent episode depressed",
    "F31.76 - Bipolar d/o, in full remission, most recent episode depressed",
    "F31.77 - Bipolar d/o, in partial remission, most recent episode mixed",
    "F31.78 - Bipolar d/o, in full remission, most recent episode mixed",
    "F31.81 - Bipolar II disorder",
    "F31.89 - Other bipolar disorder",
    "F31.9 - Bipolar disorder, unspecified",

    # Psychotic disorders.
    "F20.0 - Paranoid schizophrenia",
    "F20.1 - Disorganized schizophrenia",
    "F20.2 - Catatonic schizophrenia",
    "F20.3 - Undifferentiated schizophrenia",
    "F20.5 - Residual schizophrenia",
    "F20.81 - Schizophreniform disorder",
    "F20.89 - Other schizophrenia",
    "F20.9 - Schizophrenia, unspecified",
    "F22 - Delusional disorders",
    "F23 - Brief psychotic disorder",
    "F25.0 - Schizoaffective disorder, bipolar type",
    "F25.1 - Schizoaffective disorder, depressive type",
    "F25.9 - Schizoaffective disorder, unspecified",
    "F28 - Other psychotic disorder not due to a substance or known physiological condition",
    "F29 - Unspecified psychosis not due to a substance or known physiological condition",

    # ADHD, neurodevelopmental, and developmental disorders.
    "F84.0 - Autistic disorder",
    "F84.5 - Asperger's syndrome",
    "F84.9 - Pervasive developmental disorder, unspecified",
    "F88 - Other disorders of psychological development",
    "F89 - Unspecified disorder of psychological development",
    "F90.0 - ADHD, predominantly inattentive type",
    "F90.1 - ADHD, predominantly hyperactive/impulsive type",
    "F90.2 - ADHD, combined type",
    "F90.8 - ADHD, other type",
    "F90.9 - ADHD, unspecified type",
    "F91.1 - Conduct disorder, childhood-onset type",
    "F91.2 - Conduct disorder, adolescent-onset type",
    "F91.3 - Oppositional defiant disorder",
    "F91.8 - Other conduct disorders",
    "F91.9 - Conduct disorder, unspecified",

    # Substance-related disorders, common uncomplicated codes.
    "F10.10 - Alcohol abuse, uncomplicated",
    "F10.20 - Alcohol dependence, uncomplicated",
    "F11.10 - Opioid abuse, uncomplicated",
    "F11.20 - Opioid dependence, uncomplicated",
    "F12.10 - Cannabis abuse, uncomplicated",
    "F12.20 - Cannabis dependence, uncomplicated",
    "F13.10 - Sedative, hypnotic, or anxiolytic abuse, uncomplicated",
    "F13.20 - Sedative, hypnotic, or anxiolytic dependence, uncomplicated",
    "F14.10 - Cocaine abuse, uncomplicated",
    "F14.20 - Cocaine dependence, uncomplicated",
    "F15.10 - Other stimulant abuse, uncomplicated",
    "F15.20 - Other stimulant dependence, uncomplicated",
    "F16.10 - Hallucinogen abuse, uncomplicated",
    "F16.20 - Hallucinogen dependence, uncomplicated",
    "F17.200 - Nicotine dependence, unspecified, uncomplicated",
    "F18.10 - Inhalant abuse, uncomplicated",
    "F18.20 - Inhalant dependence, uncomplicated",
    "F19.10 - Other psychoactive substance abuse, uncomplicated",
    "F19.20 - Other psychoactive substance dependence, uncomplicated",

    # Eating disorders.
    "F50.00 - Anorexia nervosa, unspecified",
    "F50.01 - Anorexia nervosa, restricting type",
    "F50.02 - Anorexia nervosa, binge eating/purging type",
    "F50.2 - Bulimia nervosa",
    "F50.81 - Binge eating disorder",
    "F50.82 - Avoidant/restrictive food intake disorder",
    "F50.89 - Other specified eating disorder",
    "F50.9 - Eating disorder, unspecified",

    # Somatic, dissociative, sleep, impulse-control, and personality disorders.
    "F44.81 - Dissociative identity disorder",
    "F44.9 - Dissociative disorder, unspecified",
    "F45.1 - Undifferentiated somatoform disorder",
    "F45.21 - Hypochondriasis",
    "F45.22 - Body dysmorphic disorder",
    "F45.8 - Other somatoform disorders",
    "F45.9 - Somatoform disorder, unspecified",
    "F51.01 - Primary insomnia",
    "F51.05 - Insomnia due to other mental disorder",
    "F51.09 - Other insomnia not due to a substance or known physiological condition",
    "F51.13 - Hypersomnia due to other mental disorder",
    "F60.3 - Borderline personality disorder",
    "F60.9 - Personality disorder, unspecified",
    "F63.81 - Intermittent explosive disorder",
    "F63.9 - Impulse disorder, unspecified",

    # Neurocognitive and other commonly encountered billable categories.
    "F01.A0 - Vascular dementia, mild, without behavioral disturbance",
    "F01.B0 - Vascular dementia, moderate, without behavioral disturbance",
    "F01.C0 - Vascular dementia, severe, without behavioral disturbance",
    "F03.A0 - Unspecified dementia, mild, without behavioral disturbance",
    "F03.B0 - Unspecified dementia, moderate, without behavioral disturbance",
    "F03.C0 - Unspecified dementia, severe, without behavioral disturbance",
    "F06.30 - Mood disorder due to known physiological condition, unspecified",
    "F06.31 - Mood disorder due to known physiological condition with depressive features",
    "F06.32 - Mood disorder due to known physiological condition with major depressive-like episode",
    "F06.4 - Anxiety disorder due to known physiological condition",
    "Other",
]


CHOICES = {
    "client.sex": ["", "Female", "Male", "Intersex", "Unknown", "Prefer not to answer"],
    "client.gender_identity": ["", "Female", "Male", "Non-Binary", "Transgender Female", "Transgender Male", "Genderqueer", "Questioning", "Prefer not to answer", "Unknown"],
    "client.sexual_orientation": ["", "Heterosexual / Straight", "Gay", "Lesbian", "Bisexual", "Questioning", "Prefer not to answer", "Unknown"],
    "client.ethnicity": ["", "Hispanic or Latino; Mexican/Mexican American", "Hispanic or Latino", "Not Hispanic or Latino", "Unknown/Not Reported"],
    "client.hispanic_latino_status": ["", "Yes", "No", "Unknown/Not reported"],
    "client.race": ["", "White/Caucasian", "Black/African American", "Asian Indian", "American Indian", "Multiracial", "Other", "Unknown", "Prefer not to answer"],
    "client.primary_language": ["", "English", "Spanish", "Arabic", "Tagalog", "Vietnamese", "Mandarin", "Cantonese", "Korean", "Other"],
    "client.preferred_language": ["", "English", "Spanish", "Arabic", "Tagalog", "Vietnamese", "Mandarin", "Cantonese", "Korean", "Other"],
    "client.living_situation": ["", "Homeless", "Alone", "ILF", "Board and Care", "SNF", "Other"],
    "client.education": ["", "Less than high school", "High school/GED", "Some college", "Associate degree", "Bachelor's degree", "Graduate degree", "Unknown"],
    "client.marital_status": ["", "Never Married", "Married", "Domestic Partnership", "Divorced", "Separated", "Widowed", "Unknown"],
    "client.patient_status": ["", "Discharged Home", "Discharged to a Facility", "Unknown/Not reported"],
    "clinical.primary_diagnosis": DIAGNOSIS_CHOICES,
    "clinical.employment_status": ["", "Employed", "Student", "Homemaker", "Retired", "Unemployed", "Seeking Work", "Not in Labor Force", "Unknown", "Other"],
    "clinical.regional_center_client": ["", "No", "Yes"],
    "clinical.impairment_social": ["", "Yes", "No"],
    "clinical.impairment_occupational": ["", "Yes", "No"],
    "clinical.impairment_activities": ["", "Yes", "No"],
    "clinical.impairment_deterioration": ["", "Yes", "No"],
    "clinical.impairment_developmental": ["", "Yes", "No"],
    "clinical.substance_use": ["", "No", "History", "Current"],
    "clinical.interpreter_needed": ["", "No", "Yes"],
    "clinical.sessions_count": ["", "1", "4", "6", "8", "10", "12"],
    "clinical.sessions_frequency": ["", "Once a week", "2x/week", "Every other week", "Monthly", "As needed"],
    "clinical.referral_source": ["", "Self", "Family Member", "School", "Fee-For-Service Provider", "Medi-Cal Managed Care Plan", "Emergency Room", "Mental Health Facility/Community Agency", "Social Services Agency", "Other Referral"],
    "clinical.first_contact_time": TIME_CHOICES,
    "clinical.first_appointment_offered_time": TIME_CHOICES,
    "clinical.first_appointment_rendered_time": TIME_CHOICES,
    "clinical.follow_up_offered_time": TIME_CHOICES,
    "clinical.follow_up_rendered_time": TIME_CHOICES,
    "clinical.urgent_request": ["", "No", "Yes"],
    "clinical.delayed_access": ["", "No", "Yes"],
    "clinical.follow_up_delayed_access": ["", "No", "Yes"],
    "clinical.extended_wait_clinically_appropriate": ["", "No", "Yes"],
    "clinical.delay_reason": ["", "Member did not accept offered dates", "Member accepted but did not attend", "No available provider", "Other"],
    "clinical.access_closure_reason": ["", "Member did not accept appointment dates", "Member did not attend initial appointment", "Member declined treatment", "Did not meet medical necessity", "Unable to contact", "Other"],
}

for _choice_key, _choice_values in list(CHOICES.items()):
    _visible_choices = [choice for choice in _choice_values if choice]
    if 0 < len(_visible_choices) <= 6:
        CHECK_CHOICES.setdefault(_choice_key, _visible_choices)

BUTTON_CHOICES = {
    "client.phone_type": ["Mobile", "Home", "Business"],
    "client.military_status": ["No", "Yes", "Unknown"],
    "client.veteran_status": ["No", "Yes", "Unknown"],
    "clinical.interpreter_needed": ["No", "Yes"],
    "clinical.urgent_request": ["No", "Yes"],
    "clinical.delayed_access": ["No", "Yes"],
}


def read_windows_clipboard_text():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    if not user32.OpenClipboard(None):
        return ""
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return ""
        try:
            return ctypes.wstring_at(pointer)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def read_powershell_clipboard_text():
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout or ""


def read_clipboard_text():
    qt_clipboard = QApplication.clipboard()
    text = qt_clipboard.text() or ""
    if text.strip():
        return text
    mime_data = qt_clipboard.mimeData()
    if mime_data and mime_data.hasHtml():
        return mime_data.html()
    text = read_windows_clipboard_text()
    if text.strip():
        return text
    return read_powershell_clipboard_text()


def load_example():
    data = json.loads((APP_DIR / "patient_input.example.json").read_text(encoding="utf-8"))
    output_dir = str(data.get("paths", {}).get("output_dir", ""))
    if not output_dir or "C:\\path\\to" in output_dir:
        data.setdefault("paths", {})["output_dir"] = str(Path.home() / "Documents" / "FormFillerOutputs")
    data.setdefault("attachments", {}).setdefault("source_files", [])
    clear_placeholders(data)
    data.setdefault("client", {})["primary_language"] = "English"
    data.setdefault("client", {})["preferred_language"] = "English"
    return data


def diagnosis_code_from_text(value):
    match = re.search(r"\bF\d{2}(?:\.\d{1,2}|[A-Z])?\b", str(value or ""), re.I)
    return match.group(0).upper() if match else ""


def diagnosis_label_without_code(value):
    return re.sub(r"^\s*F\d{2}(?:\.\d{1,2}|[A-Z])?\s*[-:]\s*", "", str(value or "")).strip()


def load_field_fit_spec():
    try:
        return json.loads(FIELD_FIT_SPEC_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_required_fields():
    try:
        payload = json.loads(REQUIRED_FIELDS_PATH.read_text(encoding="utf-8"))
        fields = payload.get("fields", payload)
        return {key: str(value.get("label", value)) if isinstance(value, dict) else str(value) for key, value in fields.items()}
    except Exception:
        return DEFAULT_REQUIRED_FIELDS.copy()


def field_fit_entry(fit_spec, dotted_key):
    simple_key = dotted_key.split(".")[-1]
    for form_name in ("oar", "demographic", "timeliness"):
        form = fit_spec.get(form_name, {})
        if dotted_key in form:
            return form[dotted_key]
        if simple_key in form:
            return form[simple_key]
    return None


def rendered_width_points(value, entry):
    if not entry:
        return 0.0
    font = entry.get("font") or fit_spec_font_default()
    font_size = float(entry.get("font_size") or 8)
    return stringWidth(" ".join(str(value or "").split()), font, font_size)


def fit_spec_font_default():
    return "Helvetica"


def is_blank_or_placeholder(value):
    text = str(value or "").strip()
    if not text:
        return True
    placeholder_patterns = [
        r"X{2,}",
        r"(?:X+\s*)+",
        r"X{2}/X{2}/X{4}",
        r"X{3}-X{3}-X{4}",
        r"0{2}/0{2}/0{4}",
    ]
    return any(re.fullmatch(pattern, text, re.I) for pattern in placeholder_patterns)


def clear_placeholders(value):
    if isinstance(value, dict):
        for key, item in list(value.items()):
            if isinstance(item, (dict, list)):
                clear_placeholders(item)
            elif isinstance(item, str) and is_blank_or_placeholder(item):
                value[key] = ""
    elif isinstance(value, list):
        for item in value:
            clear_placeholders(item)
    return value


def today_text():
    return datetime.now().strftime("%m/%d/%Y")


def default_date_text():
    return today_text()


def parse_date_value(value):
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def qdate_from_text(value):
    parsed = parse_date_value(value)
    if parsed:
        return QDate(parsed.year, parsed.month, parsed.day)
    return QDate.currentDate()


def qdate_to_text(date_value):
    return date_value.toString("MM/dd/yyyy")


class OptionalDateEdit(QDateEdit):
    blank_date = QDate(1900, 1, 1)

    def __init__(self, value="", parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setMinimumDate(self.blank_date)
        self.setMaximumDate(QDate(2100, 12, 31))
        self.set_from_text(value)

    def is_blank(self):
        return self.date() == self.blank_date

    def refresh_display_format(self):
        self.setDisplayFormat(" " if self.is_blank() else "MM/dd/yyyy")

    def set_from_text(self, value):
        parsed = parse_date_value(value)
        self.setDate(QDate(parsed.year, parsed.month, parsed.day) if parsed else self.blank_date)
        self.refresh_display_format()

    def text_value(self):
        return "" if self.is_blank() else qdate_to_text(self.date())

    def textFromDate(self, date_value):
        if date_value == self.blank_date:
            return ""
        return date_value.toString("MM/dd/yyyy")

    def mousePressEvent(self, event):
        if self.is_blank():
            self.setDisplayFormat("MM/dd/yyyy")
            self.setDate(QDate.currentDate())
        super().mousePressEvent(event)


def add_days_text(value, days):
    parsed = parse_date_value(value)
    if not parsed:
        return ""
    return (parsed + timedelta(days=days)).strftime("%m/%d/%Y")


def age_from_dob(value):
    parsed = parse_date_value(value)
    if not parsed:
        return ""
    today = datetime.now()
    age = today.year - parsed.year - ((today.month, today.day) < (parsed.month, parsed.day))
    return str(age) if age >= 0 else ""


def apply_workflow_defaults(data):
    clinical = data.setdefault("clinical", {})
    provider = data.setdefault("provider", {})
    client = data.setdefault("client", {})
    if is_blank_or_placeholder(provider.get("date", "")):
        provider["date"] = today_text()
    first = str(client.get("first_name", "") or "").strip()
    last = str(client.get("last_name", "") or "").strip()
    if first or last:
        client["full_name"] = " ".join(part for part in (first, last) if part)
    if is_blank_or_placeholder(client.get("name_at_birth_first", "")) and first:
        client["name_at_birth_first"] = first
    if is_blank_or_placeholder(client.get("name_at_birth_last", "")) and last:
        client["name_at_birth_last"] = last
    if "same_first_name" not in client:
        client["same_first_name"] = True
    if "same_last_name" not in client:
        client["same_last_name"] = True
    if not client.get("special_population_services"):
        client["special_population_services"] = ["No"]
    if not client.get("court_status"):
        client["court_status"] = ["Unknown/Not Reported"]
    if is_blank_or_placeholder(client.get("gender_identity", "")):
        client["gender_identity"] = "Female"
    if is_blank_or_placeholder(client.get("military_status", "")):
        client["military_status"] = "No"
    if is_blank_or_placeholder(client.get("veteran_status", "")):
        client["veteran_status"] = "No"
    if is_blank_or_placeholder(client.get("primary_language", "")):
        client["primary_language"] = "English"
    if is_blank_or_placeholder(client.get("preferred_language", "")):
        client["preferred_language"] = "English"
    if not client.get("race_options") and not is_blank_or_placeholder(client.get("race", "")):
        client["race_options"] = values_matching_options(client.get("race", ""), CHECKBOX_GROUPS["client.race_options"])
    if client.get("ethnicity_options"):
        client["ethnicity"] = "; ".join(str(item) for item in client.get("ethnicity_options", []))
    if not client.get("special_population_services"):
        client["special_population_services"] = ["No"]
    if is_blank_or_placeholder(client.get("age", "")):
        client["age"] = age_from_dob(client.get("dob", ""))
    if is_blank_or_placeholder(clinical.get("problem_list_date", "")):
        clinical["problem_list_date"] = provider["date"]
    if is_blank_or_placeholder(clinical.get("problem_list_status", "")):
        clinical["problem_list_status"] = "Reviewed/updated"
    if is_blank_or_placeholder(clinical.get("request_type", "")):
        clinical["request_type"] = "Initial Request"
    if is_blank_or_placeholder(clinical.get("employment_status", "")):
        clinical["employment_status"] = "Unknown"
    if is_blank_or_placeholder(clinical.get("substance_use", "")):
        clinical["substance_use"] = "No"
    for key in (
        "first_contact_time",
        "first_appointment_offered_time",
        "first_appointment_rendered_time",
        "follow_up_offered_time",
        "follow_up_rendered_time",
    ):
        if is_blank_or_placeholder(clinical.get(key, "")):
            clinical[key] = "11:00 am"
    offered = clinical.get("first_appointment_offered_date", "")
    if offered and is_blank_or_placeholder(clinical.get("first_appointment_rendered_date", "")):
        clinical["first_appointment_rendered_date"] = offered
    if offered and is_blank_or_placeholder(clinical.get("follow_up_offered_date", "")):
        clinical["follow_up_offered_date"] = add_days_text(offered, 7)
    rendered = clinical.get("first_appointment_rendered_date", "") or offered
    if rendered and is_blank_or_placeholder(clinical.get("follow_up_rendered_date", "")):
        clinical["follow_up_rendered_date"] = add_days_text(rendered, 7)
    for key in ("urgent_request", "delayed_access", "follow_up_delayed_access", "extended_wait_clinically_appropriate"):
        if is_blank_or_placeholder(clinical.get(key, "")):
            clinical[key] = "No"
    if is_blank_or_placeholder(clinical.get("sessions_count", "")):
        clinical["sessions_count"] = "12"
    if is_blank_or_placeholder(clinical.get("sessions_frequency", "")):
        clinical["sessions_frequency"] = "Once a week"
    if is_blank_or_placeholder(clinical.get("sessions_begin_date", "")):
        clinical["sessions_begin_date"] = today_text()
    if is_blank_or_placeholder(clinical.get("interventions", "")):
        clinical["interventions"] = "ACT"
    if is_blank_or_placeholder(clinical.get("referral_source", "")):
        clinical["referral_source"] = "Self"
    clinical.setdefault("risk", {})
    if not clinical["risk"].get("suicidal"):
        clinical["risk"]["suicidal"] = ["No"]
    if not clinical["risk"].get("homicidal"):
        clinical["risk"]["homicidal"] = ["No"]
    clinical.setdefault("suicidal", {"no": True, "ideation": False, "plan": False, "intent": False, "history_of_harm": False})
    clinical.setdefault("homicidal", {"no": True, "ideation": False, "plan": False, "intent": False, "history_of_harm": False})
    if "no" not in {str(x).lower() for x in clinical["risk"].get("suicidal", [])} and not any(clinical["suicidal"].values()):
        clinical["risk"]["suicidal"] = ["No"]
    if "no" not in {str(x).lower() for x in clinical["risk"].get("homicidal", [])} and not any(clinical["homicidal"].values()):
        clinical["risk"]["homicidal"] = ["No"]
    has_medications = any(str(clinical.get(key, "")).strip() for key in (
        "medication_1_name",
        "medication_2_name",
        "medication_3_name",
        "medications",
    ))
    if has_medications:
        clinical["no_medications"] = False
    else:
        clinical.setdefault("no_medications", True)


def risk_list_to_flags(values, self_harm_label, other_label):
    selected = {str(item).lower() for item in (values or [])}
    return {
        "no": "no" in selected,
        "ideation": "ideation" in selected,
        "plan": "plan" in selected,
        "intent": "intent" in selected,
        "history_of_harm": self_harm_label.lower() in selected or other_label.lower() in selected,
    }


def normalize_app_data(data):
    clinical = data.setdefault("clinical", {})
    risk = clinical.get("risk", {})
    if isinstance(risk, dict):
        if "suicidal" in risk:
            clinical["suicidal"] = risk_list_to_flags(risk.get("suicidal"), "History of harming self", "History of harm")
        if "homicidal" in risk:
            clinical["homicidal"] = risk_list_to_flags(risk.get("homicidal"), "History of harming others", "History of harm")
    if clinical.get("interpreter_needed_yes"):
        clinical["interpreter_needed"] = "Yes"
    elif "interpreter_needed_yes" in clinical:
        clinical["interpreter_needed"] = "No"
    if clinical.get("delayed_access_yes"):
        clinical["delayed_access"] = "Yes"
    if clinical.get("no_medications"):
        clinical["medications"] = "No Medications"
    if clinical.get("cfwb_referral_yes"):
        data["cfwb_referral"] = "Yes"
    elif "cfwb_referral_yes" in clinical:
        data["cfwb_referral"] = "No"
    if clinical.get("regional_center_client"):
        data["regional_center_client"] = clinical.get("regional_center_client")
    if clinical.get("justice_system_involvement_yes"):
        data["justice_system_involvement"] = "Yes"
    elif "justice_system_involvement_yes" in clinical:
        data["justice_system_involvement"] = "N/A"
    client = data.setdefault("client", {})
    race_options = client.get("race_options") or []
    if race_options:
        client["race"] = "; ".join(str(item) for item in race_options)
    if client.get("ethnicity_options"):
        client["ethnicity"] = "; ".join(str(item) for item in client.get("ethnicity_options", []))


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
    return "" if current is None else current


CHECKBOX_GROUPS = {
    "client.suffix_at_birth": ["JR", "SR", "II", "III", "IV", "V", "VI"],
    "client.ethnicity_options": [
        "Amerasian", "American Native", "Asian Indian", "Black", "Cambodian", "Chinese", "Dominican",
        "Filipino", "Guamanian", "Hawaiian Native", "Hispanic or Latino", "Japanese", "Korean", "Laotian",
        "Mexican/Mexican American", "Middle Eastern or North African", "Multiple", "Not Hispanic or Latino",
        "Other", "Other Asian", "Other Pacific Islander", "Samoan", "Unknown/Not Reported", "Vietnamese",
        "White/Caucasian",
    ],
    "client.race_options": [
        "Alaskan Native", "American Indian", "Asian Indian", "Black/African American", "Cambodian", "Chinese",
        "Filipino", "Guamanian", "Hawaiian", "Hmong", "Japanese", "Korean", "Laotian", "Mien",
        "Middle Eastern or North African", "Multiracial", "Native Hawaiian", "Not Asked", "Other",
        "Other Asian", "Other Pacific Islander", "Prefer not to answer", "Samoan", "Unknown", "Vietnamese",
        "White/Caucasian",
    ],
    "client.special_population_services": [
        "No", "Assisted Outpatient Treatment", "IEP required services", "Governor's Homeless Initiative",
        "Welfare-to-Work",
    ],
    "client.court_status": [
        "Temporary Conservatorship", "Lanterman-Petris-Short", "Murphy", "Probate", "PC 2974",
        "Representative Payee Without Conservatorship", "Juvenile Court Dependent", "Juvenile Ward Status Offender",
        "Juvenile Ward Juvenile Offender", "Not Applicable", "Unknown/Not Reported",
    ],
    "clinical.risk.suicidal": ["No", "Ideation", "Plan", "Intent", "History of harming self"],
    "clinical.risk.homicidal": ["No", "Ideation", "Plan", "Intent", "History of harming others"],
    "clinical.tcm_focus": ["Medical", "Social", "Educational", "Other Services"],
}

YES_TEXT_FIELDS = {
    "client.discharge": ("client.discharge_acute", "client.discharge_facility", "Acute 24-hour discharge / facility"),
    "clinical.justice": ("clinical.justice_system_involvement_yes", "clinical.justice_system_involvement_explain", "Justice system involvement"),
    "clinical.cfwb": ("clinical.cfwb_referral_yes", "clinical.cfwb_psw", "CFWB referral / PSW name and number"),
    "clinical.cws_history": ("clinical.cws_history_yes", "clinical.cws_history", "History of CWS/CFWB, when and why"),
    "clinical.trauma": ("clinical.trauma_yes", "clinical.trauma_history", "Trauma/abuse history explanation"),
    "clinical.group_therapy": ("clinical.group_therapy", "clinical.group_therapy_details", "Group therapy participants/topic"),
    "clinical.interpreter": ("clinical.interpreter_needed_yes", "clinical.interpreter_language", "Interpreter language"),
    "clinical.tcm_medical": ("clinical.tcm_medical", "clinical.tcm_medical_explain", "TCM medical explanation"),
    "clinical.tcm_social": ("clinical.tcm_social", "clinical.tcm_social_explain", "TCM social explanation"),
    "clinical.tcm_educational": ("clinical.tcm_educational", "clinical.tcm_educational_explain", "TCM educational explanation"),
    "clinical.tcm_other": ("clinical.tcm_other", "clinical.tcm_other_explain", "TCM other-services explanation"),
    "clinical.timeliness_delay": ("clinical.delayed_access_yes", "clinical.delay_reason_other", "Delay reason if other"),
    "clinical.out_of_network": ("clinical.out_of_network_referral", "clinical.out_of_network_comments", "Out-of-network comments"),
    "clinical.access_closure": ("clinical.access_closed", "clinical.closure_explain", "Access closure explanation if other"),
}

FIELDS = [
    ("Output", [
        ("paths.signature_image", "OAR signature image", "file"),
        ("paths.output_dir", "Output folder", "folder"),
    ]),
    ("Demographic - Client Identity", [
        ("client.first_name", "Current first name", "text"),
        ("client.last_name", "Current last name", "text"),
        ("client.middle_name", "Current middle name", "text"),
        ("client.name_at_birth_first", "First name at birth", "text"),
        ("client.name_at_birth_middle", "Middle name at birth", "text"),
        ("client.name_at_birth_last", "Last name at birth", "text"),
        ("client.same_first_name", "Current first name same as birth first name", "bool"),
        ("client.same_last_name", "Current last name same as birth last name", "bool"),
        ("client.suffix_at_birth", "Suffix at birth", "checkgroup"),
        ("client.dob", "DOB", "date"),
        ("client.age", "Age", "text"),
        ("client.mothers_first_name", "Mother's first name", "text"),
        ("client.social_security_number", "Social Security number", "text"),
        ("client.aliases", "Aliases", "text"),
    ]),
    ("Demographic - Background", [
        ("client.place_of_birth_country", "Birth country", "text"),
        ("client.place_of_birth_state", "Birth state", "text"),
        ("client.place_of_birth_county", "Birth county/city", "text"),
        ("client.primary_language", "Primary language", "text"),
        ("client.preferred_language", "Preferred language", "text"),
        ("client.ethnicity_options", "Ethnicity checkboxes", "checkgroup"),
        ("client.hispanic_latino_status", "Hispanic/Latino ethnicity", "check_choice"),
        ("client.race_options", "Race checkboxes", "checkgroup"),
        ("client.education", "Highest completed education", "text"),
        ("client.not_currently_enrolled", "Not currently enrolled", "bool"),
    ]),
    ("Demographic - Status and Contact", [
        ("client.special_population_services", "Special population services", "checkgroup"),
        ("client.discharge", "If discharged from acute 24-hour service", "yes_text"),
        ("client.patient_status", "Patient status", "text"),
        ("client.legal_class_admission", "Legal class at admission", "text"),
        ("client.court_status", "Conservatorship/court status", "checkgroup"),
        ("client.responsible_under_18_count", "# persons under 18 responsible for", "text"),
        ("client.responsible_over_17_count", "# persons over 17 responsible for", "text"),
        ("client.phone", "Primary phone", "text"),
        ("client.phone_type", "Phone type", "text"),
        ("client.do_not_call", "Do not call", "bool"),
        ("client.do_not_leave_message", "Do not leave message", "bool"),
        ("client.address", "Address", "text"),
        ("client.address_physical", "Physical address", "bool"),
        ("client.address_mailing", "Mailing address", "bool"),
        ("client.marital_status", "Marital status", "text"),
        ("client.sex", "Sex", "text"),
        ("client.gender_identity", "Gender identity", "text"),
        ("client.sexual_orientation", "Sexual orientation", "text"),
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
    ("OAR - Client and Referral", [
        ("clinical.request_type", "Request type", "check_choice"),
        ("client.living_situation", "Living situation", "text"),
        ("client.living_with", "If other living situation, with whom", "text"),
        ("clinical.regional_center_client", "Regional Center client", "text"),
        ("clinical.employment_status", "Employment/school status", "text"),
        ("clinical.justice", "If justice involvement yes", "yes_text"),
        ("clinical.cfwb", "If CFWB referral yes", "yes_text"),
        ("clinical.cws_history", "If CWS/CFWB history yes", "yes_text"),
    ]),
    ("OAR - Diagnosis and Clinical", [
        ("clinical.primary_diagnosis", "Primary diagnosis / ICD code", "text"),
        ("clinical.other_diagnoses", "Other diagnoses", "text"),
        ("clinical.current_symptoms", "Current symptoms", "text"),
        ("clinical.problem_list_status", "Problem list status", "check_choice"),
        ("clinical.problem_list_date", "Problem list date", "date"),
        ("clinical.impairment_social", "Social/relational impairment: yes", "bool"),
        ("clinical.impairment_occupational", "Occupational/academic impairment: yes", "bool"),
        ("clinical.impairment_activities", "Other activities impairment: yes", "bool"),
        ("clinical.impairment_deterioration", "Probability of deterioration: yes", "bool"),
        ("clinical.impairment_developmental", "Under-21 developmental progress: yes", "bool"),
        ("clinical.significant_impairment", "Explain significant impairment", "text"),
        ("clinical.trauma", "If trauma/abuse yes", "yes_text"),
        ("clinical.substance_use", "Substance use", "text"),
        ("clinical.drugs_of_choice", "Drug(s) of choice", "text"),
        ("clinical.substance_use_impact", "If current substance use, impact", "text"),
    ]),
    ("OAR - Risk and Medications", [
        ("clinical.risk.suicidal", "Suicidal risk", "checkgroup"),
        ("clinical.risk.homicidal", "Homicidal risk", "checkgroup"),
        ("clinical.no_medications", "No medications", "bool"),
        ("clinical.medication_1_name", "Medication 1 name", "text"),
        ("clinical.medication_1_dosage", "Medication 1 dosage", "text"),
        ("clinical.medication_2_name", "Medication 2 name", "text"),
        ("clinical.medication_2_dosage", "Medication 2 dosage", "text"),
        ("clinical.medication_3_name", "Medication 3 name", "text"),
        ("clinical.medication_3_dosage", "Medication 3 dosage", "text"),
    ]),
    ("OAR - Services", [
        ("clinical.interventions", "Interventions", "text"),
        ("clinical.interpreter", "If interpreter yes", "yes_text"),
        ("clinical.sessions_count", "Psychotherapy number of sessions", "text"),
        ("clinical.sessions_frequency", "Psychotherapy frequency", "text"),
    ]),
    ("Timeliness", [
        ("clinical.referral_source", "Referral source", "text"),
        ("clinical.first_contact_date", "First contact date", "date"),
        ("clinical.first_contact_time", "First contact time", "text"),
        ("clinical.urgent_request", "Urgent request", "text"),
        ("clinical.first_appointment_offered_date", "First appointment offered date", "date"),
        ("clinical.first_appointment_offered_time", "First appointment offered time", "text"),
        ("clinical.first_appointment_rendered_date", "First appointment rendered date", "date"),
        ("clinical.first_appointment_rendered_time", "First appointment rendered time", "text"),
        ("clinical.sessions_begin_date", "First psychotherapy/session date", "date"),
        ("clinical.delayed_access", "Delayed access beyond 10 days", "text"),
        ("clinical.delay_reason", "Reason for delay", "text"),
        ("clinical.timeliness_delay", "If delay reason other", "yes_text"),
        ("clinical.follow_up_offered_date", "Follow-up offered date", "date"),
        ("clinical.follow_up_offered_time", "Follow-up offered time", "text"),
        ("clinical.follow_up_rendered_date", "Follow-up rendered date", "date"),
        ("clinical.follow_up_rendered_time", "Follow-up rendered time", "text"),
        ("clinical.follow_up_delayed_access", "Follow-up delayed beyond 10 days", "text"),
        ("clinical.extended_wait_clinically_appropriate", "Extended wait clinically appropriate", "text"),
        ("clinical.timeliness_comments", "Timeliness comments", "text"),
        ("clinical.out_of_network", "If out-of-network referral yes", "yes_text"),
        ("clinical.access_closure_date", "Access closure date", "date"),
        ("clinical.access_closure_reason", "Access closure reason", "text"),
        ("clinical.access_closure", "If access closure other", "yes_text"),
    ]),
    ("Provider", [
        ("provider.name_license", "Provider name/license", "text"),
        ("provider.phone", "Provider phone", "text"),
        ("provider.fax", "Provider fax", "text"),
        ("provider.date", "Provider/form date", "date"),
        ("provider.group_practice_name", "Group practice name", "text"),
        ("provider.waive_verbal_notification", "Waive verbal notification", "bool"),
    ]),
]


EXTRACTION_PROMPT = """You are extracting patient information for three forms:
1. Demographic Form
2. Outpatient Authorization Request (OAR) Psychotherapy form
3. Psychotherapy Timeliness Record

Read all uploaded images/PDFs/screenshots/text carefully. Extract only information supported by the documents or by the user's notes. If a value is uncertain, write "(uncertain)" after it. If a value is missing, leave it blank.

Important:
- Output plain labeled text only.
- Use exactly the labels below.
- One field per line.
- Do not output JSON.
- Do not add explanations.
- Condense OAR clinical fields so they fit in very small PDF fields.
- If required OAR clinical data is missing, add follow-up questions at the bottom under "Questions to ask:".

Text length limits:
- Primary diagnosis: choose a concise diagnosis label with ICD code, e.g. F43.10 - PTSD, unspecified.
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
Primary diagnosis / ICD code:
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

Questions to ask:"""


LABEL_TO_FIELD = {
    "full name": "client.full_name",
    "legal name": "client.full_name",
    "client name": "client.full_name",
    "first name": "client.first_name",
    "last name": "client.last_name",
    "first name at birth": "client.name_at_birth_first",
    "last name at birth": "client.name_at_birth_last",
    "dob": "client.dob",
    "date of birth": "client.dob",
    "age": "client.age",
    "sex": "client.sex",
    "gender": "client.gender_identity",
    "gender identity": "client.gender_identity",
    "sexual orientation": "client.sexual_orientation",
    "ethnicity": "client.ethnicity",
    "race": "client.race_options",
    "primary language": "client.primary_language",
    "preferred language": "client.preferred_language",
    "birth country": "client.place_of_birth_country",
    "place of birth country": "client.place_of_birth_country",
    "birth state": "client.place_of_birth_state",
    "place of birth state": "client.place_of_birth_state",
    "birth county": "client.place_of_birth_county",
    "birth county/city": "client.place_of_birth_county",
    "birth city": "client.place_of_birth_county",
    "place of birth": "client.place_of_birth_county",
    "mother's first name": "client.mothers_first_name",
    "mothers first name": "client.mothers_first_name",
    "mother": "client.mothers_first_name",
    "address": "client.address",
    "client phone": "client.phone",
    "phone": "client.phone",
    "phone type": "client.phone_type",
    "phone type": "client.phone_type",
    "living situation": "client.living_situation",
    "lives with": "client.living_with",
    "education": "client.education",
    "marital status": "client.marital_status",
    "military status": "client.military_status",
    "veteran status": "client.veteran_status",
    "medi-cal cin": "insurance.medi_cal_cin",
    "medi-cal": "insurance.medi_cal_cin",
    "medical cin": "insurance.medi_cal_cin",
    "benefits id": "insurance.benefits_id",
    "benefits id no": "insurance.benefits_id",
    "member number": "insurance.member_number",
    "member no": "insurance.member_number",
    "plan name": "insurance.plan_name",
    "effective date": "insurance.effective_date",
    "pcp name": "insurance.pcp_name",
    "primary care physician": "insurance.pcp_name",
    "pcp address": "insurance.pcp_address",
    "pcp phone": "insurance.pcp_phone",
    "primary diagnosis / icd code": "clinical.primary_diagnosis",
    "primary diagnosis and icd code": "clinical.primary_diagnosis",
    "primary diagnosis": "clinical.primary_diagnosis",
    "diagnosis": "clinical.primary_diagnosis",
    "icd code": "clinical.icd_code",
    "other diagnoses": "clinical.other_diagnoses",
    "current symptoms": "clinical.current_symptoms",
    "symptoms": "clinical.current_symptoms",
    "problem list date": "clinical.problem_list_date",
    "significant impairment": "clinical.significant_impairment",
    "impairment": "clinical.significant_impairment",
    "trauma history": "clinical.trauma_history",
    "trauma": "clinical.trauma_history",
    "substance use": "clinical.substance_use",
    "substance use impact": "clinical.substance_use_impact",
    "interventions": "clinical.interventions",
    "interpreter needed": "clinical.interpreter_needed",
    "sessions begin date": "clinical.sessions_begin_date",
    "begin date": "clinical.sessions_begin_date",
    "number of sessions": "clinical.sessions_count",
    "sessions": "clinical.sessions_count",
    "frequency": "clinical.sessions_frequency",
    "referral source": "clinical.referral_source",
    "first contact date": "clinical.first_contact_date",
    "first contact time": "clinical.first_contact_time",
    "first appointment offered date": "clinical.first_appointment_offered_date",
    "first appointment offered time": "clinical.first_appointment_offered_time",
    "first appointment rendered date": "clinical.first_appointment_rendered_date",
    "first appointment rendered time": "clinical.first_appointment_rendered_time",
    "follow-up offered date": "clinical.follow_up_offered_date",
    "follow up offered date": "clinical.follow_up_offered_date",
    "follow-up offered time": "clinical.follow_up_offered_time",
    "follow up offered time": "clinical.follow_up_offered_time",
    "follow-up rendered date": "clinical.follow_up_rendered_date",
    "follow up rendered date": "clinical.follow_up_rendered_date",
    "follow-up rendered time": "clinical.follow_up_rendered_time",
    "follow up rendered time": "clinical.follow_up_rendered_time",
    "urgent request": "clinical.urgent_request",
    "delayed access": "clinical.delayed_access",
    "delay reason": "clinical.delay_reason",
    "timeliness comments": "clinical.timeliness_comments",
    "provider name/license": "provider.name_license",
    "provider": "provider.name_license",
    "provider phone": "provider.phone",
    "provider date": "provider.date",
}


BOOL_LABELS = {
    "suicidal no": "clinical.suicidal.no",
    "suicidal ideation": "clinical.suicidal.ideation",
    "suicidal plan": "clinical.suicidal.plan",
    "suicidal intent": "clinical.suicidal.intent",
    "suicidal history of harm": "clinical.suicidal.history_of_harm",
    "homicidal no": "clinical.homicidal.no",
    "homicidal ideation": "clinical.homicidal.ideation",
    "homicidal plan": "clinical.homicidal.plan",
    "homicidal intent": "clinical.homicidal.intent",
    "homicidal history of harm": "clinical.homicidal.history_of_harm",
}


def normalize_label(label):
    label = label.strip().lower()
    label = re.sub(r"^[*#\-•\s]+", "", label)
    label = label.replace("_", " ")
    label = re.sub(r"\s+", " ", label)
    return label.strip(" :")


def parse_bool(value):
    value = value.strip().lower()
    return value in {"yes", "y", "true", "checked", "present", "1", "x", "on"}


def parse_extracted_text(raw_text):
    updates = {}
    for line in raw_text.splitlines():
        line = line.strip().strip("-• ")
        if not line or ":" not in line:
            continue
        label, value = line.split(":", 1)
        label = normalize_label(label)
        value = value.strip()
        if not value:
            continue
        if label in BOOL_LABELS:
            updates[BOOL_LABELS[label]] = parse_bool(value)
        elif label in LABEL_TO_FIELD:
            updates[LABEL_TO_FIELD[label]] = value

    # Lightweight fallback for unstructured text.
    if "client.dob" not in updates:
        match = re.search(r"\b(?:DOB|date of birth|born)\D{0,20}(\d{1,2}/\d{1,2}/\d{2,4})\b", raw_text, re.I)
        if match:
            updates["client.dob"] = match.group(1)
    if "insurance.medi_cal_cin" not in updates:
        match = re.search(r"\b(?:Medi-?Cal\s*(?:CIN)?|CIN)\D{0,12}([A-Z0-9]{8,15})\b", raw_text, re.I)
        if match:
            updates["insurance.medi_cal_cin"] = match.group(1)
    if "client.phone" not in updates:
        match = re.search(r"\b(?:\(?\d{3}\)?[-.\s]*)\d{3}[-.\s]*\d{4}\b", raw_text)
        if match:
            updates["client.phone"] = match.group(0)
    if updates.get("clinical.icd_code") and updates.get("clinical.primary_diagnosis"):
        diagnosis = updates["clinical.primary_diagnosis"]
        if not diagnosis_code_from_text(diagnosis):
            updates["clinical.primary_diagnosis"] = f"{updates['clinical.icd_code']} - {diagnosis}"
    return updates


def set_combo_text(combo, value):
    value = "" if value is None else str(value)
    index = combo.findText(value)
    if index >= 0:
        combo.setCurrentIndex(index)
    else:
        combo.setEditText(value)


class FormComboBox(QComboBox):
    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()


def make_button_choice(options, value):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    group = QButtonGroup(container)
    group.setExclusive(True)
    container.choice_group = group
    for option in options:
        button = QRadioButton(option)
        button.setProperty("choice_value", option)
        group.addButton(button)
        layout.addWidget(button)
        if str(value or "") == option:
            button.setChecked(True)
    layout.addStretch(1)
    return container


def make_checkbox_choice(options, value):
    container = QWidget()
    layout = QHBoxLayout(container) if len(options) <= 4 else QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    group = QButtonGroup(container)
    group.setExclusive(True)
    container.choice_group = group
    for option in options:
        box = QCheckBox(option)
        box.setProperty("choice_value", option)
        group.addButton(box)
        layout.addWidget(box)
        if str(value or "") == option:
            box.setChecked(True)
    if isinstance(layout, QHBoxLayout):
        layout.addStretch(1)
    container.setStyleSheet(CHOICE_GROUP_STYLE)
    return container


def button_choice_value(widget):
    button = widget.choice_group.checkedButton()
    if not button:
        return ""
    return button.property("choice_value") or ""


def set_button_choice(widget, value):
    value = str(value or "")
    for button in widget.choice_group.buttons():
        button.setChecked(button.property("choice_value") == value)


def selected_values_from_any(value):
    if isinstance(value, list):
        return {str(item) for item in value}
    if isinstance(value, tuple):
        return {str(item) for item in value}
    text = str(value or "").strip()
    if not text:
        return set()
    return {part.strip() for part in re.split(r"[;,]", text) if part.strip()}


def values_matching_options(value, options):
    text = str(value or "").lower()
    return [option for option in options if option.lower() in text]


def make_checkbox_group(options, value):
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    selected = selected_values_from_any(value)
    container.checkboxes = []
    for option in options:
        box = QCheckBox(option)
        box.setChecked(option in selected)
        container.checkboxes.append((option, box))
        layout.addWidget(box)
    container.setStyleSheet(CHECKGROUP_STYLE)
    return container


def checkbox_group_values(widget):
    return [option for option, box in widget.checkboxes if box.isChecked()]


def set_checkbox_group_values(widget, value):
    selected = selected_values_from_any(value)
    for option, box in widget.checkboxes:
        box.setChecked(option in selected)


def make_yes_text_control(checked_value, text_value):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    yes_box = QCheckBox("Yes")
    yes_box.setChecked(bool(checked_value))
    detail = QLineEdit(str(text_value or ""))
    layout.addWidget(yes_box)
    layout.addWidget(detail, 1)
    container.yes_box = yes_box
    container.detail = detail
    return container


def make_date_picker(value):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    line = QLineEdit("" if is_blank_or_placeholder(value) else str(value or ""))
    line.setPlaceholderText("MM/DD/YYYY")
    button = QPushButton("Calendar")
    layout.addWidget(line, 1)
    layout.addWidget(button)
    container.date_line = line
    container.date_button = button

    def pick_date():
        dialog = QDialog(container)
        dialog.setWindowTitle("Choose date")
        dialog_layout = QVBoxLayout(dialog)
        calendar = QCalendarWidget()
        parsed = parse_date_value(line.text())
        calendar.setSelectedDate(QDate(parsed.year, parsed.month, parsed.day) if parsed else QDate.currentDate())
        dialog_layout.addWidget(calendar)
        buttons = QHBoxLayout()
        clear_button = QPushButton("Clear")
        ok_button = QPushButton("Use Date")
        cancel_button = QPushButton("Cancel")
        buttons.addWidget(clear_button)
        buttons.addStretch(1)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        dialog_layout.addLayout(buttons)
        clear_button.clicked.connect(lambda: (line.setText(""), dialog.accept()))
        ok_button.clicked.connect(lambda: (line.setText(qdate_to_text(calendar.selectedDate())), dialog.accept()))
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec()

    button.clicked.connect(pick_date)
    return container


def safe_packet_name(name):
    safe = "".join(ch for ch in str(name or "") if ch.isalnum() or ch in (" ", "-", "_")).strip()
    return safe or "Client"


def data_client_name(data):
    client = data.get("client", {})
    first = str(client.get("first_name", "")).strip()
    last = str(client.get("last_name", "")).strip()
    derived = " ".join(part for part in (first, last) if part).strip()
    return derived or str(client.get("full_name", "")).strip() or "Client"


def unique_archive_name(zip_file, desired_name):
    existing = set(zip_file.namelist())
    if desired_name not in existing:
        return desired_name
    path = Path(desired_name)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent.as_posix()
    for index in range(2, 1000):
        candidate = f"{parent}/{stem} ({index}){suffix}" if parent != "." else f"{stem} ({index}){suffix}"
        if candidate not in existing:
            return candidate
    raise ValueError(f"Too many duplicate attachment names for {desired_name}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OAR + Demographic + Timeliness Form Filler")
        self.resize(980, 760)
        self.data = load_example()
        apply_workflow_defaults(self.data)
        self.widgets = {}
        self.field_fit_spec = load_field_fit_spec()
        self.required_fields = load_required_fields()
        self.fit_counters = {}
        self._updating_defaults = False
        self._auto_full_name = True
        self._auto_birth_names = True
        self.build_ui()

    def build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)

        button_row = QHBoxLayout()
        for label, handler in [
            ("Copy ChatGPT Prompt", self.copy_prompt),
            ("Paste Extracted Text", self.paste_extracted_text),
            ("Load JSON", self.load_json),
            ("Save JSON", self.save_json),
            ("Export Packet ZIP", self.export_packet_zip),
            ("Generate PDFs", self.generate),
        ]:
            button = QPushButton(label)
            button.clicked.connect(handler)
            button_row.addWidget(button)
        button_row.addStretch(1)
        root_layout.addLayout(button_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)
        form.setLabelAlignment(Qt.AlignLeft)

        for section, fields in FIELDS:
            header = QLabel(section)
            header.setStyleSheet("font-weight: 700; font-size: 15px; margin-top: 10px;")
            form.addRow(header)
            for key, label, kind in fields:
                if kind == "yes_text":
                    yes_key, text_key, _ = YES_TEXT_FIELDS[key]
                    widget = make_yes_text_control(get_nested(self.data, yes_key, False), get_nested(self.data, text_key, ""))
                    form.addRow(label, widget)
                    self.widgets[yes_key] = widget.yes_box
                    self.widgets[text_key] = widget.detail
                    self.connect_field_signals(yes_key, widget.yes_box)
                    self.connect_field_signals(text_key, widget.detail)
                    continue
                if kind == "bool":
                    widget = QCheckBox()
                    widget.setChecked(bool(get_nested(self.data, key, False)))
                    form.addRow(label, widget)
                else:
                    row = QWidget()
                    row_layout = QHBoxLayout(row)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    if key in BUTTON_CHOICES:
                        edit = make_button_choice(BUTTON_CHOICES[key], get_nested(self.data, key, ""))
                    elif kind == "check_choice" or key in CHECK_CHOICES:
                        edit = make_checkbox_choice(CHECK_CHOICES[key], get_nested(self.data, key, ""))
                    elif kind == "checkgroup":
                        edit = make_checkbox_group(CHECKBOX_GROUPS[key], get_nested(self.data, key, []))
                    elif kind == "date" or key in DATE_FIELDS:
                        edit = make_date_picker(get_nested(self.data, key, ""))
                    elif key in CHOICES:
                        edit = FormComboBox()
                        edit.setEditable(key not in NON_EDITABLE_CHOICE_FIELDS)
                        edit.addItems(CHOICES[key])
                        edit.setStyleSheet(COMBO_POPUP_STYLE)
                        edit.setMaxVisibleItems(20)
                        set_combo_text(edit, get_nested(self.data, key, ""))
                    elif key in EXTENDED_TEXT_FIELDS:
                        edit = QPlainTextEdit(str(get_nested(self.data, key, "")))
                        edit.setFixedHeight(72)
                        edit.setPlaceholderText("Raw clinical text; the AI will shorten it to the measured PDF field when generating forms.")
                    else:
                        edit = QLineEdit(str(get_nested(self.data, key, "")))
                    row_layout.addWidget(edit, 1)
                    if key in EXTENDED_TEXT_FIELDS:
                        counter = QLabel()
                        counter.setMinimumWidth(120)
                        counter.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        row_layout.addWidget(counter)
                        self.fit_counters[key] = counter
                    if kind == "file":
                        browse = QPushButton("Browse")
                        browse.clicked.connect(lambda _, e=edit: self.pick_file(e))
                        row_layout.addWidget(browse)
                    elif kind == "folder":
                        browse = QPushButton("Browse")
                        browse.clicked.connect(lambda _, e=edit: self.pick_folder(e))
                        row_layout.addWidget(browse)
                    widget = edit
                    form.addRow(label, row)
                self.widgets[key] = widget
                self.connect_field_signals(key, widget)

        attachments_header = QLabel("Source files for packet export")
        attachments_header.setStyleSheet("font-weight: 700; font-size: 15px; margin-top: 10px;")
        form.addRow(attachments_header)
        attachment_box = QWidget()
        attachment_layout = QVBoxLayout(attachment_box)
        attachment_layout.setContentsMargins(0, 0, 0, 0)
        self.attachment_list = QListWidget()
        self.attachment_list.addItems([str(path) for path in self.data.get("attachments", {}).get("source_files", [])])
        attachment_layout.addWidget(self.attachment_list)
        attachment_buttons = QHBoxLayout()
        add_files_button = QPushButton("Add Files")
        remove_files_button = QPushButton("Remove Selected")
        attachment_buttons.addWidget(add_files_button)
        attachment_buttons.addWidget(remove_files_button)
        attachment_buttons.addStretch(1)
        attachment_layout.addLayout(attachment_buttons)
        add_files_button.clicked.connect(self.add_source_files)
        remove_files_button.clicked.connect(self.remove_selected_source_files)
        form.addRow("Files/images/PDFs", attachment_box)

        scroll.setWidget(content)
        root_layout.addWidget(scroll, 1)
        self.setCentralWidget(root)
        self.sync_icd_from_diagnosis()
        self.update_all_fit_counters()
        self.update_required_highlights()

    def connect_field_signals(self, key, widget):
        if isinstance(widget, QCheckBox):
            widget.toggled.connect(lambda _checked=False: self.update_required_highlights())
        elif hasattr(widget, "checkboxes"):
            for _option, box in widget.checkboxes:
                box.toggled.connect(lambda _checked=False: self.update_required_highlights())
        elif hasattr(widget, "choice_group"):
            for button in widget.choice_group.buttons():
                button.toggled.connect(lambda _checked=False: self.update_required_highlights())
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(lambda _text="": self.update_required_highlights())
            widget.editTextChanged.connect(lambda _text="": self.update_required_highlights())
            if key == "clinical.primary_diagnosis":
                widget.currentTextChanged.connect(lambda _text="": self.sync_icd_from_diagnosis())
                widget.editTextChanged.connect(lambda _text="": self.sync_icd_from_diagnosis())
            elif key == "clinical.first_appointment_offered_time":
                widget.currentTextChanged.connect(lambda _text="": self.apply_timeliness_time_defaults_from_ui())
            elif key == "clinical.follow_up_offered_time":
                widget.currentTextChanged.connect(lambda _text="": self.apply_follow_up_time_defaults_from_ui())
        elif hasattr(widget, "date_line"):
            widget.date_line.textChanged.connect(lambda _text="": self.update_required_highlights())
            if key == "clinical.first_appointment_offered_date":
                widget.date_line.textChanged.connect(lambda _text="": self.apply_timeliness_defaults_from_ui())
            elif key == "clinical.follow_up_offered_date":
                widget.date_line.textChanged.connect(lambda _text="": self.apply_follow_up_defaults_from_ui())
            elif key == "provider.date":
                widget.date_line.textChanged.connect(lambda _text="": self.apply_oar_date_defaults_from_ui())
            elif key == "client.dob":
                widget.date_line.textChanged.connect(lambda _text="": self.update_age_from_dob())
        elif isinstance(widget, QDateEdit):
            widget.dateChanged.connect(lambda _date=None: self.update_required_highlights())
            if key == "clinical.first_appointment_offered_date":
                widget.dateChanged.connect(lambda _date=None: self.apply_timeliness_defaults_from_ui())
            elif key == "provider.date":
                widget.dateChanged.connect(lambda _date=None: self.apply_oar_date_defaults_from_ui())
            elif key == "client.dob":
                widget.dateChanged.connect(lambda _date=None: self.update_age_from_dob())
        elif isinstance(widget, QPlainTextEdit):
            widget.textChanged.connect(lambda k=key: self.update_fit_counter(k))
            widget.textChanged.connect(self.update_required_highlights)
        elif isinstance(widget, QLineEdit):
            widget.textChanged.connect(lambda _text="": self.update_required_highlights())
            if key == "clinical.first_appointment_offered_date":
                widget.textChanged.connect(lambda _text="": self.apply_timeliness_defaults_from_ui())
            elif key == "provider.date":
                widget.textChanged.connect(lambda _text="": self.apply_oar_date_defaults_from_ui())
            elif key in {"clinical.medication_1_name", "clinical.medication_2_name", "clinical.medication_3_name"}:
                widget.textChanged.connect(lambda _text="": self.update_no_medications_from_ui())
            elif key in {"client.first_name", "client.last_name"}:
                widget.textChanged.connect(lambda _text="": self.update_auto_names())
            elif key == "client.full_name":
                widget.textEdited.connect(lambda _text="": self.mark_full_name_manual())
            elif key in {"client.name_at_birth_first", "client.name_at_birth_last"}:
                widget.textEdited.connect(lambda _text="": self.mark_birth_names_manual())

    def widget_text(self, key):
        widget = self.widgets.get(key)
        if widget is None:
            return ""
        if isinstance(widget, QCheckBox):
            return "Yes" if widget.isChecked() else ""
        if hasattr(widget, "checkboxes"):
            return ", ".join(checkbox_group_values(widget))
        if hasattr(widget, "choice_group"):
            return button_choice_value(widget)
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if hasattr(widget, "date_line"):
            return widget.date_line.text()
        if isinstance(widget, OptionalDateEdit):
            return widget.text_value()
        if isinstance(widget, QDateEdit):
            return qdate_to_text(widget.date())
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        return widget.text()

    def set_widget_text(self, key, value):
        widget = self.widgets.get(key)
        if widget is None:
            return
        if isinstance(widget, QComboBox):
            set_combo_text(widget, value)
        elif hasattr(widget, "date_line"):
            widget.date_line.setText("" if is_blank_or_placeholder(value) else str(value or ""))
        elif isinstance(widget, OptionalDateEdit):
            widget.set_from_text(value)
        elif isinstance(widget, QDateEdit):
            widget.setDate(qdate_from_text(value))
        elif hasattr(widget, "checkboxes"):
            set_checkbox_group_values(widget, value)
        elif isinstance(widget, QPlainTextEdit):
            widget.setPlainText(str(value))
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif hasattr(widget, "choice_group"):
            set_button_choice(widget, value)

    def mark_full_name_manual(self):
        if not self._updating_defaults:
            self._auto_full_name = False

    def mark_birth_names_manual(self):
        if not self._updating_defaults:
            self._auto_birth_names = False

    def update_auto_names(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            first = self.widget_text("client.first_name").strip()
            last = self.widget_text("client.last_name").strip()
            display_first = "" if is_blank_or_placeholder(first) else first
            display_last = "" if is_blank_or_placeholder(last) else last
            if self._auto_full_name:
                full_name = " ".join(part for part in (display_first, display_last) if part)
                if full_name:
                    self.set_widget_text("client.full_name", full_name)
            if self._auto_birth_names:
                if display_first:
                    self.set_widget_text("client.name_at_birth_first", display_first)
                if display_last:
                    self.set_widget_text("client.name_at_birth_last", display_last)
        finally:
            self._updating_defaults = False

    def update_age_from_dob(self):
        if self._updating_defaults:
            return
        age = age_from_dob(self.widget_text("client.dob"))
        if age:
            self.set_widget_text("client.age", age)

    def update_no_medications_from_ui(self):
        if self._updating_defaults:
            return
        has_medications = any(self.widget_text(key).strip() for key in (
            "clinical.medication_1_name",
            "clinical.medication_2_name",
            "clinical.medication_3_name",
        ))
        widget = self.widgets.get("clinical.no_medications")
        if has_medications and isinstance(widget, QCheckBox):
            widget.setChecked(False)

    def set_widget_text_if_blank(self, key, value):
        if not value:
            return
        if is_blank_or_placeholder(self.widget_text(key)):
            self.set_widget_text(key, value)

    def apply_oar_date_defaults_from_ui(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            provider_date = self.widget_text("provider.date") or today_text()
            self.set_widget_text_if_blank("clinical.problem_list_date", provider_date)
        finally:
            self._updating_defaults = False

    def apply_timeliness_defaults_from_ui(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            offered = self.widget_text("clinical.first_appointment_offered_date")
            self.set_widget_text("clinical.first_appointment_rendered_date", offered)
            self.set_widget_text_if_blank("clinical.sessions_begin_date", offered)
            plus_seven = add_days_text(offered, 7)
            self.set_widget_text("clinical.follow_up_offered_date", plus_seven)
            self.set_widget_text("clinical.follow_up_rendered_date", plus_seven)
            for key in (
                "clinical.first_contact_time",
                "clinical.first_appointment_offered_time",
                "clinical.first_appointment_rendered_time",
                "clinical.follow_up_offered_time",
                "clinical.follow_up_rendered_time",
            ):
                self.set_widget_text_if_blank(key, "11:00 am")
        finally:
            self._updating_defaults = False

    def apply_timeliness_time_defaults_from_ui(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            offered_time = self.widget_text("clinical.first_appointment_offered_time")
            self.set_widget_text("clinical.first_appointment_rendered_time", offered_time)
        finally:
            self._updating_defaults = False

    def apply_follow_up_defaults_from_ui(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            self.set_widget_text("clinical.follow_up_rendered_date", self.widget_text("clinical.follow_up_offered_date"))
        finally:
            self._updating_defaults = False

    def apply_follow_up_time_defaults_from_ui(self):
        if self._updating_defaults:
            return
        self._updating_defaults = True
        try:
            self.set_widget_text("clinical.follow_up_rendered_time", self.widget_text("clinical.follow_up_offered_time"))
        finally:
            self._updating_defaults = False

    def sync_icd_from_diagnosis(self):
        code = diagnosis_code_from_text(self.widget_text("clinical.primary_diagnosis"))
        icd_widget = self.widgets.get("clinical.icd_code")
        if code and isinstance(icd_widget, QLineEdit):
            current = icd_widget.text().strip()
            if not current or diagnosis_code_from_text(current):
                icd_widget.setText(code)
        self.update_required_highlights()

    def required_field_missing(self, key):
        if key == "clinical.icd_code":
            code = diagnosis_code_from_text(self.widget_text("clinical.primary_diagnosis"))
            return not code and is_blank_or_placeholder(self.widget_text(key))
        return is_blank_or_placeholder(self.widget_text(key))

    def missing_required_fields(self):
        return [label for key, label in self.required_fields.items() if self.required_field_missing(key)]

    def set_field_warning(self, key, warn):
        widget = self.widgets.get(key)
        if widget is None:
            return
        if isinstance(widget, QComboBox):
            widget.setStyleSheet((REQUIRED_STYLE + " " + COMBO_POPUP_STYLE) if warn else COMBO_POPUP_STYLE)
        elif hasattr(widget, "date_line"):
            widget.date_line.setStyleSheet(REQUIRED_STYLE if warn else BASE_INPUT_STYLE)
        elif isinstance(widget, (QLineEdit, QPlainTextEdit, QDateEdit)):
            widget.setStyleSheet(REQUIRED_STYLE if warn else BASE_INPUT_STYLE)
        elif hasattr(widget, "choice_group"):
            widget.setStyleSheet(CHOICE_GROUP_REQUIRED_STYLE if warn else CHOICE_GROUP_STYLE)
        elif hasattr(widget, "checkboxes"):
            widget.setStyleSheet(CHECKGROUP_REQUIRED_STYLE if warn else CHECKGROUP_STYLE)
        else:
            widget.setStyleSheet(REQUIRED_STYLE if warn else "")

    def update_required_highlights(self):
        for key in self.required_fields:
            self.set_field_warning(key, self.required_field_missing(key))

    def update_fit_counter(self, key):
        counter = self.fit_counters.get(key)
        if counter is None:
            return
        entry = field_fit_entry(self.field_fit_spec, key)
        value = self.widget_text(key)
        if not entry:
            counter.setText(f"{len(value)} chars")
            counter.setStyleSheet(COUNTER_OK_STYLE)
            return
        used = rendered_width_points(value, entry)
        limit = float(entry.get("max_width_points") or 0)
        if limit <= 0:
            counter.setText(f"{len(value)} chars")
            counter.setStyleSheet(COUNTER_OK_STYLE)
            return
        counter.setText(f"{used:.0f}/{limit:.0f} pt")
        counter.setToolTip("Measured rendered text width versus writable PDF width.")
        counter.setStyleSheet(COUNTER_BAD_STYLE if used > limit else COUNTER_OK_STYLE)

    def update_all_fit_counters(self):
        for key in self.fit_counters:
            self.update_fit_counter(key)

    def over_limit_fields(self):
        over = []
        for key in self.fit_counters:
            entry = field_fit_entry(self.field_fit_spec, key)
            if not entry:
                continue
            used = rendered_width_points(self.widget_text(key), entry)
            limit = float(entry.get("max_width_points") or 0)
            if limit > 0 and used > limit:
                over.append((key, used, limit))
        return over

    def pick_file(self, edit):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if path:
            edit.setText(path)

    def pick_folder(self, edit):
        path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if path:
            edit.setText(path)

    def add_source_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add source files",
            "",
            "Source files (*.pdf *.png *.jpg *.jpeg *.tif *.tiff *.bmp *.txt *.docx);;All files (*)",
        )
        existing = {self.attachment_list.item(i).text() for i in range(self.attachment_list.count())}
        for path in paths:
            if path not in existing:
                self.attachment_list.addItem(path)
                existing.add(path)

    def remove_selected_source_files(self):
        for item in self.attachment_list.selectedItems():
            self.attachment_list.takeItem(self.attachment_list.row(item))

    def collect_data(self):
        data = load_example()
        for key, widget in self.widgets.items():
            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif hasattr(widget, "checkboxes"):
                value = checkbox_group_values(widget)
            elif hasattr(widget, "choice_group"):
                value = button_choice_value(widget)
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif hasattr(widget, "date_line"):
                value = widget.date_line.text()
            elif isinstance(widget, OptionalDateEdit):
                value = widget.text_value()
            elif isinstance(widget, QDateEdit):
                value = qdate_to_text(widget.date())
            elif isinstance(widget, QPlainTextEdit):
                value = widget.toPlainText()
            else:
                value = widget.text()
            set_nested(data, key, value)
        data.setdefault("attachments", {})["source_files"] = [
            self.attachment_list.item(i).text() for i in range(self.attachment_list.count())
        ]
        diagnosis = get_nested(data, "clinical.primary_diagnosis", "")
        diagnosis_code = diagnosis_code_from_text(diagnosis)
        if diagnosis_code:
            set_nested(data, "clinical.icd_code", diagnosis_code)
        apply_workflow_defaults(data)
        normalize_app_data(data)
        return data

    def apply_data_to_widgets(self, data):
        clear_placeholders(data)
        apply_workflow_defaults(data)
        self.data = data
        for key, widget in self.widgets.items():
            value = get_nested(data, key, False if isinstance(widget, QCheckBox) else "")
            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif hasattr(widget, "checkboxes"):
                set_checkbox_group_values(widget, value)
            elif hasattr(widget, "choice_group"):
                set_button_choice(widget, value)
            elif isinstance(widget, QComboBox):
                set_combo_text(widget, value)
            elif hasattr(widget, "date_line"):
                widget.date_line.setText("" if is_blank_or_placeholder(value) else str(value or ""))
            elif isinstance(widget, OptionalDateEdit):
                widget.set_from_text(value)
            elif isinstance(widget, QDateEdit):
                widget.setDate(qdate_from_text(value))
            elif isinstance(widget, QPlainTextEdit):
                widget.setPlainText(str(value))
            else:
                widget.setText(str(value))
        self.attachment_list.clear()
        self.attachment_list.addItems([str(path) for path in data.get("attachments", {}).get("source_files", [])])
        self.sync_icd_from_diagnosis()
        self.update_all_fit_counters()
        self.update_required_highlights()

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        try:
            self.apply_data_to_widgets(json.loads(Path(path).read_text(encoding="utf-8")))
        except Exception as exc:
            QMessageBox.critical(self, "Load failed", str(exc))

    def copy_prompt(self):
        QApplication.clipboard().setText(EXTRACTION_PROMPT)
        QMessageBox.information(self, "Prompt copied", "Extraction prompt copied to clipboard.")

    def paste_extracted_text(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Paste Extracted Patient Text")
        dialog.resize(760, 560)
        layout = QVBoxLayout(dialog)
        instructions = QLabel(
            "Paste the text extracted by ChatGPT or another source. Best format: one field per line, like 'DOB: 01/01/2000'."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        text_box = QTextEdit()
        text_box.setPlainText(read_clipboard_text())
        text_box.setFocus()
        layout.addWidget(text_box, 1)
        buttons = QHBoxLayout()
        paste_button = QPushButton("Paste from Clipboard")
        apply_button = QPushButton("Apply to Form")
        cancel_button = QPushButton("Cancel")
        buttons.addStretch(1)
        buttons.addWidget(paste_button)
        buttons.addWidget(apply_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        def apply_text():
            try:
                updates = parse_extracted_text(text_box.toPlainText())
                if not updates:
                    QMessageBox.warning(
                        dialog,
                        "No fields found",
                        "No recognizable fields were found. Use lines like 'Full name: Jane Doe' or click Copy ChatGPT Prompt.",
                    )
                    return
                applied = 0
                for key, value in updates.items():
                    widget = self.widgets.get(key)
                    if widget is None:
                        continue
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
                    elif hasattr(widget, "checkboxes"):
                        set_checkbox_group_values(widget, value)
                    elif isinstance(widget, QPlainTextEdit):
                        widget.setPlainText(str(value))
                    elif isinstance(widget, QComboBox):
                        set_combo_text(widget, value)
                    elif hasattr(widget, "date_line"):
                        widget.date_line.setText("" if is_blank_or_placeholder(value) else str(value or ""))
                    elif isinstance(widget, OptionalDateEdit):
                        widget.set_from_text(value)
                    elif isinstance(widget, QDateEdit):
                        widget.setDate(qdate_from_text(value))
                    elif hasattr(widget, "choice_group"):
                        set_button_choice(widget, value)
                    else:
                        widget.setText(str(value))
                    applied += 1
                QMessageBox.information(dialog, "Fields updated", f"Updated {applied} fields. Review before generating PDFs.")
                dialog.accept()
            except Exception as exc:
                QMessageBox.critical(dialog, "Import failed", str(exc))

        def paste_clipboard():
            text = read_clipboard_text()
            if not text:
                QMessageBox.warning(dialog, "Clipboard empty", "Windows clipboard does not currently contain text.")
                return
            text_box.setPlainText(text)

        paste_button.clicked.connect(paste_clipboard)
        apply_button.clicked.connect(apply_text)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec()

    def save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            Path(path).write_text(json.dumps(self.collect_data(), indent=2), encoding="utf-8")
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def export_packet_zip(self):
        data = self.collect_data()
        client_name = safe_packet_name(data_client_name(data))
        default_name = f"Client Packet - {client_name}.zip"
        default_path = Path(data.get("paths", {}).get("output_dir") or Path.home() / "Documents" / "FormFillerOutputs") / default_name
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Packet ZIP",
            str(default_path),
            "ZIP files (*.zip);;All files (*)",
        )
        if not path:
            return
        if not path.lower().endswith(".zip"):
            path += ".zip"
        zip_path = Path(path)
        try:
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            attachments = [Path(p) for p in data.get("attachments", {}).get("source_files", []) if str(p).strip()]
            manifest = {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "client_name": data_client_name(data),
                "included_files": [],
                "missing_files": [],
            }
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("patient_input.json", json.dumps(data, indent=2))
                for file_path in attachments:
                    if file_path.exists() and file_path.is_file():
                        archive_name = unique_archive_name(zf, f"source_files/{file_path.name}")
                        zf.write(file_path, archive_name)
                        manifest["included_files"].append({"source": str(file_path), "archive_name": archive_name})
                    else:
                        manifest["missing_files"].append(str(file_path))
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            notes = [f"Created:\n{zip_path}"]
            missing_required = self.missing_required_fields()
            if missing_required:
                notes.append("Missing required fields:\n" + "\n".join(f"- {item}" for item in missing_required))
            over_limit = self.over_limit_fields()
            if over_limit:
                notes.append(
                    "Narrative fields over measured PDF width:\n"
                    + "\n".join(f"- {key}: {used:.0f}/{limit:.0f} pt" for key, used, limit in over_limit)
                )
            if manifest["missing_files"]:
                notes.append("Missing source files:\n" + "\n".join(f"- {item}" for item in manifest["missing_files"]))
            QMessageBox.information(self, "Packet exported", "\n\n".join(notes))
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def choose_generation_options(self, data):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate PDFs")
        dialog.resize(620, 140)
        layout = QVBoxLayout(dialog)

        folder_row = QHBoxLayout()
        folder_edit = QLineEdit(str(data.get("paths", {}).get("output_dir", "")))
        browse_button = QPushButton("Browse")
        folder_row.addWidget(QLabel("Output folder:"))
        folder_row.addWidget(folder_edit, 1)
        folder_row.addWidget(browse_button)
        layout.addLayout(folder_row)

        open_after = QCheckBox("Open generated PDFs after creating them")
        open_after.setChecked(True)
        layout.addWidget(open_after)

        buttons = QHBoxLayout()
        generate_button = QPushButton("Generate")
        cancel_button = QPushButton("Cancel")
        buttons.addStretch(1)
        buttons.addWidget(generate_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        def browse_folder():
            path = QFileDialog.getExistingDirectory(self, "Select output folder", folder_edit.text())
            if path:
                folder_edit.setText(path)

        browse_button.clicked.connect(browse_folder)
        generate_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return None
        output_dir = folder_edit.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Missing output folder", "Choose an output folder before generating PDFs.")
            return None
        return output_dir, open_after.isChecked()

    def generate(self):
        try:
            data = self.collect_data()
            options = self.choose_generation_options(data)
            if options is None:
                return
            output_dir_text, open_after = options
            base_output_dir = Path(output_dir_text)
            output_dir = base_output_dir / safe_packet_name(data_client_name(data))
            data.setdefault("paths", {})["output_dir"] = str(output_dir)
            output_widget = self.widgets.get("paths.output_dir")
            if output_widget is not None:
                output_widget.setText(str(base_output_dir))
            output_dir.mkdir(parents=True, exist_ok=True)
            outputs = [fill_demographic(data, output_dir), fill_oar_flattened(data, output_dir), fill_timeliness(data, output_dir)]
            if open_after:
                for path in outputs:
                    os.startfile(path)
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Information)
            message.setWindowTitle("PDFs generated")
            message.setText("\n".join(str(path) for path in outputs))
            open_folder_button = message.addButton("Open Output Folder", QMessageBox.ActionRole)
            message.addButton(QMessageBox.Ok)
            message.exec()
            if message.clickedButton() == open_folder_button:
                os.startfile(output_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Generation failed", str(exc))


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setStyleSheet(APP_STYLE)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.write_text(traceback.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
