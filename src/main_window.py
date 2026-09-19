import time
from PyQt6.QtCore import Qt, QThread, pyqtSlot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QGroupBox, QSplitter,
    QMessageBox, QProgressBar, QStatusBar, QApplication
)
from styles import APP_STYLESHEET
from config_panel import ConfigPanel
from log_panel import LogPanel
from preview_panel import PreviewPanel
from worker import AgentWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cognita")
        self.resize(1180, 760)
        self.thread, self.worker = None, None

        self._build_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.cfg_panel = ConfigPanel()
        root.addWidget(self.cfg_panel)

        task_box = QGroupBox("Task")
        tl = QHBoxLayout(task_box)
        self.task_edit = QLineEdit(
            self.cfg_panel.settings.value("last_task", ""))
        self.task_edit.setPlaceholderText(
            "e.g. Open browser and search for weather in Berlin")
        self.task_edit.returnPressed.connect(self.start_agent)
        self.task_edit.setMinimumHeight(32)

        self.start_btn = QPushButton("▶  Run Agent", objectName="startBtn")
        self.start_btn.setMinimumHeight(34)
        self.start_btn.clicked.connect(self.start_agent)

        self.stop_btn = QPushButton("■  STOP", objectName="stopBtn")
        self.stop_btn.setMinimumHeight(34)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_agent)

        tl.addWidget(self.task_edit, 1)
        tl.addWidget(self.start_btn)
        tl.addWidget(self.stop_btn)
        root.addWidget(task_box)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.log_panel = LogPanel()
        self.preview_panel = PreviewPanel()
        self.cfg_panel.autoscroll_cb.toggled.connect(
            self.log_panel.set_autoscroll)
        self.log_panel.status_message.connect(self.statusBar().showMessage)

        splitter.addWidget(self.log_panel)
        splitter.addWidget(self.preview_panel)
        splitter.setSizes([640, 520])
        root.addWidget(splitter, 1)

        self.progress = QProgressBar(maximumWidth=220, visible=False)
        self.progress.setFormat("step %v / %m")
        sb = QStatusBar()
        sb.addPermanentWidget(self.progress)
        self.setStatusBar(sb)
        self.statusBar().showMessage(
            "Idle — fail-safe active: fling mouse to corner to abort.")

        self.setCentralWidget(central)

    def start_agent(self):
        if self.thread:
            return
        task, key = self.task_edit.text().strip(), self.cfg_panel.key_edit.text().strip()
        if not key or not task:
            QMessageBox.warning(self, "Missing fields",
                                "Please provide both an API key and a task.")
            return

        res = QMessageBox.question(
            self, "Takeover Warning", "Agent will take control of mouse/keyboard. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res != QMessageBox.StandardButton.Yes:
            return

        self.cfg_panel.save_settings()
        self.cfg_panel.settings.setValue("last_task", task)
        self._set_running(True)

        self.worker = AgentWorker(
            key, self.cfg_panel.model_edit.currentText().strip(), task,
            self.cfg_panel.steps_spin.value(),
            self.cfg_panel.pause_spin.value(), self.cfg_panel.settle_spin.value(),
        )
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log_panel.append_log)
        self.worker.thought.connect(
            lambda t: self.log_panel.append_log("think", f"🧠 {t}"))
        self.worker.action.connect(
            lambda n, a: self.log_panel.append_log("action", f"⚙ {n} {a}"))
        self.worker.screenshot.connect(self.preview_panel.update_preview)
        self.worker.step.connect(lambda cur, tot: (
            self.progress.setMaximum(tot), self.progress.setValue(cur)))
        self.worker.status.connect(self.statusBar().showMessage)
        self.worker.finished.connect(self.on_finished)

        if self.cfg_panel.hide_cb.isChecked():
            self.showMinimized()
            QApplication.processEvents()
            time.sleep(0.6)

        self.thread.start()

    def stop_agent(self):
        if self.worker:
            self.worker.stop()
            self.stop_btn.setEnabled(False)
            self.statusBar().showMessage("Stopping…")

    @pyqtSlot(bool, str)
    def on_finished(self, success: bool, summary: str):
        self.log_panel.append_log(
            "info" if success else "warn", ("✅ DONE — " if success else "⏹ ENDED — ") + summary)
        self.statusBar().showMessage("Finished" if success else "Stopped")
        if self.thread:
            self.thread.quit()
            self.thread.wait(3000)
            self.thread.deleteLater()
        if self.worker:
            self.worker.deleteLater()
        self.thread, self.worker = None, None
        self._set_running(False)
        if self.isMinimized():
            self.showNormal()

    def _set_running(self, running: bool):
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.task_edit.setEnabled(not running)
        self.progress.setVisible(running)
        self.cfg_panel.set_running(running)

    def closeEvent(self, e):
        if self.thread is not None:
            self.worker.stop()
            self.thread.quit()
            self.thread.wait(3000)
        self.cfg_panel.save_settings()
        e.accept()
