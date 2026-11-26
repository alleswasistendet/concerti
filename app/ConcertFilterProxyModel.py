from PySide6.QtCore import QDate, QSortFilterProxyModel, Qt


class ConcertFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.date_from = None
        self.date_to = None

        self.month_year_from = None
        self.month_year_to = None

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
            self.month_year_from = None
            self.month_year_to = None
        elif month is None:
            self.month_year_from = QDate(year, 1, 1)
            self.month_year_to = QDate(year, 12, 31)
        else:
            self.month_year_from = QDate(year, month, 1)
            self.month_year_to = QDate(year, month, self.month_year_from.daysInMonth())

        self.invalidate()

    def set_column_filter(self, column, value, mode="contains"):
        """Set a text filter for a column."""

        if not value:
            self.column_filters.pop(column, None)
        else:
            if mode not in ("exact", "contains", "all_words", "any"):
                raise ValueError(
                    "Sono ammessi solo filtri esatti o per corrispondenza parziale."
                )

            if mode == "any":
                value = tuple(value)

                if not value:
                    self.column_filters.pop(column, None)
                    self.invalidate()
                    return

            self.column_filters[column] = (mode, value)

        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        return self.row_matches_filters(source_row)

    def row_matches_filters(self, source_row, excluded_column=None):
        model = self.sourceModel()
        concert = model.concerts[source_row][1]
        concert_date = QDate.fromString(
            concert.date,
            Qt.DateFormat.ISODate,
        )

        # Date interval
        if self.date_from is not None or self.date_to is not None:
            if not concert_date.isValid():
                return False

            if self.date_from is not None and concert_date < self.date_from:
                return False

            if self.date_to is not None and concert_date > self.date_to:
                return False

        # Month / year filter
        if self.month_year_from is not None or self.month_year_to is not None:
            if not concert_date.isValid():
                return False

            if self.month_year_from is not None and concert_date < self.month_year_from:
                return False

            if self.month_year_to is not None and concert_date > self.month_year_to:
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
            if column == excluded_column:
                continue

            index = model.index(source_row, column)
            value = model.data(index, Qt.ItemDataRole.DisplayRole)

            value = str(value) if value is not None else ""

            if mode == "exact":
                if value.casefold() != target.casefold():
                    return False

            elif mode == "contains":
                if target.casefold() not in value.casefold():
                    return False

            elif mode == "all_words":
                words = target.casefold().split()
                text = value.casefold()

                if not all(word in text for word in words):
                    return False

            elif mode == "any" and (
                not any(option.casefold() == value.casefold() for option in target)
            ):
                return False

        return True
