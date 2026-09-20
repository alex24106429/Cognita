import copy
import json
import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTextEdit, QTabWidget,
    QScrollArea, QWidget, QGroupBox, QFileDialog, QMessageBox,
    QFrame
)

from config import load_vault, save_vault, VAULT_PATH

EXAMPLE_VAULT = {
    "personal_identity": {
        "bsn": "999999990",
        "first_name": "Marloes",
        "initials": "M.J.",
        "prefix": "van den",
        "last_name": "Berg",
        "maiden_name": "Vermeulen",
        "date_of_birth": "1976-08-14",
        "place_of_birth": "Delft",
        "gender": "female",
        "nationality": "Nederlandse",
        "marital_status": "gehuwd",
        "contact": {
            "email": "marloes.vandenberg.test@example.nl",
            "phone_mobile": "06-12345678",
            "phone_home": "070-9876543"
        },
        "address": {
            "street": "Laan van Meerdervoort",
            "house_number": "342",
            "house_number_extension": "B",
            "postal_code": "2563 AL",
            "city": "Den Haag",
            "municipality": "Den Haag",
            "country": "Nederland"
        },
        "bank_account": {
            "iban": "NL91INGB0001234567",
            "bic": "INGBNL2A",
            "account_holder": "M.J. van den Berg"
        }
    },
    "living_situation": {
        "housing_type": "huurwoning",
        "landlord_type": "woningcorporatie",
        "landlord_name": "Haag Wonen",
        "floor_level": 2,
        "elevator_present": True,
        "doorstep_barrier_cm": 6.5,
        "household_members": [
            {
                "relation": "partner",
                "first_name": "Jeroen",
                "last_name": "van den Berg",
                "date_of_birth": "1974-03-22",
                "bsn": "999999991",
                "employment_status": "full-time werkend"
            }
        ],
        "informal_care": {
            "caregiver_name": "Jeroen van den Berg",
            "relation": "partner",
            "hours_per_week": 14,
            "burden_level": "overbelast",
            "tasks_performed": [
                "Koken en maaltijdverzorging",
                "Zware huishoudelijke taken",
                "Begeleiding bij extern medisch transport"
            ]
        }
    },
    "medical_profile": {
        "primary_diagnosis": "Secundair Progressieve Multiple Sclerose (SPMS)",
        "icd_10_code": "G35",
        "diagnosis_year": 2019,
        "prognosis": "Progressief verslechterend beloop met toenemende motorische uitval",
        "practitioners": {
            "general_practitioner": {
                "name": "Dr. E.J. de Wit",
                "practice_name": "Huisartsenpraktijk Bomenbuurt",
                "address": "Fahrenheitstraat 112, 2561 ED Den Haag",
                "phone": "070-3456789",
                "big_number": "19045678901"
            },
            "neurologist": {
                "name": "Dr. S.A. Bakker",
                "hospital": "HagaZiekenhuis",
                "department": "Neurologie / MS Centrum",
                "big_number": "29012345678"
            },
            "physiotherapist": {
                "name": "T. van Rijn",
                "practice_name": "FysioDenHaag",
                "phone": "070-5554321"
            }
        },
        "functional_limitations": {
            "mobility": {
                "max_walking_distance_meters": 10,
                "requires_walking_aids": True,
                "current_aids": [
                    "Rollator binnenshuis",
                    "Handbewogen rolstoel (onvoldoende zelfstandigheid)"
                ],
                "transfer_ability": "Kan transfer maken met steun, maar armkracht neemt af",
                "stair_climbing": "Niet meer mogelijk"
            },
            "upper_extremities": {
                "fine_motor_control": "Ernstige ataxie en tremoren in beide handen",
                "gross_motor_control": "Krachtsverlies graad 3/5 bilateraal",
                "typing_capacity": "Uiterst beperkt; snel vermoeid na 5 minuten",
                "mouse_navigation": "Niet nauwkeurig; mist kleine knoppen door tremoren"
            },
            "energy_and_cognition": {
                "cognitive_state": "Helder, wilsbekwaam, geen cognitieve stoornissen",
                "fatigue_level": "Ernstige neurogene vermoeidheid na 2 uur fysieke/geestelijke inspanning",
                "max_sitting_duration_minutes": 45
            }
        }
    },
    "wmo_application_data": {
        "target_municipality": "Gemeente Den Haag",
        "requested_facilities": [
            {
                "type": "Elektrische rolstoel voor buiten- en binnengebruik",
                "category": "Mobiliteitshulpmiddelen",
                "motivation": "Aanvrager heeft minder dan 10 meter loopafstand. Handbewogen rolstoel kan wegens armkrachtverlies niet zelfstandig worden aangedreven. Elektrische rolstoel met joystickbediening is noodzakelijk voor zelfstandige participatie."
            },
            {
                "type": "Woningaanpassing drempelhulp",
                "category": "Wonen",
                "motivation": "Toegang tot het balkon en voordeur heeft een drempel van 6.5 cm waardoor de rolstoel niet zelfstandig naar binnen/buiten kan rijden."
            }
        ],
        "previous_wmo_allocations": [
            {
                "year": 2021,
                "facility": "Regiotaxi pas",
                "status": "actief"
            }
        ]
    },
    "uwv_wia_application_data": {
        "employment_history": {
            "last_employer": {
                "company_name": "Havenlogistiek Rotterdam B.V.",
                "kvk_number": "24123456",
                "address": "Maashaven Zuidzijde 12, 3081 AE Rotterdam",
                "contact_person": "Mevr. A. van Dongen (HR Manager)",
                "contact_phone": "010-8765432",
                "contact_email": "hr@havenlogistiek-rdam.nl"
            },
            "job_title": "Senior Logistiek Coördinator",
            "contract_type": "onbepaalde tijd",
            "contracted_hours_per_week": 36.0,
            "gross_monthly_salary_eur": 3850.00
        },
        "sick_leave_timeline": {
            "first_day_of_illness": "2022-10-10",
            "current_sick_leave_duration_weeks": 104,
            "reintegration_efforts": {
                "spoor_1_completed": True,
                "spoor_1_result": "Eigen werk niet meer passend; geen herplaatsingsmogelijkheden binnen organisatie wegens ernstige fysieke en energetische beperkingen.",
                "spoor_2_completed": True,
                "spoor_2_agency": "Match & Re-integratie Den Haag",
                "spoor_2_result": "Geen duurzame benutbare mogelijkheden op de open arbeidsmarkt gevonden.",
                "arbodienst": {
                    "name": "ArboNed Den Haag",
                    "company_doctor": "Dr. M.L. Jansen",
                    "big_number": "89034567890"
                }
            }
        },
        "functional_limitations_fml_summary": {
            "energetic_limitation_hours_per_day": 2.0,
            "energetic_limitation_hours_per_week": 8.0,
            "working_conditions": "Geen deadlines, geen repetitieve handmatige invoer, geen fysiek tillen boven 1 kg, rustmogelijkheid noodzakelijk."
        }
    },
    "svb_pgb_data": {
        "pgb_indication": {
            "indication_number": "PGB-2024-DH-8842",
            "statutory_basis": "Wmo 2015",
            "awarded_by": "Gemeente Den Haag",
            "budget_period_start": "2024-01-01",
            "budget_period_end": "2024-12-31",
            "total_annual_budget_eur": 18450.00
        },
        "registered_caregivers": [
            {
                "caregiver_id": "CRG-001",
                "type": "ZZP / Professionele zorgverlener",
                "company_name": "Zorgpraktijk Haaglanden",
                "kvk_number": "27987654",
                "bsn": "999999992",
                "first_name": "Fatima",
                "last_name": "El Amrani",
                "iban": "NL44RABO0123987654",
                "hourly_rate_eur": 45.00,
                "service_type": "Persoonlijke verzorging (hulp bij wassen, kleden, transfers)"
            },
            {
                "caregiver_id": "CRG-002",
                "type": "Informeel / Partner",
                "bsn": "999999991",
                "first_name": "Jeroen",
                "last_name": "van den Berg",
                "iban": "NL91INGB0001234567",
                "hourly_rate_eur": 23.50,
                "service_type": "Individuele begeleiding"
            }
        ],
        "monthly_declaration_template": {
            "target_month": "2024-08",
            "caregiver_id": "CRG-001",
            "declared_hours": 32.0,
            "total_amount_eur": 1440.00,
            "description": "32 uur persoonlijke verzorging verdeeld over 16 dagen (2 uur per sessie: ochtendtransfer, wassen, aankleden)."
        }
    }
}


def get_deep(d: dict, path: list, default=""):
    curr = d
    for p in path:
        if not isinstance(curr, dict) or p not in curr:
            return default
        curr = curr[p]
    return curr if curr is not None else default


