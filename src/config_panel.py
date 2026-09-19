import os
from PyQt6.QtCore import pyqtSignal, QSettings, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox
)

try:
    import PyQt6.QtSvg  # noqa: F401 - ensures Qt SVG plugin is loaded
except ImportError:
    pass

from config import PROVIDERS, REASONING_EFFORTS, DEFAULT_REASONING_EFFORT
from api_setup_dialog import is_api_configured


class ConfigPanel(QGroupBox):
    configure_api_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.settings = QSettings("cognita", "gui")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        # Row 0: Active API status display & Configure button
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

        layout.addWidget(badge_container, 0, 0, 1, 4)

        self.cfg_btn = QPushButton("⚙ Configure API…")
        self.cfg_btn.setObjectName("configureBtn")
        self.cfg_btn.clicked.connect(self.configure_api_requested.emit)
        layout.addWidget(self.cfg_btn, 0, 4, 1, 2)

        # Row 1: Execution parameters (steps, pauses)
        layout.addWidget(QLabel("Max steps:"), 1, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 200)
        self.steps_spin.setValue(15)
        layout.addWidget(self.steps_spin, 1, 1)

        layout.addWidget(QLabel("Action pause (s):"), 1, 2)
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0.0, 5.0)
        self.pause_spin.setSingleStep(0.1)
        self.pause_spin.setValue(0.5)
        layout.addWidget(self.pause_spin, 1, 3)

        layout.addWidget(QLabel("Settle pause (s):"), 1, 4)
        self.settle_spin = QDoubleSpinBox()
        self.settle_spin.setRange(0.0, 10.0)
        self.settle_spin.setSingleStep(0.5)
        self.settle_spin.setValue(1.0)
        layout.addWidget(self.settle_spin, 1, 5)

        # Row 2: Runtime options
        layout.addWidget(QLabel("Reasoning effort:"), 2, 0)
        self.reasoning_combo = QComboBox()
        self.reasoning_combo.addItems(REASONING_EFFORTS)
        self.reasoning_combo.setToolTip(
            "Control reasoning / thinking token allocation (default, none, minimal, low, medium, high, xhigh, max)"
        )
        self.reasoning_combo.currentTextChanged.connect(self.save_settings)
        layout.addWidget(self.reasoning_combo, 2, 1)

        opts = QHBoxLayout()
        self.hide_cb = QCheckBox("Minimise this window while the agent works")
        self.hide_cb.setChecked(True)
        self.autoscroll_cb = QCheckBox("Auto-scroll log")
        self.autoscroll_cb.setChecked(True)
        opts.addWidget(self.hide_cb)
        opts.addWidget(self.autoscroll_cb)
        opts.addStretch()
        layout.addLayout(opts, 2, 2, 1, 4)

    def load_settings(self):
        s = self.settings
        self.steps_spin.setValue(int(s.value("max_steps", 15)))
        self.pause_spin.setValue(float(s.value("pause", 0.5)))
        self.settle_spin.setValue(float(s.value("settle", 1.0)))
        self.hide_cb.setChecked(s.value("hide", True, type=bool))

        effort = s.value("reasoning_effort", DEFAULT_REASONING_EFFORT)
        idx = self.reasoning_combo.findText(effort)
        if idx >= 0:
            self.reasoning_combo.setCurrentIndex(idx)
        else:
            self.reasoning_combo.setCurrentText(DEFAULT_REASONING_EFFORT)

        self.refresh_api_info()

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

    def save_settings(self):
        s = self.settings
        s.setValue("max_steps", self.steps_spin.value())
        s.setValue("pause", self.pause_spin.value())
        s.setValue("settle", self.settle_spin.value())
        s.setValue("hide", self.hide_cb.isChecked())
        s.setValue("reasoning_effort", self.reasoning_combo.currentText())

    def set_running(self, running: bool):
        for w in (self.cfg_btn, self.steps_spin, self.pause_spin,
                  self.settle_spin, self.reasoning_combo, self.hide_cb):
            w.setEnabled(not running)
