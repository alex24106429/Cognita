APP_STYLESHEET = """
    QMainWindow, QWidget { background: #1e1f26; color: #e6e6e6; }
    QGroupBox {
        border: 1px solid #34363f; border-radius: 6px;
        margin-top: 10px; padding: 10px 8px 8px 8px; font-weight: 600;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #9aa4ff; }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
        background: #262833; border: 1px solid #3a3d4a;
        border-radius: 4px; padding: 5px; selection-background-color: #4b5bd6;
    }
    QPushButton {
        background: #333748; border: 1px solid #454a5e;
        border-radius: 5px; padding: 6px 14px;
    }
    QPushButton:hover { background: #3d4257; }
    QPushButton:disabled { color: #6b6f7d; background: #262833; }
    QPushButton#startBtn { background: #2f7d4f; border-color: #3a9b62; font-weight: 700; }
    QPushButton#startBtn:hover { background: #379059; }
    QPushButton#stopBtn { background: #8e2f38; border-color: #ad3a44; font-weight: 700; }
    QPushButton#stopBtn:hover { background: #a3363f; }
    QLabel#preview { border: 1px dashed #3a3d4a; border-radius: 6px; color: #7b8094; }
    QProgressBar { border: 1px solid #3a3d4a; border-radius: 4px; text-align: center; }
    QProgressBar::chunk { background: #4b5bd6; }
"""
