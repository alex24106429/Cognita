import time
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QFileDialog
)
from config import LOG_COLORS


class LogPanel(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.autoscroll = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<b>Agent trace</b>"))

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas, Menlo, monospace", 10))
        layout.addWidget(self.log_view)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.log_view.clear)
        save_btn = QPushButton("Save log…")
        save_btn.clicked.connect(self.save_log)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    @pyqtSlot(str, str)
    def append_log(self, level: str, text: str):
        color = LOG_COLORS.get(level, "#e6e6e6")
        stamp = time.strftime("%H:%M:%S")
        safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace("\n", "<br>"))
        html = (f'<div style="margin:2px 0;">'
                f'<span style="color:#5c6070;">[{stamp}]</span> '
                f'<span style="color:{color};">{safe}</span></div>')
        self.log_view.append(html)
        if self.autoscroll:
            self.log_view.moveCursor(QTextCursor.MoveOperation.End)

    def set_autoscroll(self, enabled: bool):
        self.autoscroll = enabled

    def save_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save log", "agent_log.txt", "Text files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_view.toPlainText())
            self.status_message.emit(f"Log saved to {path}")
