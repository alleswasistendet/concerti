from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class AlertDialog(QDialog):
    def __init__(self, title: str, message: str, button_text: str = "Ok", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(20)

        message_label = QLabel(message)
        message_label.setWordWrap(True)

        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        button = QPushButton(button_text)
        button.setObjectName("confirm_button")
        button.setDefault(True)
        button.clicked.connect(self.accept)

        button_layout.addWidget(button)

        layout.addLayout(button_layout)
