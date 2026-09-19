import sys
import pyautogui
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    load_dotenv()
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5

    app = QApplication(sys.argv)
    app.setApplicationName("Cognita")

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
