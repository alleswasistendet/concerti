from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from database.database import get_latest_concerts

from .ConcertTableModel import ConcertTableModel


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(16)

        heading = QLabel("Dashboard")
        heading.setObjectName("pageHeading")

        layout.addWidget(heading)

        self.concerts = get_latest_concerts(20)

        ### Table layout ###

        # Latest concerts
        self.table = QTableView()
        self.model = ConcertTableModel(self.concerts)
        self.table.setModel(self.model)

        # Header
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(50)

        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

        self.table.setMinimumHeight(
            header.sizeHint().height()
            + 2 * self.table.frameWidth()
            + 2 * self.table.verticalHeader().defaultSectionSize()
        )

        self._columns_initialized = False

        # Build layout
        layout.addWidget(self.table)
        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)

        if not self._columns_initialized:
            QTimer.singleShot(0, self.adjust_column_width)
            self._columns_initialized = True

    def adjust_column_width(self):
        # Width of the first six columns based on their content
        for column in range(6):
            self.table.resizeColumnToContents(column)

        # Remaining space is equally shared by last two columns
        remaining_width = self.table.viewport().width() - sum(
            self.table.columnWidth(column) for column in range(6)
        )
        column_width = max(50, remaining_width // 2)

        self.table.setColumnWidth(6, column_width)
        self.table.setColumnWidth(7, column_width)
