import os
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox
)
from config import DEFAULT_MODEL


class ConfigPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Configuration", parent)
        self.settings = QSettings("cognita", "gui")
        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        g = QGridLayout(self)
        g.setHorizontalSpacing(10)

        g.addWidget(QLabel("OpenRouter API key:"), 0, 0)
        self.key_edit = QLineEdit(os.environ.get("OPENAI_API_KEY", ""))
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("sk-or-v1-…")
        g.addWidget(self.key_edit, 0, 1, 1, 3)

        self.show_key = QCheckBox("Show")
        self.show_key.toggled.connect(
            lambda on: self.key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password)
        )
        g.addWidget(self.show_key, 0, 4)

        g.addWidget(QLabel("Model:"), 1, 0)
        self.model_edit = QComboBox()
        self.model_edit.setEditable(True)
        self.model_edit.addItems([
            DEFAULT_MODEL,
            "nex-agi/nex-n2.5-mini:free",
            "inclusionai/ling-3.0-flash-vl:free",
            "qwen/qwen3.8-27b:free",
            "dots-studio/dots-3-note-preview:free",
        ])
        g.addWidget(self.model_edit, 1, 1, 1, 4)

        g.addWidget(QLabel("Max steps:"), 2, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 200)
        self.steps_spin.setValue(15)
        g.addWidget(self.steps_spin, 2, 1)

        g.addWidget(QLabel("Action pause (s):"), 2, 2)
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0.0, 5.0)
        self.pause_spin.setSingleStep(0.1)
        self.pause_spin.setValue(0.5)
        g.addWidget(self.pause_spin, 2, 3)

        g.addWidget(QLabel("Settle pause (s):"), 2, 4)
        self.settle_spin = QDoubleSpinBox()
        self.settle_spin.setRange(0.0, 10.0)
        self.settle_spin.setSingleStep(0.5)
        self.settle_spin.setValue(1.0)
        g.addWidget(self.settle_spin, 2, 5)

        opts = QHBoxLayout()
        self.dry_run_cb = QCheckBox(
            "Dry run (plan only, don't touch mouse/keyboard)")
        self.hide_cb = QCheckBox("Minimise this window while the agent works")
        self.hide_cb.setChecked(True)
        self.autoscroll_cb = QCheckBox("Auto-scroll log")
        self.autoscroll_cb.setChecked(True)
        opts.addWidget(self.dry_run_cb)
        opts.addWidget(self.hide_cb)
        opts.addWidget(self.autoscroll_cb)
        opts.addStretch()
        g.addLayout(opts, 3, 0, 1, 6)

    def load_settings(self):
        s = self.settings
        self.model_edit.setCurrentText(s.value("model", DEFAULT_MODEL))
        self.steps_spin.setValue(int(s.value("max_steps", 15)))
        self.pause_spin.setValue(float(s.value("pause", 0.5)))
        self.settle_spin.setValue(float(s.value("settle", 1.0)))
        self.hide_cb.setChecked(s.value("hide", True, type=bool))
        if not self.key_edit.text():
            self.key_edit.setText(s.value("api_key", ""))

    def save_settings(self):
        s = self.settings
        s.setValue("model", self.model_edit.currentText())
        s.setValue("max_steps", self.steps_spin.value())
        s.setValue("pause", self.pause_spin.value())
        s.setValue("settle", self.settle_spin.value())
        s.setValue("hide", self.hide_cb.isChecked())
        s.setValue("api_key", self.key_edit.text())

    def set_running(self, running: bool):
        for w in (self.key_edit, self.model_edit, self.steps_spin,
                  self.pause_spin, self.settle_spin, self.dry_run_cb, self.hide_cb):
            w.setEnabled(not running)
