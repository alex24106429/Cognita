import json
import os
import urllib.request
import urllib.error
from openai import OpenAI
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QComboBox, QStackedWidget,
    QFrame, QApplication
)

try:
    import PyQt6.QtSvg  # noqa: F401 - ensures Qt SVG plugin is loaded
except ImportError:
    pass

from config import PROVIDERS


def is_api_configured() -> bool:
    settings = QSettings("cognita", "gui")
    provider = settings.value("provider", "")
    base_url = settings.value("base_url", "")
    model = settings.value("model", "")
    api_key = settings.value("api_key", "")

    if not provider or not base_url or not model:
        return False
    if provider != "Local" and not api_key:
        return False
    return True


def verify_api_connection(provider: str, base_url: str, api_key: str) -> tuple[bool, str]:
    base_url = base_url.strip()
    api_key = api_key.strip()

    if provider != "Local" and not api_key:
        return False, "API key cannot be empty for this provider."

    # Anthropic direct API check
    if provider == "Anthropic" or "api.anthropic.com" in base_url:
        url = base_url.rstrip("/")
        test_url = f"{url}/models" if not url.endswith("/models") else url
        req = urllib.request.Request(
            test_url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "User-Agent": "Cognita-Agent",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    return True, "Anthropic API connection verified successfully."
                return False, f"Unexpected response status: {resp.status}"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                msg = json.loads(body).get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)
            return False, f"Authentication error ({e.code}): {msg}"
        except Exception as e:
            return False, f"Connection failed: {e}"

    # OpenAI-compatible check (OpenRouter, OpenAI, Gemini, DeepSeek, Local)
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key or "local-dummy-key",
            timeout=10.0,
            max_retries=0,
        )
        client.models.list()
        return True, "API connection verified successfully."
    except Exception as e:
        err_msg = str(e)
        if "Connection refused" in err_msg:
            return False, f"Connection refused. Ensure your server is running at {base_url}."
        if "401" in err_msg or "Unauthorized" in err_msg:
            return False, "Authentication failed (401 Unauthorized): Invalid API key."
        if "403" in err_msg or "Forbidden" in err_msg:
            return False, "Access forbidden (403 Forbidden): Check your key permissions."
        return False, f"Connection test failed: {err_msg}"


class ApiSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cognita — API Setup")
        self.resize(580, 440)
        self.setModal(True)

        self.settings = QSettings("cognita", "gui")
        self.selected_provider = self.settings.value("provider", "")
        self.verified_base_url = ""
        self.verified_api_key = ""

        self._build_ui()
        self._load_initial_values()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(15)

        self.header_title = QLabel()
        self.header_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #9aa4ff;")
        self.header_desc = QLabel()
        self.header_desc.setStyleSheet("color: #9aa0b4; font-size: 12px;")
        root.addWidget(self.header_title)
        root.addWidget(self.header_desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #34363f;")
        root.addWidget(sep)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self._build_provider_page()
        self._build_credentials_page()
        self._build_model_page()

        self._update_header(0)

    def _build_provider_page(self):
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(10)

        provider_names = ["OpenRouter", "OpenAI",
                          "Gemini", "Anthropic", "DeepSeek", "Local"]
        for idx, name in enumerate(provider_names):
            cfg = PROVIDERS.get(name, {})
            btn = QPushButton()
            btn.setObjectName("providerSelectBtn")
            btn.setMinimumHeight(64)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(12, 8, 12, 8)
            btn_layout.setSpacing(12)

            icon_lbl = QLabel()
            icon_lbl.setFixedSize(36, 36)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("background: transparent;")
            icon_lbl.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            icon_path = cfg.get("icon", "")
            if icon_path and os.path.exists(icon_path):
                icon_lbl.setPixmap(QIcon(icon_path).pixmap(32, 32))
            btn_layout.addWidget(icon_lbl)

            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)

            title_lbl = QLabel(f"<b>{name}</b>")
            title_lbl.setStyleSheet(
                "background: transparent; font-size: 13px; color: #e6e6e6;")
            title_lbl.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            desc_lbl = QLabel(cfg.get("description", ""))
            desc_lbl.setStyleSheet(
                "background: transparent; font-size: 10px; color: #8e92a4;")
            desc_lbl.setWordWrap(True)
            desc_lbl.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            text_layout.addWidget(title_lbl)
            text_layout.addWidget(desc_lbl)
            btn_layout.addLayout(text_layout, 1)

            btn.clicked.connect(
                lambda checked, p=name: self._on_provider_selected(p))
            row, col = divmod(idx, 2)
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        layout.addStretch()
        self.stack.addWidget(page)

    def _build_credentials_page(self):
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(10)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)

        self.provider_icon_lbl = QLabel()
        self.provider_icon_lbl.setFixedSize(24, 24)
        self.provider_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.provider_icon_lbl.setStyleSheet("background: transparent;")
        badge_row.addWidget(self.provider_icon_lbl)

        self.provider_badge = QLabel()
        self.provider_badge.setStyleSheet(
            "color: #7bd88f; font-weight: 600; font-size: 13px;")
        badge_row.addWidget(self.provider_badge)
        badge_row.addStretch()
        layout.addLayout(badge_row)

        layout.addWidget(QLabel("Base URL / Endpoint:"))
        self.url_edit = QLineEdit()
        layout.addWidget(self.url_edit)

        layout.addWidget(QLabel("API Key:"))
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_edit)

        show_key_cb = QCheckBox("Show API key")
        show_key_cb.toggled.connect(
            lambda on: self.key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password
            )
        )
        layout.addWidget(show_key_cb)

        self.status_lbl = QLabel()
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.status_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("◀ Back")
        back_btn.clicked.connect(lambda: self._go_to_step(0))
        btn_row.addWidget(back_btn)
        btn_row.addStretch()

        self.verify_btn = QPushButton("Connect ▶")
        self.verify_btn.setObjectName("startBtn")
        self.verify_btn.clicked.connect(self._on_verify_credentials)
        btn_row.addWidget(self.verify_btn)

        layout.addLayout(btn_row)
        self.stack.addWidget(page)

    def _build_model_page(self):
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(12)

        verified_row = QHBoxLayout()
        verified_row.setSpacing(8)

        self.model_provider_icon_lbl = QLabel()
        self.model_provider_icon_lbl.setFixedSize(24, 24)
        self.model_provider_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_provider_icon_lbl.setStyleSheet("background: transparent;")
        verified_row.addWidget(self.model_provider_icon_lbl)

        verified_banner = QLabel("✓ Connection verified successfully!")
        verified_banner.setStyleSheet(
            "color: #7bd88f; font-weight: 700; font-size: 13px;")
        verified_row.addWidget(verified_banner)
        verified_row.addStretch()
        layout.addLayout(verified_row)

        layout.addWidget(QLabel("Select Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setMinimumHeight(32)
        layout.addWidget(self.model_combo)

        hint = QLabel(
            "Select from the list above or enter a custom model name.")
        hint.setStyleSheet("font-size: 11px; color: #8e92a4;")
        layout.addWidget(hint)

        layout.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("◀ Back")
        back_btn.clicked.connect(lambda: self._go_to_step(1))
        btn_row.addWidget(back_btn)
        btn_row.addStretch()

        finish_btn = QPushButton("Finish")
        finish_btn.setObjectName("startBtn")
        finish_btn.clicked.connect(self._on_finish_setup)
        btn_row.addWidget(finish_btn)

        layout.addLayout(btn_row)
        self.stack.addWidget(page)

    def _load_initial_values(self):
        if self.selected_provider in PROVIDERS:
            cfg = PROVIDERS[self.selected_provider]
            self.url_edit.setText(
                self.settings.value(
                    "base_url", cfg["base_url"])
            )
            self.key_edit.setText(self.settings.value("api_key", ""))
            self.key_edit.setPlaceholderText(cfg.get("key_placeholder", ""))
            self.provider_badge.setText(
                f"Selected Provider: {self.selected_provider}")

            icon_path = cfg.get("icon", "")
            if icon_path and os.path.exists(icon_path):
                self.provider_icon_lbl.setPixmap(
                    QIcon(icon_path).pixmap(24, 24))
                self.provider_icon_lbl.show()
            else:
                self.provider_icon_lbl.hide()

    def _update_header(self, step_index: int):
        if step_index == 0:
            self.header_title.setText("Step 1: Choose LLM Provider")
            self.header_desc.setText(
                "Select an API provider to power the autonomous agent.")
        elif step_index == 1:
            self.header_title.setText("Step 2: API Credentials & Endpoint")
            self.header_desc.setText(
                "Enter your API key and verify the server connection.")
        elif step_index == 2:
            self.header_title.setText("Step 3: Select Model")
            self.header_desc.setText(
                "Choose the model to use for visual grounding and tool calling.")

    def _go_to_step(self, step_index: int):
        self.stack.setCurrentIndex(step_index)
        self._update_header(step_index)

    def _on_provider_selected(self, provider_name: str):
        self.selected_provider = provider_name
        cfg = PROVIDERS.get(provider_name, {})

        saved_provider = self.settings.value("provider", "")
        if saved_provider == provider_name:
            self.url_edit.setText(self.settings.value(
                "base_url", cfg.get("base_url", "")))
            self.key_edit.setText(self.settings.value("api_key", ""))
        else:
            self.url_edit.setText(cfg.get("base_url", ""))
            self.key_edit.clear()

        self.key_edit.setPlaceholderText(cfg.get("key_placeholder", ""))
        self.provider_badge.setText(provider_name)

        icon_path = cfg.get("icon", "")
        if icon_path and os.path.exists(icon_path):
            self.provider_icon_lbl.setPixmap(QIcon(icon_path).pixmap(24, 24))
            self.provider_icon_lbl.show()
        else:
            self.provider_icon_lbl.clear()
            self.provider_icon_lbl.hide()

        self.status_lbl.clear()
        self._go_to_step(1)

    def _on_verify_credentials(self):
        base_url = self.url_edit.text().strip()
        api_key = self.key_edit.text().strip()

        cfg = PROVIDERS.get(self.selected_provider, {})
        if cfg.get("key_required", True) and not api_key:
            self.status_lbl.setText("❌ Please enter your API key.")
            self.status_lbl.setStyleSheet("color: #ff6b6b; font-size: 11px;")
            return

        self.verify_btn.setEnabled(False)
        self.status_lbl.setText("⏳ Testing API connection…")
        self.status_lbl.setStyleSheet("color: #8ab4f8; font-size: 11px;")
        QApplication.processEvents()

        ok, msg = verify_api_connection(
            self.selected_provider, base_url, api_key)
        self.verify_btn.setEnabled(True)

        if ok:
            self.verified_base_url = base_url
            self.verified_api_key = api_key
            self.status_lbl.clear()

            icon_path = cfg.get("icon", "")
            if icon_path and os.path.exists(icon_path):
                self.model_provider_icon_lbl.setPixmap(
                    QIcon(icon_path).pixmap(24, 24))
                self.model_provider_icon_lbl.show()
            else:
                self.model_provider_icon_lbl.clear()
                self.model_provider_icon_lbl.hide()

            # Populate models for selected provider
            self.model_combo.clear()
            models = cfg.get("models", [])
            self.model_combo.addItems(models)
            saved_model = self.settings.value("model", "")
            if saved_model and saved_model in models:
                self.model_combo.setCurrentText(saved_model)
            elif models:
                self.model_combo.setCurrentText(
                    cfg.get("default_model", models[0]))

            self._go_to_step(2)
        else:
            self.status_lbl.setText(f"❌ {msg}")
            self.status_lbl.setStyleSheet("color: #ff6b6b; font-size: 11px;")

    def _on_finish_setup(self):
        chosen_model = self.model_combo.currentText().strip()
        if not chosen_model:
            return

        key_to_save = self.verified_api_key or self.key_edit.text().strip()
        base_url_to_save = self.verified_base_url or self.url_edit.text().strip()

        s = self.settings
        s.setValue("provider", self.selected_provider)
        s.setValue("base_url", base_url_to_save)
        s.setValue("api_key", key_to_save)
        s.setValue("model", chosen_model)

        # Store provider-specific key to enable seamless reuse by TTS
        if key_to_save:
            s.setValue(
                f"{self.selected_provider.lower()}_api_key", key_to_save)

        self.accept()
