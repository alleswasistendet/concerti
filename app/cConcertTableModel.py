from typing import ClassVar

from PySide6.QtCore import QAbstractTableModel, QDate, QLocale, QModelIndex, Qt


class ConcertTableModel(QAbstractTableModel):
    HEADERS: ClassVar[list[str]] = [
        "Data",
        "Istituzione",
        "Titolo",
        "Prezzo",
        "Tipologia",
        "Sottotipologia",
        "Programma",
        "Commento",
    ]
    INVALID_INDEX = QModelIndex()

    def __init__(self, concerts=None):
        """Initialize the class. Variable concerts is expected to be a tuple (id, Concert)."""
        super().__init__()
        self.concerts = concerts or []

    def rowCount(self, parent=INVALID_INDEX):
        return len(self.concerts)

    def columnCount(self, parent=INVALID_INDEX):
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() in (0, 3):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return None

        if role == Qt.ItemDataRole.UserRole:
            if index.column() == 0:
                concert = self.concerts[index.row()][1]
                return QDate.fromString(
                    concert.date,
                    Qt.DateFormat.ISODate,
                )
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        concert = self.concerts[index.row()][1]

        date = QDate.fromString(concert.date, Qt.DateFormat.ISODate)
        formatted_date = QLocale.system().toString(date, "dd/MM/yyyy")

        values = [
            formatted_date,
            concert.institution,
            concert.title,
            f"{concert.price:.2f} €" if concert.price is not None else "0.00 €",
            concert.typology,
            concert.subtypology,
            concert.program,
            concert.comment,
        ]

        return values[index.column()]

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]

        return str(section + 1)
