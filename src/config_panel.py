import os
import sounddevice as sd
from PyQt6.QtCore import pyqtSignal, QSettings, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QDoubleSpinBox, QComboBox,
    QLineEdit
)

try:
    import PyQt6.QtSvg  # noqa: F401 - ensures Qt SVG plugin is loaded
except ImportError:
    pass

from config import PROVIDERS, REASONING_EFFORTS, DEFAULT_REASONING_EFFORT, load_vault
from api_setup_dialog import is_api_configured


class ConfigPanel(QGroupBox):
    configure_api_requested = pyqtSignal()
    configure_tts_requested = pyqtSignal()
    configure_vault_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.settings = QSettings("cognita", "gui")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        # Row 0: Active API status display & Configure buttons
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(8)

        self.provider_icon = QLabel()
        self.provider_icon.setFixedSize(20, 20)
        self.provider_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.provider_icon.setStyleSheet("background: transparent;")
        self.provider_icon.hide()
        badge_layout.addWidget(self.provider_icon)

        self.api_badge = QLabel()
        self.api_badge.setStyleSheet("font-size: 12px; padding: 3px 0;")
        badge_layout.addWidget(self.api_badge)
        badge_layout.addStretch()

        layout.addWidget(badge_container, 0, 0, 1, 3)

        self.vault_btn = QPushButton("👤 User Data")
        self.vault_btn.setObjectName("vaultBtn")
        self.vault_btn.setToolTip(
            "Configure user profile, identity, and personal records for automated forms (data/vault.json)")
        self.vault_btn.clicked.connect(self.configure_vault_requested.emit)
        layout.addWidget(self.vault_btn, 0, 3, 1, 1)

        self.cfg_btn = QPushButton("⚙ Configure API")
        self.cfg_btn.setObjectName("configureBtn")
        self.cfg_btn.clicked.connect(self.configure_api_requested.emit)
        layout.addWidget(self.cfg_btn, 0, 4, 1, 1)

        self.tts_btn = QPushButton("🔊 Text-to-Speech")
        self.tts_btn.setObjectName("ttsBtn")
        self.tts_btn.setToolTip(
            "Configure Text-to-Speech voice engine and audio announcements")
        self.tts_btn.clicked.connect(self.configure_tts_requested.emit)
        layout.addWidget(self.tts_btn, 0, 5, 1, 1)

        # Row 1: Execution parameters (pauses)
        layout.addWidget(QLabel("Action pause (s):"), 1, 0)
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0.0, 5.0)
        self.pause_spin.setSingleStep(0.1)
        self.pause_spin.setValue(0.2)
        layout.addWidget(self.pause_spin, 1, 1)

        layout.addWidget(QLabel("Settle pause (s):"), 1, 2)
        self.settle_spin = QDoubleSpinBox()
        self.settle_spin.setRange(0.0, 10.0)
        self.settle_spin.setSingleStep(0.1)
        self.settle_spin.setValue(0.3)
        layout.addWidget(self.settle_spin, 1, 3)

        # Row 2: Target Selection (Local vs Remote Device)
        layout.addWidget(QLabel("Target:"), 2, 0)
        self.target_mode_combo = QComboBox()
        self.target_mode_combo.addItems(
            ["Local Machine", "Remote Target Device"])
        self.target_mode_combo.currentIndexChanged.connect(
            self._on_target_mode_changed)
        layout.addWidget(self.target_mode_combo, 2, 1)

        remote_container = QWidget()
        remote_row = QHBoxLayout(remote_container)
        remote_row.setContentsMargins(0, 0, 0, 0)
        remote_row.setSpacing(8)

        self.remote_host_edit = QLineEdit()
        self.remote_host_edit.setPlaceholderText(
            "IP:Port (e.g. 192.168.1.50:8765)")
        self.remote_token_edit = QLineEdit()
        self.remote_token_edit.setPlaceholderText("Auth Token (optional)")
        self.remote_token_edit.setEchoMode(QLineEdit.EchoMode.Password)

        remote_row.addWidget(QLabel("Host:"))
        remote_row.addWidget(self.remote_host_edit, 2)
        remote_row.addWidget(QLabel("Token:"))
        remote_row.addWidget(self.remote_token_edit, 1)

        layout.addWidget(remote_container, 2, 2, 1, 4)

        # Row 3: Runtime options
        layout.addWidget(QLabel("Reasoning effort:"), 3, 0)
        self.reasoning_combo = QComboBox()
        self.reasoning_combo.addItems(REASONING_EFFORTS)
        self.reasoning_combo.setToolTip(
            "Control reasoning / thinking token allocation (default, none, minimal, low, medium, high, xhigh, max)"
        )
        self.reasoning_combo.currentTextChanged.connect(self.save_settings)
        layout.addWidget(self.reasoning_combo, 3, 1)

        opts = QHBoxLayout()
        self.hide_cb = QCheckBox("Minimise this window while the agent works")
        self.hide_cb.setChecked(True)
        self.autoscroll_cb = QCheckBox("Auto-scroll log")
        self.autoscroll_cb.setChecked(True)
        opts.addWidget(self.hide_cb)
        opts.addWidget(self.autoscroll_cb)
        opts.addStretch()
        layout.addLayout(opts, 3, 2, 1, 4)

        # Row 4: Microphone selection
        layout.addWidget(QLabel("Microphone:"), 4, 0)
        self.mic_combo = QComboBox()
        self.mic_combo.setToolTip(
            "Select the microphone device for voice input")
        self._populate_microphones()
        self.mic_combo.currentIndexChanged.connect(self._on_mic_changed)
        layout.addWidget(self.mic_combo, 4, 1, 1, 3)

        self._on_target_mode_changed(self.target_mode_combo.currentIndex())

    def _on_target_mode_changed(self, index: int):
        is_remote = (index == 1)
        self.remote_host_edit.setEnabled(is_remote)
        self.remote_token_edit.setEnabled(is_remote)
        if is_remote:
            self.hide_cb.setChecked(False)

    def _populate_microphones(self):
        """Populate the microphone combo box with available input devices.

        1. Always keeps "System Default" as the first option (device data None).
        2. On Windows, targets the WASAPI host API to eliminate duplicate entries
           from MME, DirectSound, WDM-KS, etc.
        3. Falls back to generic input device enumeration if WASAPI is not available.
        """
        self.mic_combo.blockSignals(True)
        self.mic_combo.clear()

        # Always add "System Default" as the first option
        self.mic_combo.addItem("System Default", None)

        try:
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()

            # Find Windows WASAPI host API index if present
            wasapi_idx = None
            for idx, h_api in enumerate(hostapis):
                if h_api.get("name") == "Windows WASAPI":
                    wasapi_idx = idx
                    break

            for i, dev in enumerate(devices):
                if dev["max_input_channels"] <= 0:
                    continue

                # If WASAPI is present, filter for WASAPI host API devices only
                if wasapi_idx is not None and dev.get("hostapi") != wasapi_idx:
                    continue

                self.mic_combo.addItem(dev["name"], i)
        except Exception:
            pass  # "System Default" remains option

        self.mic_combo.blockSignals(False)

    def get_selected_microphone(self):
        """Return the selected microphone device ID, or None for default."""
        idx = self.mic_combo.currentIndex()
        if idx >= 0:
            return self.mic_combo.itemData(idx)
        return None

    def _on_mic_changed(self, index: int):
        """Save the selected microphone to settings."""
        device_id = self.mic_combo.itemData(index) if index >= 0 else None
        self.settings.setValue(
            "mic_device", device_id if device_id is not None else -1)

    def load_settings(self):
        s = self.settings
        self.pause_spin.setValue(float(s.value("pause", 0.2)))
        self.settle_spin.setValue(float(s.value("settle", 0.3)))
        self.hide_cb.setChecked(s.value("hide", True, type=bool))

        target_mode = int(s.value("target_mode", 0))
        self.target_mode_combo.setCurrentIndex(target_mode)
        self.remote_host_edit.setText(
            s.value("remote_host", "192.168.1.50:8765"))
        self.remote_token_edit.setText(s.value("remote_token", ""))

        effort = s.value("reasoning_effort", DEFAULT_REASONING_EFFORT)
        idx = self.reasoning_combo.findText(effort)
        if idx >= 0:
            self.reasoning_combo.setCurrentIndex(idx)
        else:
            self.reasoning_combo.setCurrentText(DEFAULT_REASONING_EFFORT)

        self.refresh_api_info()
        self.refresh_tts_info()
        self.refresh_vault_info()

        # Load saved microphone selection (fall back to System Default)
        saved_mic = self.settings.value("mic_device", type=int)
        selected = 0  # "System Default"
        if saved_mic is not None and saved_mic >= 0:
            for i in range(self.mic_combo.count()):
                if self.mic_combo.itemData(i) == saved_mic:
                    selected = i
                    break
        self.mic_combo.setCurrentIndex(selected)

    def refresh_api_info(self):
        s = self.settings
        provider = s.value("provider", "")
        model = s.value("model", "")
        if is_api_configured():
            self.api_badge.setText(
                f"<b>Provider:</b> <span style='color:#7bd88f;'>{provider}</span> &nbsp;|&nbsp; "
                f"<b>Model:</b> <span style='color:#8ab4f8;'>{model}</span>"
            )
            cfg = PROVIDERS.get(provider, {})
            icon_path = cfg.get("icon", "")
            if icon_path and os.path.exists(icon_path):
                self.provider_icon.setPixmap(QIcon(icon_path).pixmap(20, 20))
                self.provider_icon.show()
            else:
                self.provider_icon.clear()
                self.provider_icon.hide()
        else:
            self.provider_icon.clear()
            self.provider_icon.hide()
            self.api_badge.setText(
                "<span style='color:#ff6b6b;'>⚠️ API not configured. Please click 'Configure API' to begin.</span>"
            )

    def refresh_tts_info(self):
        s = self.settings
        enabled = s.value("tts_enabled", True, type=bool)
        provider = s.value("tts_provider", "supertonic")
        voice = s.value("tts_voice", "M4")
        status = "Enabled" if enabled else "Disabled"
        self.tts_btn.setToolTip(
            f"Voice Output: {status}\nProvider: {provider}\nVoice: {voice}"
        )

    def refresh_vault_info(self):
        vault = load_vault()
        if vault:
            count = len(vault)
            self.vault_btn.setToolTip(
                f"User Data: Configured ({count} sections)\nClick to edit data/vault.json"
            )
        else:
            self.vault_btn.setToolTip(
                "User Data: Not configured\nClick to set up personal profile in data/vault.json"
            )

    def save_settings(self):
        s = self.settings
        s.setValue("pause", self.pause_spin.value())
        s.setValue("settle", self.settle_spin.value())
        s.setValue("hide", self.hide_cb.isChecked())
        s.setValue("reasoning_effort", self.reasoning_combo.currentText())
        s.setValue("target_mode", self.target_mode_combo.currentIndex())
        s.setValue("remote_host", self.remote_host_edit.text().strip())
        s.setValue("remote_token", self.remote_token_edit.text().strip())
        device_id = self.get_selected_microphone()
        s.setValue("mic_device", -1 if device_id is None else device_id)

    def set_running(self, running: bool):
        for w in (self.cfg_btn, self.tts_btn, self.vault_btn, self.pause_spin,
                  self.settle_spin, self.reasoning_combo, self.hide_cb,
                  self.target_mode_combo, self.remote_host_edit, self.remote_token_edit,
                  self.mic_combo):
            w.setEnabled(not running)
