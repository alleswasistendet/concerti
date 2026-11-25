from PySide6.QtCore import QDate, QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
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

from .AlertDialog import AlertDialog
from .ConcertFilterProxyModel import ConcertFilterProxyModel
from .ConcertTableModel import ConcertTableModel
from .ConfirmDialog import ConfirmDialog
from .MultiSelectComboBox import MultiSelectComboBox
from .RangeSlider import RangeSlider


class ArchivePage(QWidget):
    edit_requested = Signal(
        int, object
    )  # signal holding the concert_id and Concert object

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
            Qt.SortOrder.DescendingOrder,
        )

        # Assign proxy model to table
        self.table.setModel(self.proxy_model)

        # Header
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(50)

        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

        self._columns_initialized = False

        # Double click to update a selected line
        self.table.doubleClicked.connect(self.edit_concert)

        # Table
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

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
        for year in sorted(years, reverse=True):
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

        self.month_year_check.toggled.connect(lambda _: self.update_month_year_filter())
        self.year_combo.currentIndexChanged.connect(
            lambda _: self.update_month_year_filter(source="year")
        )
        self.month_combo.currentIndexChanged.connect(
            lambda _: self.update_month_year_filter(source="month")
        )

        # Base date filter
        dates = [
            QDate.fromString(concert.date, Qt.DateFormat.ISODate)
            for _, concert in self.model.concerts
        ]
        self.min_date_in_table = min(dates)
        self.max_date_in_table = max(dates)

        self.date_from_check = QCheckBox("Data da")
        self.date_from_check.setChecked(False)
        self.date_from_edit = QDateEdit(self.min_date_in_table)
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDisplayFormat("dd/MM/yyyy")

        self.date_to_check = QCheckBox("a")
        self.date_to_check.setChecked(False)
        self.date_to_edit = QDateEdit(self.max_date_in_table)
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
        self.price_label = QLabel("Prezzo")

        self.price_slider = RangeSlider()

        self.price_min_label = QLabel("0.00 €")
        self.price_max_label = QLabel("0.00 €")

        self.price_slider.rangeChanged.connect(self.update_price_filter)

        self.update_price_slider_range()

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
            if column == 1:  # Institution
                value_combo = MultiSelectComboBox()
                value_combo.set_options(self.get_column_values(column))

                value_combo.selectionChanged.connect(self.update_institution_filter)

                mode_combo = None
            else:
                value_combo = QComboBox()
                value_combo.setEditable(True)
                value_combo.addItem("")
                value_combo.addItems(self.get_column_values(column))
                value_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
                value_combo.setPlaceholderText(label)

                value_combo.currentTextChanged.connect(
                    lambda value, col=column: self.update_text_filter(col)
                )

                if column == 2:  # Title
                    mode_combo = QComboBox()
                    mode_combo.addItem("Contiene", "contains")
                    mode_combo.addItem("Uguale a", "exact")

                    mode_combo.currentIndexChanged.connect(
                        lambda value, col=column: self.update_text_filter(col)
                    )
                else:
                    mode_combo = None

            self.text_filters[column] = (value_combo, mode_combo)

            row_layout = QHBoxLayout()
            row_layout.addWidget(value_combo, 1)

            if mode_combo is not None:
                row_layout.addWidget(mode_combo)

            text_filter_layout.addRow(label, row_layout)

        # Filters layout
        # - First column: dates and price
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

        price_filter_layout = QGridLayout()
        price_filter_layout.setContentsMargins(0, 0, 0, 0)
        price_filter_layout.setVerticalSpacing(2)
        price_filter_layout.setColumnStretch(1, 1)

        price_filter_layout.addWidget(
            self.price_label, 0, 0, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        price_filter_layout.addWidget(self.price_slider, 0, 1)

        price_values_layout = QHBoxLayout()
        price_values_layout.setContentsMargins(0, 0, 0, 0)

        price_values_layout.addWidget(self.price_min_label)
        price_values_layout.addStretch()
        price_values_layout.addWidget(self.price_max_label)

        price_filter_layout.addLayout(price_values_layout, 1, 1)

        filters_grid.addLayout(price_filter_layout, 2, 0, 1, 4)

        # - Actual filters layout
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(24)

        filters_layout.addLayout(filters_grid)
        filters_layout.addLayout(text_filter_layout, 1)

        filters_layout.setAlignment(filters_grid, Qt.AlignmentFlag.AlignCenter)
        filters_layout.setAlignment(text_filter_layout, Qt.AlignmentFlag.AlignTop)

        # Animated filters panel
        self.filter_panel = QWidget()
        self.filter_panel.setLayout(filters_layout)
        self.filter_panel.setMaximumHeight(0)

        self.filters_animation = QPropertyAnimation(
            self.filter_panel, b"maximumHeight", self
        )
        self.filters_animation.setDuration(250)
        self.filters_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

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
        # Delete button
        self.delete_button = QPushButton("Elimina")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_concerts)

        self.table.selectionModel().selectionChanged.connect(self.update_delete_button)

        delete_button_layout = QHBoxLayout()
        delete_button_layout.addStretch()
        delete_button_layout.addWidget(self.delete_button)

        # Toggle filters button
        self.toggle_filters_button = QPushButton("Filtri")
        self.toggle_filters_button.setObjectName("toggle_filters_button")
        self.toggle_filters_button.clicked.connect(self.toggle_filters)

        # Reset filters button
        self.reset_filters_button = QPushButton("Reset")
        self.reset_filters_button.setObjectName("reset_filters_button")
        self.reset_filters_button.clicked.connect(self.reset_filters)

        ### Page layout ###
        header_layout = QHBoxLayout()
        header_layout.addWidget(heading)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_filters_button)
        header_layout.addWidget(self.reset_filters_button)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_filters_button)

        layout.addLayout(header_layout)
        layout.addWidget(self.filter_panel)
        layout.addLayout(delete_button_layout)
        layout.addWidget(self.table)
        layout.addLayout(statistics_layout)

        # Assign statistics
        self.proxy_model.modelReset.connect(lambda *args: self.update_statistics())
        self.proxy_model.layoutChanged.connect(lambda *args: self.update_statistics())
        self.proxy_model.rowsInserted.connect(lambda *args: self.update_statistics())
        self.proxy_model.rowsRemoved.connect(lambda *args: self.update_statistics())
        self.update_statistics()

    ###############
    ### Methods ###
    ###############

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

    def showEvent(self, event):
        super().showEvent(event)

        if not self._columns_initialized:
            QTimer.singleShot(0, self.adjust_column_width)
            self._columns_initialized = True

    def reload_concerts(self):
        self.model.beginResetModel()
        self.model.concerts = get_concerts()
        self.model.endResetModel()

        self.refresh_filter_values()

    def edit_concert(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)

        concert_id, concert = self.model.concerts[source_index.row()]

        self.edit_requested.emit(concert_id, concert)

    def get_column_values(self, column):
        values = {
            self.model.data(
                self.model.index(row, column),
            )
            for row in range(self.model.rowCount())
        }

        unique_values = {value.casefold(): value for value in values if value}

        return sorted(unique_values.values(), key=str.casefold)

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

        self.refresh_filter_values()

    def update_delete_button(self):
        selected_rows = self.table.selectionModel().selectedRows()
        self.delete_button.setEnabled(bool(selected_rows))

    def update_date_filter(self):
        date_from = (
            self.date_from_edit.date() if self.date_from_check.isChecked() else None
        )

        date_to = self.date_to_edit.date() if self.date_to_check.isChecked() else None

        self.proxy_model.set_date_range(date_from, date_to)

    def update_month_year_filter(self, source=None):
        # Enable filter
        if source is not None and not self.month_year_check.isChecked():
            self.month_year_check.blockSignals(True)
            self.month_year_check.setChecked(True)
            self.month_year_check.blockSignals(False)

        if not self.month_year_check.isChecked():
            self.proxy_model.set_month_year()
            return

        year = self.year_combo.currentData()
        month = self.month_combo.currentData()

        if month is not None and year is None:
            if source == "month":
                dialog = AlertDialog(
                    title="Filtro non valido",
                    message="Seleziona un anno.",
                    parent=self,
                )
                dialog.exec()

                self.month_combo.setCurrentIndex(0)

            self.proxy_model.set_month_year()
            return

        self.proxy_model.set_month_year(month=month, year=year)

    def update_price_filter(self, min_price, max_price):
        self.price_min_label.setText(f"{min_price / 100:.2f} €")
        self.price_max_label.setText(f"{max_price / 100:.2f} €")
        self.proxy_model.set_price_range(min_price / 100, max_price / 100)

    def update_price_slider_range(self):
        prices = [
            concert.price
            for _, concert in self.model.concerts
            if concert.price is not None
        ]

        min_price = round(min(prices) * 100) if prices else 0
        max_price = round(max(prices) * 100) if prices else 0

        self.price_slider.setRange(min_price, max_price)
        self.price_slider.setValues(min_price, max_price)

        self.price_min_label.setText(f"{min_price / 100:.2f} €")
        self.price_max_label.setText(f"{max_price / 100:.2f} €")

        self.proxy_model.set_price_range()

    def update_text_filter(self, column):
        value_combo, mode_combo = self.text_filters[column]

        value = value_combo.currentText().strip()

        if column in (1, 4, 5):  # Institution, Typology, Subtypology
            mode = "exact"
        elif column in (6, 7):  # Program, Comment
            mode = "all_words"
        else:
            mode = mode_combo.currentData()  # Title

        self.proxy_model.set_column_filter(column, value, mode)

    def update_institution_filter(self, values):
        self.proxy_model.set_column_filter(1, values, "any")

    def refresh_filter_values(self):
        ### Refresh price filter ###
        # Current slider range
        old_min = self.price_slider.minimum
        old_max = self.price_slider.maximum

        # Current selected range
        current_min = self.price_slider.lower_value
        current_max = self.price_slider.upper_value

        # Check if the price filter has been modified
        price_filter_unchanged = current_min == old_min and current_max == old_max

        # New price range from source model
        prices = [
            concert.price
            for _, concert in self.model.concerts
            if concert.price is not None
        ]

        min_price = round(min(prices) * 100) if prices else 0
        max_price = round(max(prices) * 100) if prices else 0

        if price_filter_unchanged:
            # Extend filter to the new price range
            current_min = min_price
            current_max = max_price
        else:
            # Preserve the filtered price selection
            current_min = max(current_min, min_price)
            current_max = min(current_max, max_price)

        current_min = min(current_min, current_max)

        # Update slider
        self.price_slider.setRange(min_price, max_price)
        self.price_slider.setValues(current_min, current_max)

        # Update labels
        self.price_min_label.setText(f"{current_min / 100:.2f} €")
        self.price_max_label.setText(f"{current_max / 100:.2f} €")

        ### Refresh text filters ###
        for column, (value_combo, _) in self.text_filters.items():
            if isinstance(value_combo, MultiSelectComboBox):
                current_values = value_combo.selected_values()

                value_combo.blockSignals(True)
                value_combo.set_options(self.get_column_values(column))
                value_combo.set_selected_values(current_values)
                value_combo.blockSignals(False)
            else:
                current_value = value_combo.currentText()

                value_combo.blockSignals(True)
                value_combo.clear()
                value_combo.addItem("")
                value_combo.addItems(self.get_column_values(column))
                value_combo.setCurrentText(current_value)
                value_combo.blockSignals(False)

    def toggle_filters(self):
        self.filters_animation.stop()

        if self.filter_panel.maximumHeight() == 0:
            self.filters_animation.setStartValue(0)
            self.filters_animation.setEndValue(self.filter_panel.sizeHint().height())
            self.toggle_filters_button.setText("Nascondi filtri")
        else:
            self.filters_animation.setStartValue(self.filter_panel.maximumHeight())
            self.filters_animation.setEndValue(0)
            self.toggle_filters_button.setText("Filtri")

        self.filters_animation.start()

    def reset_filters(self):
        # Month / year
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)

        self.month_combo.setCurrentIndex(0)
        self.year_combo.setCurrentIndex(0)

        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)

        self.month_year_check.setChecked(False)

        # Base date
        self.date_to_check.setChecked(False)
        self.date_from_edit.setDate(self.min_date_in_table)
        self.date_to_edit.setDate(self.max_date_in_table)
        self.date_from_check.setChecked(False)

        # Price
        self.price_slider.setValues(
            self.price_slider.minimum, self.price_slider.maximum
        )

        # Text
        for column, (value_combo, mode_combo) in self.text_filters.items():
            if column == 1:
                value_combo.clear()
            else:
                value_combo.setCurrentText("")

            if mode_combo is not None:
                mode_combo.setCurrentIndex(0)

        # Reset proxy filters
        self.proxy_model.set_date_range()
        self.proxy_model.set_month_year()
        self.proxy_model.set_price_range()

        for column in self.text_filters:
            self.proxy_model.set_column_filter(column, "")

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

        average_price = total_price / event_count if event_count > 0 else None

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

        metrics = QFontMetrics(self.total_price_stat.font())
        self.total_price_stat.setFixedWidth(
            metrics.horizontalAdvance("Totale: 99.999,99€")
        )
        self.average_price_stat.setFixedWidth(
            metrics.horizontalAdvance("Prezzo medio: 999,99€")
        )
