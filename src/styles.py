APP_STYLESHEET = """
    QMainWindow, QWidget, QDialog { background: #1e1f26; color: #e6e6e6; }
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
    QPushButton#configureBtn { background: #4b5bd6; border-color: #5d6de6; font-weight: 600; }
    QPushButton#configureBtn:hover { background: #5a6ae6; }
    QPushButton#ttsBtn { background: #40346e; border-color: #59489c; font-weight: 600; }
    QPushButton#ttsBtn:hover { background: #4e3f87; }
    QPushButton#vaultBtn { background: #2f567d; border-color: #3b6ea0; font-weight: 600; }
    QPushButton#vaultBtn:hover { background: #396796; }
    QPushButton#providerSelectBtn {
        background: #262833; border: 1px solid #3a3d4a;
        border-radius: 6px; text-align: left;
    }
    QPushButton#providerSelectBtn:hover {
        background: #313442; border-color: #6a74db;
    }
    QPushButton#providerSelectBtn:pressed {
        background: #3a3e52;
    }
    QLabel#preview { border: 1px dashed #3a3d4a; border-radius: 6px; color: #7b8094; }
    QProgressBar { border: 1px solid #3a3d4a; border-radius: 4px; text-align: center; }
    QProgressBar::chunk { background: #4b5bd6; }
    QTabWidget::pane { border: 1px solid #34363f; background: #1e1f26; border-radius: 4px; }
    QTabBar::tab {
        background: #262833; color: #9aa0b4; padding: 8px 14px;
        border: 1px solid #34363f; border-bottom: none;
        border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;
    }
    QTabBar::tab:selected { background: #333748; color: #ffffff; border-color: #4b5bd6; font-weight: 600; }
    QTabBar::tab:hover { background: #2e3140; color: #e6e6e6; }
    QScrollArea { border: none; background: transparent; }
"""
