from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from database.Concert import Concert
from database.typologies import load_typologies

from .AlertDialog import AlertDialog


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
        self.typologies = load_typologies()

        self.typology_edit = QComboBox()
        self.typology_edit.addItem("")
        self.typology_edit.addItems(self.typologies.keys())

        # Subtypology
        self.subtypology_edit = QComboBox()
        self.subtypology_edit.addItem("")

        self.typology_edit.currentTextChanged.connect(self.update_subtypologies)

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

        typology = concert.typology or ""

        if typology and self.typology_edit.findText(typology) == -1:
            self.typology_edit.addItem(typology)

        self.typology_edit.setCurrentText(typology)

        subtypology = concert.subtypology or ""

        if subtypology and self.subtypology_edit.findText(subtypology) == -1:
            self.subtypology_edit.addItem(subtypology)

        self.subtypology_edit.setCurrentText(subtypology)

        self.program_edit.setPlainText(concert.program or "")
        self.comment_edit.setPlainText(concert.comment or "")

    def get_concert(self):
        return Concert(
            date=self.date_edit.date().toString("yyyy-MM-dd"),
            title=self.title_edit.text().strip(),
            institution=self.institution_edit.text().strip() or None,
            price=self.price_edit.value(),
            typology=self.typology_edit.currentText().strip() or None,
            subtypology=self.subtypology_edit.currentText().strip() or None,
            program=self.program_edit.toPlainText().strip() or None,
            comment=self.comment_edit.toPlainText().strip() or None,
        )

    def validate_and_save(self):
        if not self.title_edit.text().strip():
            dialog = AlertDialog(
                title="Campo obbligatorio",
                message="Inserisci il titolo dell'evento.",
                parent=self,
            )
            dialog.exec()
            self.title_edit.setFocus()
            return

        self.accept()

    def update_subtypologies(self, typology):
        self.subtypology_edit.clear()
        self.subtypology_edit.addItem("")

        subtypologies = self.typologies.get(typology, [])
        self.subtypology_edit.addItems(subtypologies)
