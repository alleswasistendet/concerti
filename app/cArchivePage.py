from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from database.database import delete_concert, get_concerts

from .cConcertFilterProxyModel import ConcertFilterProxyModel
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

        ### Table layout ###

        self.table = QTableView()
        concerts = get_concerts()

        # Model
        self.model = ConcertTableModel(concerts)

        # Proxy model
        self.proxy_model = ConcertFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy_model.sort(
            0,
            Qt.SortOrder.AscendingOrder,
        )

        # Assign statistics
        self.proxy_model.modelReset.connect(lambda *args: self.update_statistics())
        self.proxy_model.layoutChanged.connect(lambda *args: self.update_statistics())
        self.proxy_model.rowsInserted.connect(lambda *args: self.update_statistics())
        self.proxy_model.rowsRemoved.connect(lambda *args: self.update_statistics())

        # Assign proxy model to table
        self.table.setModel(self.proxy_model)

        # Table
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        header = self.table.horizontalHeader()
        self.table.resizeColumnsToContents()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

        ### Filters ###

        # Month / year filter
        self.month_year_check = QCheckBox("Mese / anno")
        self.month_year_check.setChecked(False)

        self.year_combo = QComboBox()
        self.year_combo.addItem("Anno", None)

        years = {int(concert.date[:4]) for _, concert in self.model.concerts}
        years.add(QDate.currentDate().year())

        self.month_combo = QComboBox()
        self.month_combo.addItem("Tutti i mesi", None)
        for year in sorted(years):
            self.year_combo.addItem(str(year), year)

        months = [
            "Gennaio",
            "Febbraio",
            "Marzo",
            "Aprile",
            "Maggio",
            "Giugno",
            "Luglio",
            "Agosto",
            "Settembre",
            "Ottobre",
            "Novembre",
            "Dicembre",
        ]

        for month, name in enumerate(months, start=1):
            self.month_combo.addItem(name, month)

        self.month_year_check.toggled.connect(self.update_month_year_filter)
        self.year_combo.currentIndexChanged.connect(
            lambda _: self.update_month_year_filter()
        )
        self.month_combo.currentIndexChanged.connect(
            lambda _: self.update_month_year_filter()
        )
        self.year_combo.currentIndexChanged.connect(
            lambda: self.month_year_check.setChecked(True)
        )
        self.month_combo.currentIndexChanged.connect(
            lambda: self.month_year_check.setChecked(True)
        )

        # Base date filter
        dates = [
            QDate.fromString(concert.date, Qt.DateFormat.ISODate)
            for _, concert in self.model.concerts
        ]
        min_date_in_table = min(dates)
        max_date_in_table = max(dates)

        self.date_from_check = QCheckBox("Data da")
        self.date_from_check.setChecked(False)
        self.date_from_edit = QDateEdit(min_date_in_table)
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDisplayFormat("dd/MM/yyyy")

        self.date_to_check = QCheckBox("a")
        self.date_to_check.setChecked(False)
        self.date_to_edit = QDateEdit(max_date_in_table)
        self.date_to_edit.setCalendarPopup(True)
        self.date_to_edit.setDisplayFormat("dd/MM/yyyy")

        self.date_from_check.toggled.connect(self.update_date_filter)
        self.date_to_check.toggled.connect(self.update_date_filter)
        self.date_from_edit.dateChanged.connect(self.update_date_filter)
        self.date_to_edit.dateChanged.connect(self.update_date_filter)

        self.date_from_edit.dateChanged.connect(
            lambda: self.date_from_check.setChecked(True)
        )
        self.date_to_edit.dateChanged.connect(
            lambda: self.date_to_check.setChecked(True)
        )

        # Price filter
        prices_float = tuple(float(x[:-2]) for x in self.get_column_values(3))
        min_price_in_table = min(prices_float)
        max_price_in_table = max(prices_float)

        self.price_min_check = QCheckBox("Prezzo da")
        self.price_min_check.setChecked(False)
        self.price_min_edit = QDoubleSpinBox()
        self.price_min_edit.setRange(0, 100000)
        self.price_min_edit.setDecimals(2)
        self.price_min_edit.setSuffix(" €")
        self.price_min_edit.setValue(min_price_in_table)

        self.price_max_check = QCheckBox("a")
        self.price_max_check.setChecked(False)
        self.price_max_edit = QDoubleSpinBox()
        self.price_max_edit.setRange(0, 100000)
        self.price_max_edit.setDecimals(2)
        self.price_max_edit.setSuffix(" €")
        self.price_max_edit.setValue(max_price_in_table)

        self.price_min_check.toggled.connect(self.update_price_filter)
        self.price_max_check.toggled.connect(self.update_price_filter)
        self.price_min_edit.valueChanged.connect(self.update_price_filter)
        self.price_max_edit.valueChanged.connect(self.update_price_filter)

        self.price_min_edit.valueChanged.connect(
            lambda: self.price_min_check.setChecked(True)
        )
        self.price_max_edit.valueChanged.connect(
            lambda: self.price_max_check.setChecked(True)
        )

        # Text filters
        self.text_filters = {}

        text_columns = {
            1: "Istituzione",
            2: "Titolo",
            4: "Tipologia",
            5: "Sottotipologia",
            6: "Programma",
            7: "Commento",
        }

        text_filter_layout = QFormLayout()
        text_filter_layout.setSpacing(8)

        for column, label in text_columns.items():
            value_combo = QComboBox()
            value_combo.setEditable(True)
            value_combo.addItem("")
            value_combo.addItems(self.get_column_values(column))
            value_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            value_combo.setPlaceholderText(label)

            mode_combo = QComboBox()
            mode_combo.addItem("Contiene", "contains")
            mode_combo.addItem("Uguale a", "exact")

            value_combo.currentTextChanged.connect(
                lambda value, col=column: self.update_text_filter(col)
            )
            mode_combo.currentIndexChanged.connect(
                lambda value, col=column: self.update_text_filter(col)
            )

            self.text_filters[column] = (value_combo, mode_combo)

            row_layout = QHBoxLayout()
            row_layout.addWidget(value_combo, 1)
            row_layout.addWidget(mode_combo)

            text_filter_layout.addRow(label, row_layout)

        # Filters layout
        filters_grid = QGridLayout()
        filters_grid.setHorizontalSpacing(12)
        filters_grid.setVerticalSpacing(12)

        filters_grid.addWidget(self.month_year_check, 0, 0)
        filters_grid.addWidget(self.year_combo, 0, 1)
        filters_grid.addWidget(self.month_combo, 0, 3)

        filters_grid.addWidget(self.date_from_check, 1, 0)
        filters_grid.addWidget(self.date_from_edit, 1, 1)
        filters_grid.addWidget(self.date_to_check, 1, 2)
        filters_grid.addWidget(self.date_to_edit, 1, 3)

        filters_grid.addWidget(self.price_min_check, 2, 0)
        filters_grid.addWidget(self.price_min_edit, 2, 1)
        filters_grid.addWidget(self.price_max_check, 2, 2)
        filters_grid.addWidget(self.price_max_edit, 2, 3)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(24)

        filters_layout.addLayout(filters_grid)
        filters_layout.addLayout(text_filter_layout, 1)

        filters_layout.setAlignment(filters_grid, Qt.AlignmentFlag.AlignTop)
        filters_layout.setAlignment(text_filter_layout, Qt.AlignmentFlag.AlignTop)

        ### Statistics ###

        self.event_stat = QLabel("Eventi: 0")
        self.total_price_stat = QLabel("Totale: 0.00 €")
        self.average_price_stat = QLabel("Prezzo medio: —")

        statistics_layout = QHBoxLayout()
        statistics_layout.addWidget(self.total_price_stat)
        statistics_layout.addWidget(self.average_price_stat)
        statistics_layout.addStretch()
        statistics_layout.addWidget(self.event_stat)

        ### Buttons ###

        self.delete_button = QPushButton("Elimina")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_concerts)

        self.table.selectionModel().selectionChanged.connect(self.update_delete_button)

        delete_button_layout = QHBoxLayout()
        delete_button_layout.addStretch()
        delete_button_layout.addWidget(self.delete_button)

        ### Page layout ###
        layout.addWidget(heading)
        layout.addLayout(filters_layout)
        layout.addLayout(delete_button_layout)
        layout.addWidget(self.table)
        layout.addLayout(statistics_layout)

        self.update_statistics()

    ###############
    ### Methods ###
    ###############

    def get_column_values(self, column):
        values = {
            self.model.data(
                self.model.index(row, column),
            )
            for row in range(self.model.rowCount())
        }

        return sorted((value for value in values if value), key=str.casefold)

    def delete_selected_concerts(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            return

        source_rows = [self.proxy_model.mapToSource(index) for index in selected_rows]
        concert_ids = [self.model.concerts[index.row()][0] for index in source_rows]

        message = (
            f"Eliminare {len(concert_ids)} eventi?"
            if len(concert_ids) > 1
            else "Eliminare l'evento?"
        )

        dialog = ConfirmDialog("Elimina", message, "Sì", "No", self.window())

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        for concert_id in concert_ids:
            delete_concert(concert_id)

        self.model.beginResetModel()
        self.model.concerts = get_concerts()
        self.model.endResetModel()

        self.refresh_text_filter_values()

    def update_delete_button(self):
        selected_rows = self.table.selectionModel().selectedRows()
        self.delete_button.setEnabled(bool(selected_rows))

    def update_date_filter(self):
        date_from = (
            self.date_from_edit.date() if self.date_from_check.isChecked() else None
        )

        date_to = self.date_to_edit.date() if self.date_to_check.isChecked() else None

        self.proxy_model.set_date_range(date_from, date_to)

    def update_month_year_filter(self):
        if not self.month_year_check.isChecked():
            self.proxy_model.set_month_year()
            return

        year = self.year_combo.currentData()
        month = self.month_combo.currentData()

        self.proxy_model.set_month_year(month=month, year=year)

    def update_price_filter(self):
        price_min = (
            self.price_min_edit.value() if self.price_min_check.isChecked() else None
        )
        price_max = (
            self.price_max_edit.value() if self.price_max_check.isChecked() else None
        )

        self.proxy_model.set_price_range(price_min=price_min, price_max=price_max)

    def update_text_filter(self, column):
        value_combo, mode_combo = self.text_filters[column]

        value = value_combo.currentText().strip()
        mode = mode_combo.currentData()

        self.proxy_model.set_column_filter(column, value, mode)

    def refresh_text_filter_values(self):
        for column, (value_combo, _) in self.text_filters.items():
            current_value = value_combo.currentText()

            value_combo.blockSignals(True)
            value_combo.clear()
            value_combo.addItem("")
            value_combo.addItems(self.get_column_values(column))
            value_combo.setCurrentText(current_value)
            value_combo.blockSignals(False)

    def compute_statistics(self):
        event_count = self.proxy_model.rowCount()
        total_price = 0.0

        for row in range(event_count):
            proxy_index = self.proxy_model.index(row, 0)
            source_index = self.proxy_model.mapToSource(proxy_index)

            concert = self.model.concerts[source_index.row()][1]

            if concert.price is None:
                continue

            total_price += concert.price

        average_price = total_price / event_count

        return {
            "event_count": event_count,
            "total_price": total_price,
            "average_price": average_price,
        }

    def update_statistics(self):
        statistics = self.compute_statistics()

        self.event_stat.setText(f"Eventi: {statistics['event_count']}")
        self.total_price_stat.setText(f"Totale: {statistics['total_price']:.2f} €")

        average_price = statistics["average_price"]
        self.average_price_stat.setText(
            f"Prezzo medio: {average_price:.2f} €"
            if average_price is not None
            else "Prezzo medio: —"
        )