def parse_num_or_str(text: str):
    t = text.strip()
    if not t:
        return ""
    try:
        if "." in t:
            return float(t)
        return int(t)
    except ValueError:
        return t


def parse_json_or_raw(text: str):
    t = text.strip()
    if not t:
        return None
    try:
        return json.loads(t)
    except Exception:
        return t


def prune_empty(d):
    if not isinstance(d, dict):
        return d
    pruned = {}
    for k, v in d.items():
        if isinstance(v, dict):
            sub = prune_empty(v)
            if sub:
                pruned[k] = sub
        elif v is not None and v != "" and v != [] and v != {}:
            pruned[k] = v
    return pruned


class VaultSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cognita — User Data Setup")
        self.resize(860, 700)
        self.setMinimumSize(740, 540)
        self.setModal(True)

        self.vault_data = {}
        loaded = load_vault()
        if loaded and isinstance(loaded, dict):
            self.vault_data = copy.deepcopy(loaded)

        self._previous_tab_index = 0
        self._build_ui()
        self._sync_data_to_form()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        # Header Bar
        header_row = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        title_lbl = QLabel("User Data Setup")
        title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #9aa4ff;")
        desc_lbl = QLabel(
            "Provide personal identity, address, medical records, and social provision data for automated desktop tasks. All fields are completely optional."
        )
        desc_lbl.setStyleSheet("color: #9aa0b4; font-size: 11px;")
        desc_lbl.setWordWrap(True)

        header_text.addWidget(title_lbl)
        header_text.addWidget(desc_lbl)
        header_row.addLayout(header_text, 1)

        # Action Buttons in Header
        load_ex_btn = QPushButton("⚡ Load Example Template")
        load_ex_btn.setToolTip(
            "Populate all fields with the full example profile")
        load_ex_btn.clicked.connect(self._on_load_example)
        header_row.addWidget(load_ex_btn)

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setToolTip("Clear all fields in the vault")
        clear_btn.clicked.connect(self._on_clear_all)
        header_row.addWidget(clear_btn)

        root.addLayout(header_row)

        # File path & status banner
        banner_row = QHBoxLayout()
        file_exists = VAULT_PATH.is_file()
        status_text = "Found" if file_exists else "Not yet created"
        status_color = "#7bd88f" if file_exists else "#ffcb6b"

        banner_row.addStretch()

        import_btn = QPushButton("📂 Import…")
        import_btn.clicked.connect(self._on_import_file)
        export_btn = QPushButton("💾 Export…")
        export_btn.clicked.connect(self._on_export_file)
        banner_row.addWidget(import_btn)
        banner_row.addWidget(export_btn)
        root.addLayout(banner_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #34363f;")
        root.addWidget(sep)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.tabs.addTab(self._build_personal_tab(), "👤 Identity and Contact")
        self.tabs.addTab(self._build_living_tab(), "🏡 Living Situation")
        self.tabs.addTab(self._build_medical_tab(), "🩺 Medical Profile")
        self.tabs.addTab(self._build_services_tab(),
                         "🏛️ Provisions (WMO/UWV/PGB)")
        self.tabs.addTab(self._build_json_tab(), "📋 Raw JSON Editor")

        root.addWidget(self.tabs, 1)

        # Bottom Buttons
        btn_row = QHBoxLayout()
        self.status_bar_lbl = QLabel()
        self.status_bar_lbl.setStyleSheet("font-size: 11px;")
        btn_row.addWidget(self.status_bar_lbl)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Data")
        save_btn.setObjectName("startBtn")
        save_btn.setMinimumWidth(110)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        root.addLayout(btn_row)

    def _create_scroll_tab(self, layout: QVBoxLayout) -> QScrollArea:
        container = QWidget()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        container.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def _build_personal_tab(self) -> QWidget:
        layout = QVBoxLayout()

        # Personal Identity
        id_box = QGroupBox("Personal Identity")
        grid1 = QGridLayout(id_box)
        grid1.setSpacing(8)

        self.first_name_edit = QLineEdit()
        self.initials_edit = QLineEdit()
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("e.g. van den, de")
        self.last_name_edit = QLineEdit()
        self.maiden_name_edit = QLineEdit()
        self.bsn_edit = QLineEdit()
        self.bsn_edit.setPlaceholderText("9-digit Dutch BSN")

        self.dob_edit = QLineEdit()
        self.dob_edit.setPlaceholderText("YYYY-MM-DD")
        self.pob_edit = QLineEdit()
        self.gender_edit = QLineEdit()
        self.nationality_edit = QLineEdit()
        self.marital_edit = QLineEdit()

        grid1.addWidget(QLabel("First Name:"), 0, 0)
        grid1.addWidget(self.first_name_edit, 0, 1)
        grid1.addWidget(QLabel("Initials:"), 0, 2)
        grid1.addWidget(self.initials_edit, 0, 3)

        grid1.addWidget(QLabel("Prefix (Tussenvoegsel):"), 1, 0)
        grid1.addWidget(self.prefix_edit, 1, 1)
        grid1.addWidget(QLabel("Last Name:"), 1, 2)
        grid1.addWidget(self.last_name_edit, 1, 3)

        grid1.addWidget(QLabel("Maiden Name:"), 2, 0)
        grid1.addWidget(self.maiden_name_edit, 2, 1)
        grid1.addWidget(QLabel("BSN (Burger Service Nr):"), 2, 2)
        grid1.addWidget(self.bsn_edit, 2, 3)

        grid1.addWidget(QLabel("Date of Birth:"), 3, 0)
        grid1.addWidget(self.dob_edit, 3, 1)
        grid1.addWidget(QLabel("Place of Birth:"), 3, 2)
        grid1.addWidget(self.pob_edit, 3, 3)

        grid1.addWidget(QLabel("Gender:"), 4, 0)
        grid1.addWidget(self.gender_edit, 4, 1)
        grid1.addWidget(QLabel("Nationality:"), 4, 2)
        grid1.addWidget(self.nationality_edit, 4, 3)

        grid1.addWidget(QLabel("Marital Status:"), 5, 0)
        grid1.addWidget(self.marital_edit, 5, 1)

        layout.addWidget(id_box)

        # Contact Details
        contact_box = QGroupBox("Contact Details")
        grid2 = QGridLayout(contact_box)
        grid2.setSpacing(8)

        self.email_edit = QLineEdit()
        self.phone_mobile_edit = QLineEdit()
        self.phone_home_edit = QLineEdit()

        grid2.addWidget(QLabel("Email Address:"), 0, 0)
        grid2.addWidget(self.email_edit, 0, 1, 1, 3)
        grid2.addWidget(QLabel("Mobile Phone:"), 1, 0)
        grid2.addWidget(self.phone_mobile_edit, 1, 1)
        grid2.addWidget(QLabel("Home Phone:"), 1, 2)
        grid2.addWidget(self.phone_home_edit, 1, 3)

        layout.addWidget(contact_box)

        # Address
        addr_box = QGroupBox("Residential Address")
        grid3 = QGridLayout(addr_box)
        grid3.setSpacing(8)

        self.street_edit = QLineEdit()
        self.house_no_edit = QLineEdit()
        self.house_ext_edit = QLineEdit()
        self.postal_edit = QLineEdit()
        self.city_edit = QLineEdit()
        self.municipality_edit = QLineEdit()
        self.country_edit = QLineEdit()

        grid3.addWidget(QLabel("Street:"), 0, 0)
        grid3.addWidget(self.street_edit, 0, 1)
        grid3.addWidget(QLabel("House No:"), 0, 2)
        grid3.addWidget(self.house_no_edit, 0, 3)
        grid3.addWidget(QLabel("Ext:"), 0, 4)
        grid3.addWidget(self.house_ext_edit, 0, 5)

        grid3.addWidget(QLabel("Postal Code:"), 1, 0)
        grid3.addWidget(self.postal_edit, 1, 1)
        grid3.addWidget(QLabel("City:"), 1, 2)
        grid3.addWidget(self.city_edit, 1, 3, 1, 3)

        grid3.addWidget(QLabel("Municipality (Gemeente):"), 2, 0)
        grid3.addWidget(self.municipality_edit, 2, 1)
        grid3.addWidget(QLabel("Country:"), 2, 2)
        grid3.addWidget(self.country_edit, 2, 3, 1, 3)

        layout.addWidget(addr_box)

        # Bank Account
        bank_box = QGroupBox("Bank Account")
        grid4 = QGridLayout(bank_box)
        grid4.setSpacing(8)

        self.bank_holder_edit = QLineEdit()
        self.iban_edit = QLineEdit()
        self.bic_edit = QLineEdit()

        grid4.addWidget(QLabel("Account Holder:"), 0, 0)
        grid4.addWidget(self.bank_holder_edit, 0, 1)
        grid4.addWidget(QLabel("IBAN:"), 1, 0)
        grid4.addWidget(self.iban_edit, 1, 1)
        grid4.addWidget(QLabel("BIC:"), 1, 2)
        grid4.addWidget(self.bic_edit, 1, 3)

        layout.addWidget(bank_box)
        layout.addStretch()

        return self._create_scroll_tab(layout)

    def _build_living_tab(self) -> QWidget:
        layout = QVBoxLayout()

        # Housing & Accessibility
        house_box = QGroupBox("Housing & Accessibility")
        grid1 = QGridLayout(house_box)
        grid1.setSpacing(8)

        self.housing_type_edit = QLineEdit()
        self.housing_type_edit.setPlaceholderText(
            "e.g. huurwoning, koopwoning")
        self.landlord_type_edit = QLineEdit()
        self.landlord_type_edit.setPlaceholderText(
            "e.g. woningcorporatie, particulier")
        self.landlord_name_edit = QLineEdit()
        self.floor_level_edit = QLineEdit()
        self.doorstep_cm_edit = QLineEdit()
        self.doorstep_cm_edit.setPlaceholderText("cm")

        self.elevator_combo = QComboBox()
        self.elevator_combo.addItems(["(Not specified)", "Yes", "No"])

        grid1.addWidget(QLabel("Housing Type:"), 0, 0)
        grid1.addWidget(self.housing_type_edit, 0, 1)
        grid1.addWidget(QLabel("Landlord Type:"), 0, 2)
        grid1.addWidget(self.landlord_type_edit, 0, 3)

        grid1.addWidget(QLabel("Landlord / Corporation:"), 1, 0)
        grid1.addWidget(self.landlord_name_edit, 1, 1)
        grid1.addWidget(QLabel("Floor Level:"), 1, 2)
        grid1.addWidget(self.floor_level_edit, 1, 3)

        grid1.addWidget(QLabel("Doorstep Barrier (cm):"), 2, 0)
        grid1.addWidget(self.doorstep_cm_edit, 2, 1)
        grid1.addWidget(QLabel("Elevator Present:"), 2, 2)
        grid1.addWidget(self.elevator_combo, 2, 3)

        layout.addWidget(house_box)

        # Informal Care
        care_box = QGroupBox("Informal Care (Mantelzorg)")
        grid2 = QGridLayout(care_box)
        grid2.setSpacing(8)

        self.caregiver_name_edit = QLineEdit()
        self.caregiver_rel_edit = QLineEdit()
        self.caregiver_hours_edit = QLineEdit()
        self.caregiver_burden_edit = QLineEdit()
        self.caregiver_burden_edit.setPlaceholderText(
            "e.g. normaal, zwaar, overbelast")

        grid2.addWidget(QLabel("Caregiver Name:"), 0, 0)
        grid2.addWidget(self.caregiver_name_edit, 0, 1)
        grid2.addWidget(QLabel("Relation:"), 0, 2)
        grid2.addWidget(self.caregiver_rel_edit, 0, 3)

        grid2.addWidget(QLabel("Hours per Week:"), 1, 0)
        grid2.addWidget(self.caregiver_hours_edit, 1, 1)
        grid2.addWidget(QLabel("Burden Level:"), 1, 2)
        grid2.addWidget(self.caregiver_burden_edit, 1, 3)

        grid2.addWidget(QLabel("Tasks Performed:"), 2, 0)
        self.caregiver_tasks_edit = QTextEdit()
        self.caregiver_tasks_edit.setPlaceholderText(
            "One task per line, e.g.:\nKoken en maaltijdverzorging\nZware huishoudelijke taken")
        self.caregiver_tasks_edit.setMinimumHeight(60)
        grid2.addWidget(self.caregiver_tasks_edit, 2, 1, 1, 3)

        layout.addWidget(care_box)

        # Household Members
        members_box = QGroupBox("Household Members (JSON Array)")
        mv = QVBoxLayout(members_box)
        m_head = QHBoxLayout()
        m_head.addWidget(
            QLabel("List partners, children, or other co-habitants:"))
        m_head.addStretch()
        add_partner_btn = QPushButton("➕ Add Partner Template")
        add_partner_btn.clicked.connect(
            self._insert_household_partner_template)
        m_head.addWidget(add_partner_btn)
        mv.addLayout(m_head)

        self.household_members_edit = QTextEdit()
        self.household_members_edit.setFont(
            QFont("Consolas, Menlo, monospace", 9))
        self.household_members_edit.setPlaceholderText(
            '[\n  {\n    "relation": "partner",\n    "first_name": "...",\n    "last_name": "...",\n    "date_of_birth": "...",\n    "bsn": "...",\n    "employment_status": "..."\n  }\n]')
        self.household_members_edit.setMinimumHeight(90)
        mv.addWidget(self.household_members_edit)
        layout.addWidget(members_box)

        layout.addStretch()
        return self._create_scroll_tab(layout)

    def _build_medical_tab(self) -> QWidget:
        layout = QVBoxLayout()

        # Diagnosis
        diag_box = QGroupBox("Diagnosis & Prognosis")
        grid1 = QGridLayout(diag_box)
        grid1.setSpacing(8)

        self.med_diagnosis_edit = QLineEdit()
        self.med_icd10_edit = QLineEdit()
        self.med_diag_year_edit = QLineEdit()
        self.med_prognosis_edit = QLineEdit()

        grid1.addWidget(QLabel("Primary Diagnosis:"), 0, 0)
        grid1.addWidget(self.med_diagnosis_edit, 0, 1, 1, 3)

        grid1.addWidget(QLabel("ICD-10 Code:"), 1, 0)
        grid1.addWidget(self.med_icd10_edit, 1, 1)
        grid1.addWidget(QLabel("Year of Diagnosis:"), 1, 2)
        grid1.addWidget(self.med_diag_year_edit, 1, 3)

        grid1.addWidget(QLabel("Prognosis:"), 2, 0)
        grid1.addWidget(self.med_prognosis_edit, 2, 1, 1, 3)

        layout.addWidget(diag_box)

        # Practitioners
        prac_box = QGroupBox("Medical Practitioners & Contacts")
        grid2 = QGridLayout(prac_box)
        grid2.setSpacing(8)

        # General Practitioner
        self.gp_name_edit = QLineEdit()
        self.gp_practice_edit = QLineEdit()
        self.gp_phone_edit = QLineEdit()
        self.gp_big_edit = QLineEdit()
        self.gp_addr_edit = QLineEdit()

        grid2.addWidget(
            QLabel("<b>General Practitioner (Huisarts):</b>"), 0, 0, 1, 4)
        grid2.addWidget(QLabel("Name:"), 1, 0)
        grid2.addWidget(self.gp_name_edit, 1, 1)
        grid2.addWidget(QLabel("Practice:"), 1, 2)
        grid2.addWidget(self.gp_practice_edit, 1, 3)
        grid2.addWidget(QLabel("Address:"), 2, 0)
        grid2.addWidget(self.gp_addr_edit, 2, 1)
        grid2.addWidget(QLabel("Phone / BIG:"), 2, 2)
        gp_sub = QHBoxLayout()
        gp_sub.addWidget(self.gp_phone_edit, 2)
        gp_sub.addWidget(self.gp_big_edit, 2)
        grid2.addLayout(gp_sub, 2, 3)

        # Specialist
        self.neuro_name_edit = QLineEdit()
        self.neuro_hosp_edit = QLineEdit()
        self.neuro_dept_edit = QLineEdit()
        self.neuro_big_edit = QLineEdit()

        grid2.addWidget(QLabel("<b>Specialist / Neurologist:</b>"), 3, 0, 1, 4)
        grid2.addWidget(QLabel("Name:"), 4, 0)
        grid2.addWidget(self.neuro_name_edit, 4, 1)
        grid2.addWidget(QLabel("Hospital / Dept:"), 4, 2)
        neuro_sub = QHBoxLayout()
        neuro_sub.addWidget(self.neuro_hosp_edit, 2)
        neuro_sub.addWidget(self.neuro_dept_edit, 2)
        grid2.addLayout(neuro_sub, 4, 3)
        grid2.addWidget(QLabel("BIG Number:"), 5, 0)
        grid2.addWidget(self.neuro_big_edit, 5, 1)

        # Physiotherapist
        self.physio_name_edit = QLineEdit()
        self.physio_practice_edit = QLineEdit()
        self.physio_phone_edit = QLineEdit()

        grid2.addWidget(QLabel("<b>Physiotherapist:</b>"), 6, 0, 1, 4)
        grid2.addWidget(QLabel("Name:"), 7, 0)
        grid2.addWidget(self.physio_name_edit, 7, 1)
        grid2.addWidget(QLabel("Practice / Phone:"), 7, 2)
        physio_sub = QHBoxLayout()
        physio_sub.addWidget(self.physio_practice_edit, 2)
        physio_sub.addWidget(self.physio_phone_edit, 2)
        grid2.addLayout(physio_sub, 7, 3)

        layout.addWidget(prac_box)

        # Functional Limitations
        limit_box = QGroupBox("Functional Limitations & Mobility")
        grid3 = QGridLayout(limit_box)
        grid3.setSpacing(8)

        self.walk_dist_edit = QLineEdit()
        self.walk_dist_edit.setPlaceholderText("meters")
        self.walking_aids_combo = QComboBox()
        self.walking_aids_combo.addItems(["(Not specified)", "Yes", "No"])

        self.current_aids_edit = QTextEdit()
        self.current_aids_edit.setPlaceholderText(
            "One aid per line, e.g.:\nRollator binnenshuis\nHandbewogen rolstoel")
        self.current_aids_edit.setMinimumHeight(55)

        self.transfer_ability_edit = QLineEdit()
        self.stair_climbing_edit = QLineEdit()

        grid3.addWidget(QLabel("Max Walking Distance (m):"), 0, 0)
        grid3.addWidget(self.walk_dist_edit, 0, 1)
        grid3.addWidget(QLabel("Requires Aids:"), 0, 2)
        grid3.addWidget(self.walking_aids_combo, 0, 3)

        grid3.addWidget(QLabel("Current Aids:"), 1, 0)
        grid3.addWidget(self.current_aids_edit, 1, 1, 1, 3)

        grid3.addWidget(QLabel("Transfer Ability:"), 2, 0)
        grid3.addWidget(self.transfer_ability_edit, 2, 1, 1, 3)

        grid3.addWidget(QLabel("Stair Climbing:"), 3, 0)
        grid3.addWidget(self.stair_climbing_edit, 3, 1, 1, 3)

        # Motor control
        self.fine_motor_edit = QLineEdit()
        self.gross_motor_edit = QLineEdit()
        self.typing_cap_edit = QLineEdit()
        self.mouse_nav_edit = QLineEdit()

        grid3.addWidget(QLabel("Fine Motor Control:"), 4, 0)
        grid3.addWidget(self.fine_motor_edit, 4, 1)
        grid3.addWidget(QLabel("Gross Motor Control:"), 4, 2)
        grid3.addWidget(self.gross_motor_edit, 4, 3)

        grid3.addWidget(QLabel("Typing Capacity:"), 5, 0)
        grid3.addWidget(self.typing_cap_edit, 5, 1)
        grid3.addWidget(QLabel("Mouse Navigation:"), 5, 2)
        grid3.addWidget(self.mouse_nav_edit, 5, 3)

        # Energy & Cognition
        self.cognitive_state_edit = QLineEdit()
        self.fatigue_level_edit = QLineEdit()
        self.max_sitting_edit = QLineEdit()
        self.max_sitting_edit.setPlaceholderText("minutes")

        grid3.addWidget(QLabel("Cognitive State:"), 6, 0)
        grid3.addWidget(self.cognitive_state_edit, 6, 1)
        grid3.addWidget(QLabel("Sitting Duration (min):"), 6, 2)
        grid3.addWidget(self.max_sitting_edit, 6, 3)

        grid3.addWidget(QLabel("Fatigue Level:"), 7, 0)
        grid3.addWidget(self.fatigue_level_edit, 7, 1, 1, 3)

        layout.addWidget(limit_box)
        layout.addStretch()
        return self._create_scroll_tab(layout)

    def _build_services_tab(self) -> QWidget:
        layout = QVBoxLayout()

        # WMO
        wmo_box = QGroupBox("WMO (Social Support Act) Application")
        wmo_lay = QVBoxLayout(wmo_box)
        wmo_grid = QGridLayout()

        self.wmo_municipality_edit = QLineEdit()
        wmo_grid.addWidget(QLabel("Target Municipality:"), 0, 0)
        wmo_grid.addWidget(self.wmo_municipality_edit, 0, 1)
        wmo_lay.addLayout(wmo_grid)

        fac_head = QHBoxLayout()
        fac_head.addWidget(
            QLabel("Requested Facilities (JSON array of type, category, motivation):"))
        fac_head.addStretch()
        add_wmo_btn = QPushButton("➕ Insert Facility Template")
        add_wmo_btn.clicked.connect(self._insert_wmo_template)
        fac_head.addWidget(add_wmo_btn)
        wmo_lay.addLayout(fac_head)

        self.wmo_facilities_edit = QTextEdit()
        self.wmo_facilities_edit.setFont(
            QFont("Consolas, Menlo, monospace", 9))
        self.wmo_facilities_edit.setMinimumHeight(80)
        wmo_lay.addWidget(self.wmo_facilities_edit)

        wmo_lay.addWidget(QLabel("Previous Allocations (JSON array):"))
        self.wmo_previous_edit = QTextEdit()
        self.wmo_previous_edit.setFont(QFont("Consolas, Menlo, monospace", 9))
        self.wmo_previous_edit.setMinimumHeight(60)
        wmo_lay.addWidget(self.wmo_previous_edit)

        layout.addWidget(wmo_box)

        # UWV WIA
        uwv_box = QGroupBox("UWV / WIA (Employment & Disability)")
        uwv_grid = QGridLayout(uwv_box)
        uwv_grid.setSpacing(8)

        self.uwv_company_edit = QLineEdit()
        self.uwv_kvk_edit = QLineEdit()
        self.uwv_emp_addr_edit = QLineEdit()
        self.uwv_emp_contact_edit = QLineEdit()
        self.uwv_emp_phone_edit = QLineEdit()
        self.uwv_emp_email_edit = QLineEdit()

        uwv_grid.addWidget(QLabel("Last Employer:"), 0, 0)
        uwv_grid.addWidget(self.uwv_company_edit, 0, 1)
        uwv_grid.addWidget(QLabel("KVK Number:"), 0, 2)
        uwv_grid.addWidget(self.uwv_kvk_edit, 0, 3)

        uwv_grid.addWidget(QLabel("Employer Address:"), 1, 0)
        uwv_grid.addWidget(self.uwv_emp_addr_edit, 1, 1)
        uwv_grid.addWidget(QLabel("HR Contact:"), 1, 2)
        uwv_grid.addWidget(self.uwv_emp_contact_edit, 1, 3)

        uwv_grid.addWidget(QLabel("Contact Phone:"), 2, 0)
        uwv_grid.addWidget(self.uwv_emp_phone_edit, 2, 1)
        uwv_grid.addWidget(QLabel("Contact Email:"), 2, 2)
        uwv_grid.addWidget(self.uwv_emp_email_edit, 2, 3)

        self.uwv_job_title_edit = QLineEdit()
        self.uwv_contract_edit = QLineEdit()
        self.uwv_hours_edit = QLineEdit()
        self.uwv_salary_edit = QLineEdit()

        uwv_grid.addWidget(QLabel("Job Title:"), 3, 0)
        uwv_grid.addWidget(self.uwv_job_title_edit, 3, 1)
        uwv_grid.addWidget(QLabel("Contract Type:"), 3, 2)
        uwv_grid.addWidget(self.uwv_contract_edit, 3, 3)

        uwv_grid.addWidget(QLabel("Hours / Week:"), 4, 0)
        uwv_grid.addWidget(self.uwv_hours_edit, 4, 1)
        uwv_grid.addWidget(QLabel("Gross Monthly (€):"), 4, 2)
        uwv_grid.addWidget(self.uwv_salary_edit, 4, 3)

        self.uwv_sick_start_edit = QLineEdit()
        self.uwv_sick_start_edit.setPlaceholderText("YYYY-MM-DD")
        self.uwv_sick_weeks_edit = QLineEdit()

        uwv_grid.addWidget(QLabel("1st Day Illness:"), 5, 0)
        uwv_grid.addWidget(self.uwv_sick_start_edit, 5, 1)
        uwv_grid.addWidget(QLabel("Weeks Ill:"), 5, 2)
        uwv_grid.addWidget(self.uwv_sick_weeks_edit, 5, 3)

        self.uwv_spoor1_edit = QLineEdit()
        self.uwv_spoor2_edit = QLineEdit()

        uwv_grid.addWidget(QLabel("Spoor 1 Result:"), 6, 0)
        uwv_grid.addWidget(self.uwv_spoor1_edit, 6, 1, 1, 3)
        uwv_grid.addWidget(QLabel("Spoor 2 Result:"), 7, 0)
        uwv_grid.addWidget(self.uwv_spoor2_edit, 7, 1, 1, 3)

        self.uwv_fml_day_edit = QLineEdit()
        self.uwv_fml_week_edit = QLineEdit()
        self.uwv_fml_conditions_edit = QLineEdit()

        uwv_grid.addWidget(QLabel("Limit (Hours/Day):"), 8, 0)
        uwv_grid.addWidget(self.uwv_fml_day_edit, 8, 1)
        uwv_grid.addWidget(QLabel("Limit (Hours/Wk):"), 8, 2)
        uwv_grid.addWidget(self.uwv_fml_week_edit, 8, 3)

        uwv_grid.addWidget(QLabel("Working Restrictions:"), 9, 0)
        uwv_grid.addWidget(self.uwv_fml_conditions_edit, 9, 1, 1, 3)

        layout.addWidget(uwv_box)

        # SVB PGB
        pgb_box = QGroupBox("SVB / PGB (Personal Health Budget)")
        pgb_lay = QVBoxLayout(pgb_box)
        pgb_grid = QGridLayout()
        pgb_grid.setSpacing(8)

        self.pgb_indication_edit = QLineEdit()
        self.pgb_basis_edit = QLineEdit()
        self.pgb_awarded_edit = QLineEdit()
        self.pgb_budget_edit = QLineEdit()
        self.pgb_start_edit = QLineEdit()
        self.pgb_end_edit = QLineEdit()

        pgb_grid.addWidget(QLabel("Indication Nr:"), 0, 0)
        pgb_grid.addWidget(self.pgb_indication_edit, 0, 1)
        pgb_grid.addWidget(QLabel("Basis (e.g. Wmo 2015):"), 0, 2)
        pgb_grid.addWidget(self.pgb_basis_edit, 0, 3)

        pgb_grid.addWidget(QLabel("Awarded By:"), 1, 0)
        pgb_grid.addWidget(self.pgb_awarded_edit, 1, 1)
        pgb_grid.addWidget(QLabel("Annual Budget (€):"), 1, 2)
        pgb_grid.addWidget(self.pgb_budget_edit, 1, 3)

        pgb_grid.addWidget(QLabel("Period Start:"), 2, 0)
        pgb_grid.addWidget(self.pgb_start_edit, 2, 1)
        pgb_grid.addWidget(QLabel("Period End:"), 2, 2)
        pgb_grid.addWidget(self.pgb_end_edit, 2, 3)

        pgb_lay.addLayout(pgb_grid)

        cg_head = QHBoxLayout()
        cg_head.addWidget(QLabel("Registered Caregivers (JSON Array):"))
        cg_head.addStretch()
        add_cg_btn = QPushButton("➕ Insert Caregiver Template")
        add_cg_btn.clicked.connect(self._insert_pgb_caregiver_template)
        cg_head.addWidget(add_cg_btn)
        pgb_lay.addLayout(cg_head)

        self.pgb_caregivers_edit = QTextEdit()
        self.pgb_caregivers_edit.setFont(
            QFont("Consolas, Menlo, monospace", 9))
        self.pgb_caregivers_edit.setMinimumHeight(80)
        pgb_lay.addWidget(self.pgb_caregivers_edit)

        pgb_lay.addWidget(
            QLabel("Monthly Declaration Template (JSON Object):"))
        self.pgb_declaration_edit = QTextEdit()
        self.pgb_declaration_edit.setFont(
            QFont("Consolas, Menlo, monospace", 9))
        self.pgb_declaration_edit.setMinimumHeight(60)
        pgb_lay.addWidget(self.pgb_declaration_edit)

        layout.addWidget(pgb_box)
        layout.addStretch()

        return self._create_scroll_tab(layout)

    def _build_json_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        tb_row = QHBoxLayout()
        fmt_btn = QPushButton("⚙ Format / Prettify JSON")
        fmt_btn.clicked.connect(self._format_json)
        tb_row.addWidget(fmt_btn)

        validate_btn = QPushButton("✓ Validate JSON")
        validate_btn.clicked.connect(self._validate_json)
        tb_row.addWidget(validate_btn)

        self.json_status_lbl = QLabel()
        self.json_status_lbl.setStyleSheet("font-size: 11px;")
        tb_row.addWidget(self.json_status_lbl)
        tb_row.addStretch()
        layout.addLayout(tb_row)

        self.json_edit = QTextEdit()
        self.json_edit.setFont(QFont("Consolas, Menlo, monospace", 10))
        self.json_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.json_edit, 1)

        return container

    def _sync_data_to_form(self):
        d = self.vault_data

        # Identity & Contact
        self.first_name_edit.setText(
            str(get_deep(d, ["personal_identity", "first_name"], "")))
        self.initials_edit.setText(
            str(get_deep(d, ["personal_identity", "initials"], "")))
        self.prefix_edit.setText(
            str(get_deep(d, ["personal_identity", "prefix"], "")))
        self.last_name_edit.setText(
            str(get_deep(d, ["personal_identity", "last_name"], "")))
        self.maiden_name_edit.setText(
            str(get_deep(d, ["personal_identity", "maiden_name"], "")))
        self.bsn_edit.setText(
            str(get_deep(d, ["personal_identity", "bsn"], "")))
        self.dob_edit.setText(
            str(get_deep(d, ["personal_identity", "date_of_birth"], "")))
        self.pob_edit.setText(
            str(get_deep(d, ["personal_identity", "place_of_birth"], "")))
        self.gender_edit.setText(
            str(get_deep(d, ["personal_identity", "gender"], "")))
        self.nationality_edit.setText(
            str(get_deep(d, ["personal_identity", "nationality"], "")))
        self.marital_edit.setText(
            str(get_deep(d, ["personal_identity", "marital_status"], "")))

        self.email_edit.setText(
            str(get_deep(d, ["personal_identity", "contact", "email"], "")))
        self.phone_mobile_edit.setText(
            str(get_deep(d, ["personal_identity", "contact", "phone_mobile"], "")))
        self.phone_home_edit.setText(
            str(get_deep(d, ["personal_identity", "contact", "phone_home"], "")))

        self.street_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "street"], "")))
        self.house_no_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "house_number"], "")))
        self.house_ext_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "house_number_extension"], "")))
        self.postal_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "postal_code"], "")))
        self.city_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "city"], "")))
        self.municipality_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "municipality"], "")))
        self.country_edit.setText(
            str(get_deep(d, ["personal_identity", "address", "country"], "")))

        self.bank_holder_edit.setText(
            str(get_deep(d, ["personal_identity", "bank_account", "account_holder"], "")))
        self.iban_edit.setText(
            str(get_deep(d, ["personal_identity", "bank_account", "iban"], "")))
        self.bic_edit.setText(
            str(get_deep(d, ["personal_identity", "bank_account", "bic"], "")))

        # Living
        self.housing_type_edit.setText(
            str(get_deep(d, ["living_situation", "housing_type"], "")))
        self.landlord_type_edit.setText(
            str(get_deep(d, ["living_situation", "landlord_type"], "")))
        self.landlord_name_edit.setText(
            str(get_deep(d, ["living_situation", "landlord_name"], "")))
        self.floor_level_edit.setText(
            str(get_deep(d, ["living_situation", "floor_level"], "")))
        self.doorstep_cm_edit.setText(
            str(get_deep(d, ["living_situation", "doorstep_barrier_cm"], "")))

        elev = get_deep(d, ["living_situation", "elevator_present"], None)
        if elev is True:
            self.elevator_combo.setCurrentText("Yes")
        elif elev is False:
            self.elevator_combo.setCurrentText("No")
        else:
            self.elevator_combo.setCurrentText("(Not specified)")

        self.caregiver_name_edit.setText(
            str(get_deep(d, ["living_situation", "informal_care", "caregiver_name"], "")))
        self.caregiver_rel_edit.setText(
            str(get_deep(d, ["living_situation", "informal_care", "relation"], "")))
        self.caregiver_hours_edit.setText(
            str(get_deep(d, ["living_situation", "informal_care", "hours_per_week"], "")))
        self.caregiver_burden_edit.setText(
            str(get_deep(d, ["living_situation", "informal_care", "burden_level"], "")))

        tasks = get_deep(
            d, ["living_situation", "informal_care", "tasks_performed"], [])
        if isinstance(tasks, list):
            self.caregiver_tasks_edit.setPlainText(
                "\n".join(str(t) for t in tasks))
        elif tasks:
            self.caregiver_tasks_edit.setPlainText(str(tasks))
        else:
            self.caregiver_tasks_edit.clear()

        members = get_deep(d, ["living_situation", "household_members"], None)
        if members:
            self.household_members_edit.setPlainText(
                json.dumps(members, indent=2, ensure_ascii=False) if not isinstance(
                    members, str) else members
            )
        else:
            self.household_members_edit.clear()

        # Medical
        self.med_diagnosis_edit.setText(
            str(get_deep(d, ["medical_profile", "primary_diagnosis"], "")))
        self.med_icd10_edit.setText(
            str(get_deep(d, ["medical_profile", "icd_10_code"], "")))
        self.med_diag_year_edit.setText(
            str(get_deep(d, ["medical_profile", "diagnosis_year"], "")))
        self.med_prognosis_edit.setText(
            str(get_deep(d, ["medical_profile", "prognosis"], "")))

        self.gp_name_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "general_practitioner", "name"], "")))
        self.gp_practice_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "general_practitioner", "practice_name"], "")))
        self.gp_addr_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "general_practitioner", "address"], "")))
        self.gp_phone_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "general_practitioner", "phone"], "")))
        self.gp_big_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "general_practitioner", "big_number"], "")))

        self.neuro_name_edit.setText(
            str(get_deep(d, ["medical_profile", "practitioners", "neurologist", "name"], "")))
        self.neuro_hosp_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "neurologist", "hospital"], "")))
        self.neuro_dept_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "neurologist", "department"], "")))
        self.neuro_big_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "neurologist", "big_number"], "")))

        self.physio_name_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "physiotherapist", "name"], "")))
        self.physio_practice_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "physiotherapist", "practice_name"], "")))
        self.physio_phone_edit.setText(str(get_deep(
            d, ["medical_profile", "practitioners", "physiotherapist", "phone"], "")))

        self.walk_dist_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "mobility", "max_walking_distance_meters"], "")))
        waids = get_deep(d, ["medical_profile", "functional_limitations",
                         "mobility", "requires_walking_aids"], None)
        if waids is True:
            self.walking_aids_combo.setCurrentText("Yes")
        elif waids is False:
            self.walking_aids_combo.setCurrentText("No")
        else:
            self.walking_aids_combo.setCurrentText("(Not specified)")

        aids = get_deep(
            d, ["medical_profile", "functional_limitations", "mobility", "current_aids"], [])
        if isinstance(aids, list):
            self.current_aids_edit.setPlainText(
                "\n".join(str(a) for a in aids))
        elif aids:
            self.current_aids_edit.setPlainText(str(aids))
        else:
            self.current_aids_edit.clear()

        self.transfer_ability_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "mobility", "transfer_ability"], "")))
        self.stair_climbing_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "mobility", "stair_climbing"], "")))

        self.fine_motor_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "upper_extremities", "fine_motor_control"], "")))
        self.gross_motor_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "upper_extremities", "gross_motor_control"], "")))
        self.typing_cap_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "upper_extremities", "typing_capacity"], "")))
        self.mouse_nav_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "upper_extremities", "mouse_navigation"], "")))

        self.cognitive_state_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "energy_and_cognition", "cognitive_state"], "")))
        self.fatigue_level_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "energy_and_cognition", "fatigue_level"], "")))
        self.max_sitting_edit.setText(str(get_deep(
            d, ["medical_profile", "functional_limitations", "energy_and_cognition", "max_sitting_duration_minutes"], "")))

        # Services / Provisions
        self.wmo_municipality_edit.setText(
            str(get_deep(d, ["wmo_application_data", "target_municipality"], "")))
        wmo_fac = get_deep(
            d, ["wmo_application_data", "requested_facilities"], None)
        if wmo_fac:
            self.wmo_facilities_edit.setPlainText(
                json.dumps(wmo_fac, indent=2, ensure_ascii=False) if not isinstance(
                    wmo_fac, str) else wmo_fac
            )
        else:
            self.wmo_facilities_edit.clear()

        wmo_prev = get_deep(
            d, ["wmo_application_data", "previous_wmo_allocations"], None)
        if wmo_prev:
            self.wmo_previous_edit.setPlainText(
                json.dumps(wmo_prev, indent=2, ensure_ascii=False) if not isinstance(
                    wmo_prev, str) else wmo_prev
            )
        else:
            self.wmo_previous_edit.clear()

        # UWV
        self.uwv_company_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "company_name"], "")))
        self.uwv_kvk_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "kvk_number"], "")))
        self.uwv_emp_addr_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "address"], "")))
        self.uwv_emp_contact_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "contact_person"], "")))
        self.uwv_emp_phone_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "contact_phone"], "")))
        self.uwv_emp_email_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "last_employer", "contact_email"], "")))

        self.uwv_job_title_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "job_title"], "")))
        self.uwv_contract_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "contract_type"], "")))
        self.uwv_hours_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "contracted_hours_per_week"], "")))
        self.uwv_salary_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "employment_history", "gross_monthly_salary_eur"], "")))

        self.uwv_sick_start_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "sick_leave_timeline", "first_day_of_illness"], "")))
        self.uwv_sick_weeks_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "sick_leave_timeline", "current_sick_leave_duration_weeks"], "")))
        self.uwv_spoor1_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "sick_leave_timeline", "reintegration_efforts", "spoor_1_result"], "")))
        self.uwv_spoor2_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "sick_leave_timeline", "reintegration_efforts", "spoor_2_result"], "")))

        self.uwv_fml_day_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "functional_limitations_fml_summary", "energetic_limitation_hours_per_day"], "")))
        self.uwv_fml_week_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "functional_limitations_fml_summary", "energetic_limitation_hours_per_week"], "")))
        self.uwv_fml_conditions_edit.setText(str(get_deep(
            d, ["uwv_wia_application_data", "functional_limitations_fml_summary", "working_conditions"], "")))

        # PGB
        self.pgb_indication_edit.setText(
            str(get_deep(d, ["svb_pgb_data", "pgb_indication", "indication_number"], "")))
        self.pgb_basis_edit.setText(
            str(get_deep(d, ["svb_pgb_data", "pgb_indication", "statutory_basis"], "")))
        self.pgb_awarded_edit.setText(
            str(get_deep(d, ["svb_pgb_data", "pgb_indication", "awarded_by"], "")))
        self.pgb_budget_edit.setText(str(get_deep(
            d, ["svb_pgb_data", "pgb_indication", "total_annual_budget_eur"], "")))
        self.pgb_start_edit.setText(
            str(get_deep(d, ["svb_pgb_data", "pgb_indication", "budget_period_start"], "")))
        self.pgb_end_edit.setText(
            str(get_deep(d, ["svb_pgb_data", "pgb_indication", "budget_period_end"], "")))

        cg = get_deep(d, ["svb_pgb_data", "registered_caregivers"], None)
        if cg:
            self.pgb_caregivers_edit.setPlainText(
                json.dumps(cg, indent=2, ensure_ascii=False) if not isinstance(
                    cg, str) else cg
            )
        else:
            self.pgb_caregivers_edit.clear()

        decl = get_deep(
            d, ["svb_pgb_data", "monthly_declaration_template"], None)
        if decl:
            self.pgb_declaration_edit.setPlainText(
                json.dumps(decl, indent=2, ensure_ascii=False) if not isinstance(
                    decl, str) else decl
            )
        else:
            self.pgb_declaration_edit.clear()

        # Update JSON tab as well
        self.json_edit.setPlainText(
            json.dumps(self.vault_data, indent=2,
                       ensure_ascii=False) if self.vault_data else "{}"
        )

    def _sync_form_to_data(self):
        d = copy.deepcopy(self.vault_data)

        def set_val(path: list, val):
            if val is None or val == "" or val == [] or val == {}:
                curr = d
                for k in path[:-1]:
                    if not isinstance(curr, dict) or k not in curr:
                        return
                    curr = curr[k]
                if isinstance(curr, dict) and path[-1] in curr:
                    del curr[path[-1]]
                return

            curr = d
            for k in path[:-1]:
                if k not in curr or not isinstance(curr[k], dict):
                    curr[k] = {}
                curr = curr[k]
            curr[path[-1]] = val

        # Identity & Contact
        set_val(["personal_identity", "first_name"],
                self.first_name_edit.text().strip())
        set_val(["personal_identity", "initials"],
                self.initials_edit.text().strip())
        set_val(["personal_identity", "prefix"],
                self.prefix_edit.text().strip())
        set_val(["personal_identity", "last_name"],
                self.last_name_edit.text().strip())
        set_val(["personal_identity", "maiden_name"],
                self.maiden_name_edit.text().strip())
        set_val(["personal_identity", "bsn"], self.bsn_edit.text().strip())
        set_val(["personal_identity", "date_of_birth"],
                self.dob_edit.text().strip())
        set_val(["personal_identity", "place_of_birth"],
                self.pob_edit.text().strip())
        set_val(["personal_identity", "gender"],
                self.gender_edit.text().strip())
        set_val(["personal_identity", "nationality"],
                self.nationality_edit.text().strip())
        set_val(["personal_identity", "marital_status"],
                self.marital_edit.text().strip())

        set_val(["personal_identity", "contact", "email"],
                self.email_edit.text().strip())
        set_val(["personal_identity", "contact", "phone_mobile"],
                self.phone_mobile_edit.text().strip())
        set_val(["personal_identity", "contact", "phone_home"],
                self.phone_home_edit.text().strip())

        set_val(["personal_identity", "address", "street"],
                self.street_edit.text().strip())
        set_val(["personal_identity", "address", "house_number"],
                self.house_no_edit.text().strip())
        set_val(["personal_identity", "address", "house_number_extension"],
                self.house_ext_edit.text().strip())
        set_val(["personal_identity", "address", "postal_code"],
                self.postal_edit.text().strip())
        set_val(["personal_identity", "address", "city"],
                self.city_edit.text().strip())
        set_val(["personal_identity", "address", "municipality"],
                self.municipality_edit.text().strip())
        set_val(["personal_identity", "address", "country"],
                self.country_edit.text().strip())

        set_val(["personal_identity", "bank_account", "account_holder"],
                self.bank_holder_edit.text().strip())
        set_val(["personal_identity", "bank_account", "iban"],
                self.iban_edit.text().strip())
        set_val(["personal_identity", "bank_account", "bic"],
                self.bic_edit.text().strip())

        # Living
        set_val(["living_situation", "housing_type"],
                self.housing_type_edit.text().strip())
        set_val(["living_situation", "landlord_type"],
                self.landlord_type_edit.text().strip())
        set_val(["living_situation", "landlord_name"],
                self.landlord_name_edit.text().strip())
        set_val(["living_situation", "floor_level"],
                parse_num_or_str(self.floor_level_edit.text()))
        set_val(["living_situation", "doorstep_barrier_cm"],
                parse_num_or_str(self.doorstep_cm_edit.text()))

        elev = self.elevator_combo.currentText()
        if elev == "Yes":
            set_val(["living_situation", "elevator_present"], True)
        elif elev == "No":
            set_val(["living_situation", "elevator_present"], False)
        else:
            set_val(["living_situation", "elevator_present"], None)

        set_val(["living_situation", "informal_care", "caregiver_name"],
                self.caregiver_name_edit.text().strip())
        set_val(["living_situation", "informal_care", "relation"],
                self.caregiver_rel_edit.text().strip())
        set_val(["living_situation", "informal_care", "hours_per_week"],
                parse_num_or_str(self.caregiver_hours_edit.text()))
        set_val(["living_situation", "informal_care", "burden_level"],
                self.caregiver_burden_edit.text().strip())

        care_tasks = [t.strip() for t in self.caregiver_tasks_edit.toPlainText(
        ).splitlines() if t.strip()]
        set_val(["living_situation", "informal_care",
                "tasks_performed"], care_tasks)

        set_val(["living_situation", "household_members"],
                parse_json_or_raw(self.household_members_edit.toPlainText()))

        # Medical
        set_val(["medical_profile", "primary_diagnosis"],
                self.med_diagnosis_edit.text().strip())
        set_val(["medical_profile", "icd_10_code"],
                self.med_icd10_edit.text().strip())
        set_val(["medical_profile", "diagnosis_year"],
                parse_num_or_str(self.med_diag_year_edit.text()))
        set_val(["medical_profile", "prognosis"],
                self.med_prognosis_edit.text().strip())

        set_val(["medical_profile", "practitioners", "general_practitioner",
                "name"], self.gp_name_edit.text().strip())
        set_val(["medical_profile", "practitioners", "general_practitioner",
                "practice_name"], self.gp_practice_edit.text().strip())
        set_val(["medical_profile", "practitioners", "general_practitioner",
                "address"], self.gp_addr_edit.text().strip())
        set_val(["medical_profile", "practitioners", "general_practitioner",
                "phone"], self.gp_phone_edit.text().strip())
        set_val(["medical_profile", "practitioners", "general_practitioner",
                "big_number"], self.gp_big_edit.text().strip())

        set_val(["medical_profile", "practitioners", "neurologist",
                "name"], self.neuro_name_edit.text().strip())
        set_val(["medical_profile", "practitioners", "neurologist",
                "hospital"], self.neuro_hosp_edit.text().strip())
        set_val(["medical_profile", "practitioners", "neurologist",
                "department"], self.neuro_dept_edit.text().strip())
        set_val(["medical_profile", "practitioners", "neurologist",
                "big_number"], self.neuro_big_edit.text().strip())

        set_val(["medical_profile", "practitioners", "physiotherapist",
                "name"], self.physio_name_edit.text().strip())
        set_val(["medical_profile", "practitioners", "physiotherapist",
                "practice_name"], self.physio_practice_edit.text().strip())
        set_val(["medical_profile", "practitioners", "physiotherapist",
                "phone"], self.physio_phone_edit.text().strip())

        set_val(["medical_profile", "functional_limitations", "mobility",
                "max_walking_distance_meters"], parse_num_or_str(self.walk_dist_edit.text()))

        waids = self.walking_aids_combo.currentText()
        if waids == "Yes":
            set_val(["medical_profile", "functional_limitations",
                    "mobility", "requires_walking_aids"], True)
        elif waids == "No":
            set_val(["medical_profile", "functional_limitations",
                    "mobility", "requires_walking_aids"], False)
        else:
            set_val(["medical_profile", "functional_limitations",
                    "mobility", "requires_walking_aids"], None)

        cur_aids = [a.strip() for a in self.current_aids_edit.toPlainText(
        ).splitlines() if a.strip()]
        set_val(["medical_profile", "functional_limitations",
                "mobility", "current_aids"], cur_aids)

        set_val(["medical_profile", "functional_limitations", "mobility",
                "transfer_ability"], self.transfer_ability_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "mobility",
                "stair_climbing"], self.stair_climbing_edit.text().strip())

        set_val(["medical_profile", "functional_limitations", "upper_extremities",
                "fine_motor_control"], self.fine_motor_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "upper_extremities",
                "gross_motor_control"], self.gross_motor_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "upper_extremities",
                "typing_capacity"], self.typing_cap_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "upper_extremities",
                "mouse_navigation"], self.mouse_nav_edit.text().strip())

        set_val(["medical_profile", "functional_limitations", "energy_and_cognition",
                "cognitive_state"], self.cognitive_state_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "energy_and_cognition",
                "fatigue_level"], self.fatigue_level_edit.text().strip())
        set_val(["medical_profile", "functional_limitations", "energy_and_cognition",
                "max_sitting_duration_minutes"], parse_num_or_str(self.max_sitting_edit.text()))

        # Services
        set_val(["wmo_application_data", "target_municipality"],
                self.wmo_municipality_edit.text().strip())
        set_val(["wmo_application_data", "requested_facilities"],
                parse_json_or_raw(self.wmo_facilities_edit.toPlainText()))
        set_val(["wmo_application_data", "previous_wmo_allocations"],
                parse_json_or_raw(self.wmo_previous_edit.toPlainText()))

        set_val(["uwv_wia_application_data", "employment_history",
                "last_employer", "company_name"], self.uwv_company_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history",
                "last_employer", "kvk_number"], self.uwv_kvk_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history",
                "last_employer", "address"], self.uwv_emp_addr_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history", "last_employer",
                "contact_person"], self.uwv_emp_contact_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history", "last_employer",
                "contact_phone"], self.uwv_emp_phone_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history", "last_employer",
                "contact_email"], self.uwv_emp_email_edit.text().strip())

        set_val(["uwv_wia_application_data", "employment_history",
                "job_title"], self.uwv_job_title_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history",
                "contract_type"], self.uwv_contract_edit.text().strip())
        set_val(["uwv_wia_application_data", "employment_history",
                "contracted_hours_per_week"], parse_num_or_str(self.uwv_hours_edit.text()))
        set_val(["uwv_wia_application_data", "employment_history",
                "gross_monthly_salary_eur"], parse_num_or_str(self.uwv_salary_edit.text()))

        set_val(["uwv_wia_application_data", "sick_leave_timeline",
                "first_day_of_illness"], self.uwv_sick_start_edit.text().strip())
        set_val(["uwv_wia_application_data", "sick_leave_timeline",
                "current_sick_leave_duration_weeks"], parse_num_or_str(self.uwv_sick_weeks_edit.text()))
        set_val(["uwv_wia_application_data", "sick_leave_timeline",
                "reintegration_efforts", "spoor_1_result"], self.uwv_spoor1_edit.text().strip())
        set_val(["uwv_wia_application_data", "sick_leave_timeline",
                "reintegration_efforts", "spoor_2_result"], self.uwv_spoor2_edit.text().strip())

        set_val(["uwv_wia_application_data", "functional_limitations_fml_summary",
                "energetic_limitation_hours_per_day"], parse_num_or_str(self.uwv_fml_day_edit.text()))
        set_val(["uwv_wia_application_data", "functional_limitations_fml_summary",
                "energetic_limitation_hours_per_week"], parse_num_or_str(self.uwv_fml_week_edit.text()))
        set_val(["uwv_wia_application_data", "functional_limitations_fml_summary",
                "working_conditions"], self.uwv_fml_conditions_edit.text().strip())

        set_val(["svb_pgb_data", "pgb_indication", "indication_number"],
                self.pgb_indication_edit.text().strip())
        set_val(["svb_pgb_data", "pgb_indication", "statutory_basis"],
                self.pgb_basis_edit.text().strip())
        set_val(["svb_pgb_data", "pgb_indication", "awarded_by"],
                self.pgb_awarded_edit.text().strip())
        set_val(["svb_pgb_data", "pgb_indication", "total_annual_budget_eur"],
                parse_num_or_str(self.pgb_budget_edit.text()))
        set_val(["svb_pgb_data", "pgb_indication", "budget_period_start"],
                self.pgb_start_edit.text().strip())
        set_val(["svb_pgb_data", "pgb_indication", "budget_period_end"],
                self.pgb_end_edit.text().strip())

        set_val(["svb_pgb_data", "registered_caregivers"],
                parse_json_or_raw(self.pgb_caregivers_edit.toPlainText()))
        set_val(["svb_pgb_data", "monthly_declaration_template"],
                parse_json_or_raw(self.pgb_declaration_edit.toPlainText()))

        self.vault_data = prune_empty(d)

    def _on_tab_changed(self, new_index: int):
        prev = self._previous_tab_index
        if prev == 4 and new_index != 4:
            # Switching from JSON tab to Form Tab: Parse JSON
            raw_text = self.json_edit.toPlainText().strip()
            if raw_text:
                try:
                    parsed = json.loads(raw_text)
                    if not isinstance(parsed, dict):
                        raise ValueError("Root JSON must be a dictionary.")
                    self.vault_data = parsed
                    self._sync_data_to_form()
                    self.json_status_lbl.setText("✓ In sync with form tabs")
                    self.json_status_lbl.setStyleSheet(
                        "color: #7bd88f; font-size: 11px;")
                except Exception as e:
                    QMessageBox.warning(
                        self, "Invalid JSON",
                        f"Please fix the JSON syntax before switching tabs:\n\n{e}"
                    )
                    self.tabs.blockSignals(True)
                    self.tabs.setCurrentIndex(4)
                    self.tabs.blockSignals(False)
                    return
            else:
                self.vault_data = {}
                self._sync_data_to_form()
        elif prev != 4 and new_index == 4:
            # Switching from Form to JSON Tab: Update JSON view
            self._sync_form_to_data()
            self.json_edit.setPlainText(
                json.dumps(self.vault_data, indent=2,
                           ensure_ascii=False) if self.vault_data else "{}"
            )
            self.json_status_lbl.setText("✓ In sync with form tabs")
            self.json_status_lbl.setStyleSheet(
                "color: #7bd88f; font-size: 11px;")

        self._previous_tab_index = new_index

    def _format_json(self):
        raw = self.json_edit.toPlainText().strip()
        if not raw:
            self.json_edit.setPlainText("{}")
            return
        try:
            parsed = json.loads(raw)
            self.json_edit.setPlainText(json.dumps(
                parsed, indent=2, ensure_ascii=False))
            self.json_status_lbl.setText("✓ JSON formatted successfully")
            self.json_status_lbl.setStyleSheet(
                "color: #7bd88f; font-size: 11px;")
        except Exception as e:
            self.json_status_lbl.setText(f"❌ Syntax Error: {e}")
            self.json_status_lbl.setStyleSheet(
                "color: #ff6b6b; font-size: 11px;")

    def _validate_json(self):
        raw = self.json_edit.toPlainText().strip()
        if not raw:
            self.json_status_lbl.setText("✓ Empty document is valid")
            self.json_status_lbl.setStyleSheet(
                "color: #7bd88f; font-size: 11px;")
            return
        try:
            parsed = json.loads(raw)
            keys_count = len(parsed) if isinstance(parsed, dict) else len(
                parsed) if isinstance(parsed, list) else 0
            self.json_status_lbl.setText(
                f"✓ Valid JSON ({keys_count} top-level items)")
            self.json_status_lbl.setStyleSheet(
                "color: #7bd88f; font-size: 11px;")
        except Exception as e:
            self.json_status_lbl.setText(f"❌ Error: {e}")
            self.json_status_lbl.setStyleSheet(
                "color: #ff6b6b; font-size: 11px;")

    def _on_load_example(self):
        res = QMessageBox.question(
            self, "Load Example Template",
            "Replace current dialog values with the complete example profile (Marloes van den Berg)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            self.vault_data = copy.deepcopy(EXAMPLE_VAULT)
            self._sync_data_to_form()
            self.status_bar_lbl.setText(
                "✓ Example template loaded successfully.")
            self.status_bar_lbl.setStyleSheet("color: #7bd88f;")

    def _on_clear_all(self):
        res = QMessageBox.question(
            self, "Clear Data",
            "Are you sure you want to clear all fields in the dialog?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            self.vault_data = {}
            self._sync_data_to_form()
            self.status_bar_lbl.setText("✓ All fields cleared.")
            self.status_bar_lbl.setStyleSheet("color: #ffcb6b;")

    def _on_import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Vault JSON", "", "JSON files (*.json);;All files (*)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(
                        "Imported JSON must contain a root object/dictionary.")
                self.vault_data = data
                self._sync_data_to_form()
                self.status_bar_lbl.setText(
                    f"✓ Imported data from {os.path.basename(path)}")
                self.status_bar_lbl.setStyleSheet("color: #7bd88f;")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed",
                                     f"Could not read JSON file:\n{e}")

    def _on_export_file(self):
        if self.tabs.currentIndex() == 4:
            self._on_tab_changed(0)
        else:
            self._sync_form_to_data()

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Vault JSON", "vault.json", "JSON files (*.json);;All files (*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.vault_data, f, indent=2, ensure_ascii=False)
                self.status_bar_lbl.setText(
                    f"✓ Exported to {os.path.basename(path)}")
                self.status_bar_lbl.setStyleSheet("color: #7bd88f;")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed",
                                     f"Could not save JSON file:\n{e}")

    def _insert_household_partner_template(self):
        template = [
            {
                "relation": "partner",
                "first_name": "Jeroen",
                "last_name": "van den Berg",
                "date_of_birth": "1974-03-22",
                "bsn": "999999991",
                "employment_status": "full-time werkend"
            }
        ]
        self.household_members_edit.setPlainText(
            json.dumps(template, indent=2, ensure_ascii=False))

    def _insert_wmo_template(self):
        template = [
            {
                "type": "Elektrische rolstoel voor buiten- en binnengebruik",
                "category": "Mobiliteitshulpmiddelen",
                "motivation": "Aanvrager heeft minder dan 10 meter loopafstand. Handbewogen rolstoel kan niet zelfstandig worden aangedreven."
            }
        ]
        self.wmo_facilities_edit.setPlainText(
            json.dumps(template, indent=2, ensure_ascii=False))

    def _insert_pgb_caregiver_template(self):
        template = [
            {
                "caregiver_id": "CRG-001",
                "type": "ZZP / Professionele zorgverlener",
                "company_name": "Zorgpraktijk Haaglanden",
                "kvk_number": "27987654",
                "bsn": "999999992",
                "first_name": "Fatima",
                "last_name": "El Amrani",
                "iban": "NL44RABO0123987654",
                "hourly_rate_eur": 45.00,
                "service_type": "Persoonlijke verzorging"
            }
        ]
        self.pgb_caregivers_edit.setPlainText(
            json.dumps(template, indent=2, ensure_ascii=False))

    def _on_save(self):
        if self.tabs.currentIndex() == 4:
            raw = self.json_edit.toPlainText().strip()
            if raw:
                try:
                    parsed = json.loads(raw)
                    if not isinstance(parsed, dict):
                        raise ValueError(
                            "Root JSON must be an object/dictionary.")
                    self.vault_data = parsed
                except Exception as e:
                    QMessageBox.critical(
                        self, "Invalid JSON", f"Cannot save syntax errors:\n\n{e}")
                    return
            else:
                self.vault_data = {}
        else:
            self._sync_form_to_data()

        try:
            save_vault(self.vault_data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error",
                                 f"Failed to save vault file:\n{e}")
