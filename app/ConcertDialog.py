from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from database.Concert import Concert


class ConcertDialog(QDialog):
    def __init__(self, concert=None, parent=None):
        super().__init__(parent)

        self.concert = concert

        self.setWindowTitle("Modifica evento" if concert else "Nuovo evento")
        self.resize(600, 700)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Form
        form = QFormLayout()
        form.setSpacing(12)

        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())

        # Institution
        self.institution_edit = QLineEdit()

        # Title
        self.title_edit = QLineEdit()

        # Price
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setDecimals(2)
        self.price_edit.setRange(0, 99999.99)
        self.price_edit.setValue(0.0)
        self.price_edit.setSuffix(" €")

        # Typology
        self.typology_edit = QLineEdit()

        # Subtypology
        self.subtypology_edit = QLineEdit()

        # Program
        self.program_edit = QTextEdit()
        self.program_edit.setMinimumHeight(100)
        self.program_edit.setTabChangesFocus(True)

        # Comment
        self.comment_edit = QTextEdit()
        self.comment_edit.setMinimumHeight(80)
        self.comment_edit.setTabChangesFocus(True)

        # Add widgets to form
        form.addRow("Data *", self.date_edit)
        form.addRow("Istituzione", self.institution_edit)
        form.addRow("Titolo *", self.title_edit)
        form.addRow("Prezzo", self.price_edit)
        form.addRow("Tipologia", self.typology_edit)
        form.addRow("Sottotipologia", self.subtypology_edit)
        form.addRow("Programma", self.program_edit)
        form.addRow("Commento", self.comment_edit)

        layout.addLayout(form)

        # Dialog button
        button_layout = QHBoxLayout()

        save_button = QPushButton("Salva")
        save_button.setObjectName("confirm_button")
        save_button.setDefault(True)
        save_button.clicked.connect(self.validate_and_save)

        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        # Load existing concert, if present
        if concert is not None:
            self.load_concert(concert)

    def load_concert(self, concert):
        self.date_edit.setDate(QDate.fromString(concert.date, "yyyy-MM-dd"))
        self.institution_edit.setText(concert.institution or "")
        self.title_edit.setText(concert.title)
        self.price_edit.setValue(concert.price or 0.0)
        self.typology_edit.setText(concert.typology or "")
        self.subtypology_edit.setText(concert.subtypology or "")
        self.program_edit.setPlainText(concert.program or "")
        self.comment_edit.setPlainText(concert.comment or "")

    def get_concert(self):
        return Concert(
            date=self.date_edit.date().toString("yyyy-MM-dd"),
            title=self.title_edit.text().strip(),
            institution=self.institution_edit.text().strip() or None,
            price=self.price_edit.value(),
            typology=self.typology_edit.text().strip() or None,
            subtypology=self.subtypology_edit.text().strip() or None,
            program=self.program_edit.toPlainText().strip() or None,
            comment=self.comment_edit.toPlainText().strip() or None,
        )

    def validate_and_save(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(
                self, "Campo obbligatorio", "Inserisci il titolo dell'evento."
            )
            self.title_edit.setFocus()
            return

        self.accept()
