from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from database.database import get_concerts

from .cConcertTableModel import ConcertTableModel


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
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

        # Assign objects to the page
        layout.addWidget(heading)
        layout.addWidget(self.table)
        layout.addStretch()
