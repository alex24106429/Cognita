from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_pixmap = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<b>What the agent sees</b>"))

        self.preview = QLabel("No screenshot yet")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(320, 200)
        self.preview.setObjectName("preview")
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.preview, 1)

    @pyqtSlot(bytes)
    def update_preview(self, jpeg: bytes):
        img = QImage.fromData(jpeg, "JPEG")
        if img.isNull():
            return
        self._last_pixmap = QPixmap.fromImage(img)
        self.rescale()

    def rescale(self):
        if self._last_pixmap is not None:
            self.preview.setPixmap(self._last_pixmap.scaled(
                self.preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rescale()
