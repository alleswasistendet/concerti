from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class ConfirmDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str,
        cancel_text: str = "Cancel",
        parent=None,
    ):
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

        confirm_button = QPushButton(confirm_text)
        confirm_button.setObjectName("confirm_button")
        confirm_button.clicked.connect(self.accept)

        cancel_button = QPushButton(cancel_text)
        cancel_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
