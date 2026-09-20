from PyQt6.QtCore import Qt, QSettings, QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QComboBox,
    QFrame, QGroupBox, QApplication
)

from config import TTS_PROVIDERS, DEFAULT_TTS_PROVIDER
from tts import speak_text, get_reusable_api_key


class TtsTestWorker(QObject):
    finished = pyqtSignal(bool, str)

    def __init__(self, text: str, provider: str, voice: str, api_key: str, model: str):
        super().__init__()
        self.text = text
        self.provider = provider
        self.voice = voice
        self.api_key = api_key
        self.model = model

    def run(self):
        try:
            speak_text(
                text=self.text,
                provider=self.provider,
                voice=self.voice,
                api_key=self.api_key,
                model=self.model,
            )
            self.finished.emit(True, "Audio playback completed.")
        except Exception as e:
            self.finished.emit(False, str(e))


class TtsSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cognita — Text-to-Speech (TTS) Setup")
        self.resize(600, 520)
        self.setModal(True)

        self.settings = QSettings("cognita", "gui")
        self.test_thread = None
        self.test_worker = None

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # Header
        title_lbl = QLabel("Text-to-Speech Settings")
        title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #9aa4ff;")
        desc_lbl = QLabel(
            "Select a voice provider and configure synthesis options for task feedback."
        )
        desc_lbl.setStyleSheet("color: #9aa0b4; font-size: 12px;")
        root.addWidget(title_lbl)
        root.addWidget(desc_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #34363f;")
        root.addWidget(sep)

        # Enable TTS toggle
        self.enable_cb = QCheckBox("Enable voice output on task completion")
        self.enable_cb.setStyleSheet(
            "font-weight: 600; font-size: 13px; color: #e6e6e6;")
        self.enable_cb.toggled.connect(self._on_enable_toggled)
        root.addWidget(self.enable_cb)

        # Config Box
        self.settings_box = QGroupBox("Voice Provider Configuration")
        box_layout = QVBoxLayout(self.settings_box)
        box_layout.setSpacing(10)

        # Provider Selector
        p_row = QHBoxLayout()
        p_row.addWidget(QLabel("TTS Provider:"), 1)
        self.provider_combo = QComboBox()
        for p_id, p_info in TTS_PROVIDERS.items():
            self.provider_combo.addItem(p_info["label"], p_id)
        self.provider_combo.currentIndexChanged.connect(
            self._on_provider_changed)
        p_row.addWidget(self.provider_combo, 3)
        box_layout.addLayout(p_row)

        self.provider_desc_lbl = QLabel()
        self.provider_desc_lbl.setStyleSheet(
            "color: #8e92a4; font-size: 11px;")
        box_layout.addWidget(self.provider_desc_lbl)

        # API Key Row
        self.key_container = QFrame()
        key_layout = QVBoxLayout(self.key_container)
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.setSpacing(4)

        key_head_row = QHBoxLayout()
        key_head_row.addWidget(QLabel("API Key:"))
        self.key_source_badge = QLabel()
        self.key_source_badge.setStyleSheet(
            "font-size: 11px; color: #7bd88f; font-weight: 600;")
        key_head_row.addWidget(self.key_source_badge)
        key_head_row.addStretch()
        key_layout.addLayout(key_head_row)

        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText(
            "Enter API key or reuse active credentials…")
        key_layout.addWidget(self.key_edit)

        show_key_cb = QCheckBox("Show API key")
        show_key_cb.toggled.connect(
            lambda on: self.key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password
            )
        )
        key_layout.addWidget(show_key_cb)
        box_layout.addWidget(self.key_container)

        # Model Selection Row
        self.model_row = QHBoxLayout()
        self.model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_row.addWidget(self.model_label, 1)
        self.model_row.addWidget(self.model_combo, 3)
        box_layout.addLayout(self.model_row)

        # Voice Selection Row
        v_row = QHBoxLayout()
        v_row.addWidget(QLabel("Voice:"), 1)
        self.voice_combo = QComboBox()
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        v_row.addWidget(self.voice_combo, 3)
        box_layout.addLayout(v_row)

        # Custom Voice ID row (For ElevenLabs)
        self.custom_voice_container = QFrame()
        cv_layout = QHBoxLayout(self.custom_voice_container)
        cv_layout.setContentsMargins(0, 0, 0, 0)
        cv_layout.addWidget(QLabel("Custom Voice ID:"), 1)
        self.custom_voice_edit = QLineEdit()
        self.custom_voice_edit.setPlaceholderText("e.g. 21m00Tcm4TlvDq8ikWAM")
        cv_layout.addWidget(self.custom_voice_edit, 3)
        box_layout.addWidget(self.custom_voice_container)

        root.addWidget(self.settings_box)

        # Test Section
        test_box = QGroupBox("Test Voice Output")
        test_layout = QVBoxLayout(test_box)
        test_layout.setSpacing(8)

        t_row = QHBoxLayout()
        self.test_edit = QLineEdit(
            "Cognita has completed your task successfully.")
        self.test_btn = QPushButton("▶ Test Voice")
        self.test_btn.clicked.connect(self._on_test_voice)
        t_row.addWidget(self.test_edit, 1)
        t_row.addWidget(self.test_btn)
        test_layout.addLayout(t_row)

        self.test_status_lbl = QLabel()
        self.test_status_lbl.setStyleSheet("font-size: 11px;")
        test_layout.addWidget(self.test_status_lbl)
        root.addWidget(test_box)

        root.addStretch()

        # Dialog Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("startBtn")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _on_enable_toggled(self, enabled: bool):
        self.settings_box.setEnabled(enabled)

    def _load_settings(self):
        s = self.settings
        self.enable_cb.setChecked(s.value("tts_enabled", True, type=bool))

        saved_provider = s.value("tts_provider", DEFAULT_TTS_PROVIDER)
        idx = self.provider_combo.findData(saved_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        else:
            self.provider_combo.setCurrentIndex(0)

        self._update_provider_fields(self.provider_combo.currentData())

        saved_voice = s.value("tts_voice", "")
        if saved_voice:
            v_idx = self.voice_combo.findText(saved_voice)
            if v_idx >= 0:
                self.voice_combo.setCurrentIndex(v_idx)
            else:
                self.voice_combo.setCurrentText(saved_voice)

        saved_model = s.value("tts_model", "")
        if saved_model:
            m_idx = self.model_combo.findText(saved_model)
            if m_idx >= 0:
                self.model_combo.setCurrentIndex(m_idx)
            else:
                self.model_combo.setCurrentText(saved_model)

        self.custom_voice_edit.setText(s.value("tts_elevenlabs_custom_id", ""))
        self._on_enable_toggled(self.enable_cb.isChecked())

    def _on_provider_changed(self):
        provider = self.provider_combo.currentData()
        self._update_provider_fields(provider)

    def _update_provider_fields(self, provider: str):
        cfg = TTS_PROVIDERS.get(provider, {})
        self.provider_desc_lbl.setText(cfg.get("description", ""))

        # Voice list setup
        self.voice_combo.clear()
        self.voice_combo.addItems(cfg.get("voices", []))
        default_voice = cfg.get("default_voice", "")
        if default_voice:
            self.voice_combo.setCurrentText(default_voice)

        # Model list setup
        self.model_combo.clear()
        models = cfg.get("models", [])
        self.model_combo.addItems(models)
        if models:
            self.model_combo.setCurrentText(
                cfg.get("default_model", models[0]))

        # Key & controls visibility
        if provider == "supertonic":
            self.key_container.hide()
            self.model_row.itemAt(0).widget().hide()
            self.model_combo.hide()
            self.custom_voice_container.hide()
        elif provider == "openrouter":
            self.key_container.show()
            self.model_row.itemAt(0).widget().hide()
            self.model_combo.hide()
            self.custom_voice_container.hide()
            self._populate_key("openrouter")
        elif provider == "openai":
            self.key_container.show()
            self.model_row.itemAt(0).widget().show()
            self.model_combo.show()
            self.custom_voice_container.hide()
            self._populate_key("openai")
        elif provider == "elevenlabs":
            self.key_container.show()
            self.model_row.itemAt(0).widget().show()
            self.model_combo.show()
            self._populate_key("elevenlabs")
            self._on_voice_changed()

    def _populate_key(self, provider: str):
        key, source = get_reusable_api_key(provider)
        self.key_edit.setText(key)
        if source:
            self.key_source_badge.setText(f"✓ {source}")
            self.key_source_badge.show()
        else:
            self.key_source_badge.hide()

    def _on_voice_changed(self):
        provider = self.provider_combo.currentData()
        if provider == "elevenlabs" and "Custom" in self.voice_combo.currentText():
            self.custom_voice_container.show()
        else:
            self.custom_voice_container.hide()

    def _on_test_voice(self):
        provider = self.provider_combo.currentData()
        text = self.test_edit.text().strip()
        if not text:
            self.test_status_lbl.setText("❌ Please enter some test text.")
            self.test_status_lbl.setStyleSheet("color: #ff6b6b;")
            return

        api_key = self.key_edit.text().strip()
        cfg = TTS_PROVIDERS.get(provider, {})
        if cfg.get("key_required", False) and not api_key:
            self.test_status_lbl.setText(
                f"❌ API key is required for {provider}.")
            self.test_status_lbl.setStyleSheet("color: #ff6b6b;")
            return

        voice = self.voice_combo.currentText()
        if provider == "elevenlabs" and "Custom" in voice:
            voice = self.custom_voice_edit.text().strip()
            if not voice:
                self.test_status_lbl.setText(
                    "❌ Please enter a custom ElevenLabs voice ID.")
                self.test_status_lbl.setStyleSheet("color: #ff6b6b;")
                return

        model = self.model_combo.currentText().strip()

        self.test_btn.setEnabled(False)
        self.test_status_lbl.setText("⏳ Synthesizing and playing speech…")
        self.test_status_lbl.setStyleSheet("color: #8ab4f8;")
        QApplication.processEvents()

        self.test_thread = QThread()
        self.test_worker = TtsTestWorker(
            text=text,
            provider=provider,
            voice=voice,
            api_key=api_key,
            model=model,
        )
        self.test_worker.moveToThread(self.test_thread)
        self.test_thread.started.connect(self.test_worker.run)
        self.test_worker.finished.connect(self._on_test_finished)
        self.test_thread.start()

    def _on_test_finished(self, success: bool, message: str):
        self.test_btn.setEnabled(True)
        if success:
            self.test_status_lbl.setText(f"✓ {message}")
            self.test_status_lbl.setStyleSheet("color: #7bd88f;")
        else:
            self.test_status_lbl.setText(f"❌ {message}")
            self.test_status_lbl.setStyleSheet("color: #ff6b6b;")

        if self.test_thread:
            self.test_thread.quit()
            self.test_thread.wait()
            self.test_thread = None
            self.test_worker = None

    def _on_save(self):
        provider = self.provider_combo.currentData()
        voice = self.voice_combo.currentText()
        model = self.model_combo.currentText().strip()
        api_key = self.key_edit.text().strip()

        s = self.settings
        s.setValue("tts_enabled", self.enable_cb.isChecked())
        s.setValue("tts_provider", provider)
        s.setValue("tts_voice", voice)
        s.setValue("tts_model", model)

        if provider in ("openrouter", "openai", "elevenlabs") and api_key:
            s.setValue(f"tts_{provider}_api_key", api_key)

        if provider == "elevenlabs":
            s.setValue("tts_elevenlabs_custom_id",
                       self.custom_voice_edit.text().strip())

        self.accept()
