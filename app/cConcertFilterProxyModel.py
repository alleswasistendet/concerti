from PySide6.QtCore import QDate, QSortFilterProxyModel, Qt


class ConcertFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.date_from = None
        self.date_to = None

        self.price_min = None
        self.price_max = None

        self.column_filters = {}  # {column: (mode, value)}

    def set_date_range(self, date_from=None, date_to=None):
        """Set a date interval, with either endpoint optional."""

        self.date_from = date_from
        self.date_to = date_to
        self.invalidate()

    def set_price_range(self, price_min=None, price_max=None):
        """Set a price interval, with either endpoint optional."""
        self.price_min = price_min
        self.price_max = price_max
        self.invalidate()

    def set_month_year(self, month=None, year=None):
        """Set a filter by month and/or year."""
        if month is not None and year is None:
            raise ValueError("Seleziona anche l'anno.")

        if year is None:
            self.set_date_range()
            return

        if month is None:
            date_from = QDate(year, 1, 1)
            date_to = QDate(year, 12, 31)
        else:
            date_from = QDate(year, month, 1)
            date_to = QDate(year, month, date_from.daysInMonth())

        self.set_date_range(date_from, date_to)

    def set_column_filter(self, column, value, mode="contains"):
        """Set a text filter for a column, either exact or by partial content's match."""

        if not value:
            self.column_filters.pop(column, None)
        else:
            if mode not in ("exact", "contains"):
                raise ValueError(
                    "Sono ammessi solo filtri esatti o per corrispondenza parziale."
                )

            self.column_filters[column] = (mode, value)

        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        concert = model.concerts[source_row][1]

        # Date interval
        if self.date_from is not None or self.date_to is not None:
            concert_date = QDate.fromString(
                concert.date,
                Qt.DateFormat.ISODate,
            )

            if not concert_date.isValid():
                return False

            if self.date_from is not None and concert_date < self.date_from:
                return False

            if self.date_to is not None and concert_date > self.date_to:
                return False

        # Price interval
        if self.price_min is not None or self.price_max is not None:
            price = concert.price

            if price is None:
                return False

            if self.price_min is not None and price < self.price_min:
                return False

            if self.price_max is not None and price > self.price_max:
                return False

        # Column filters
        for column, (mode, target) in self.column_filters.items():
            index = model.index(source_row, column)
            value = model.data(index, Qt.ItemDataRole.DisplayRole)

            value = str(value) if value is not None else ""

            if mode == "exact":
                if value.casefold() != target.casefold():
                    return False
            elif mode == "contains":  # noqa: SIM102
                if target.casefold() not in value.casefold():
                    return False

        return True
