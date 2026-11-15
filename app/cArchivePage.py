from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from database.database import delete_concert, get_concerts

from .cConcertTableModel import ConcertTableModel
from .cConfirmDialog import ConfirmDialog


class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(16)

        heading = QLabel("Archivio")
        heading.setObjectName("page_title")

        # Table displaying the DB contents
        self.table = QTableView()
        concerts = get_concerts()
        self.model = ConcertTableModel(concerts)
        self.table.setModel(self.model)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        header = self.table.horizontalHeader()
        self.table.resizeColumnsToContents()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

        # Delete button
        self.delete_button = QPushButton("Elimina")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_concerts)

        self.table.selectionModel().selectionChanged.connect(self.update_delete_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)

        # Assign objects to the page
        layout.addWidget(heading)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        layout.addStretch()

    def delete_selected_concerts(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            return

        concert_ids = [self.model.concerts[index.row()][0] for index in selected_rows]

        message = (
            f"Eliminare {len(concert_ids)} eventi?"
            if len(concert_ids) > 1
            else "Eliminare l'evento?"
        )

        dialog = ConfirmDialog("Elimina", message, "Sì", "No")

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        for concert_id in concert_ids:
            delete_concert(concert_id)

        self.model.beginResetModel()
        self.model.concerts = get_concerts()
        self.model.endResetModel()

    def update_delete_button(self):
        selected_rows = self.table.selectionModel().selectedRows()
        self.delete_button.setEnabled(bool(selected_rows))
