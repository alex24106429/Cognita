from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox
)
from api_setup_dialog import is_api_configured


class ConfigPanel(QGroupBox):
    configure_api_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Execution & API Settings", parent)
        self.settings = QSettings("cognita", "gui")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        # Row 0: Active API status display & Configure button
        self.api_badge = QLabel()
        self.api_badge.setStyleSheet("font-size: 12px; padding: 3px 0;")
        layout.addWidget(self.api_badge, 0, 0, 1, 4)

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
        opts = QHBoxLayout()
        self.hide_cb = QCheckBox("Minimise this window while the agent works")
        self.hide_cb.setChecked(True)
        self.autoscroll_cb = QCheckBox("Auto-scroll log")
        self.autoscroll_cb.setChecked(True)
        opts.addWidget(self.hide_cb)
        opts.addWidget(self.autoscroll_cb)
        opts.addStretch()
        layout.addLayout(opts, 2, 0, 1, 6)

    def load_settings(self):
        s = self.settings
        self.steps_spin.setValue(int(s.value("max_steps", 15)))
        self.pause_spin.setValue(float(s.value("pause", 0.5)))
        self.settle_spin.setValue(float(s.value("settle", 1.0)))
        self.hide_cb.setChecked(s.value("hide", True, type=bool))
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
        else:
            self.api_badge.setText(
                "<span style='color:#ff6b6b;'>⚠️ API not configured. Please click 'Configure API' to begin.</span>"
            )

    def save_settings(self):
        s = self.settings
        s.setValue("max_steps", self.steps_spin.value())
        s.setValue("pause", self.pause_spin.value())
        s.setValue("settle", self.settle_spin.value())
        s.setValue("hide", self.hide_cb.isChecked())

    def set_running(self, running: bool):
        for w in (self.cfg_btn, self.steps_spin, self.pause_spin,
                  self.settle_spin, self.hide_cb):
            w.setEnabled(not running)
