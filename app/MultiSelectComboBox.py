from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .theme import is_dark_mode


class MultiSelectListWidget(QListWidget):
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            item = self.currentItem()

            if item is not None:
                state = (
                    Qt.CheckState.Unchecked
                    if item.checkState() == Qt.CheckState.Checked
                    else Qt.CheckState.Checked
                )
                item.setCheckState(state)
            return

        if event.key() == Qt.Key.Key_Escape:
            self.window().hide()
            return

        super().keyPressEvent(event)


class MultiSelectSearchEdit(QLineEdit):
    def __init__(self, combo, parent=None):
        super().__init__(parent)
        self.combo = combo
        self.list_has_focus = False

    def keyPressEvent(self, event):
        key = event.key()
        list_widget = self.combo.list_widget

        if key == Qt.Key.Key_Escape:
            self.combo.close_popup()
            return

        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            if not self.combo.popup.isVisible():
                self.combo.show_popup()
                self.list_has_focus = True

                visible_items = [
                    list_widget.item(i)
                    for i in range(list_widget.count())
                    if not list_widget.item(i).isHidden()
                ]

                if visible_items:
                    target = (
                        visible_items[0]
                        if key == Qt.Key.Key_Down
                        else visible_items[-1]
                    )
                    list_widget.setCurrentItem(target)

                return

            visible_items = [
                list_widget.item(i)
                for i in range(list_widget.count())
                if not list_widget.item(i).isHidden()
            ]

            if not visible_items:
                return

            current = list_widget.currentItem()

            if not self.list_has_focus:
                self.list_has_focus = True
                target = (
                    visible_items[0] if key == Qt.Key.Key_Down else visible_items[-1]
                )
            else:
                current_index = (
                    visible_items.index(current) if current in visible_items else -1
                )
                next_index = current_index + (1 if key == Qt.Key.Key_Down else -1)
                next_index = max(0, min(next_index, len(visible_items) - 1))
                target = visible_items[next_index]

            list_widget.setCurrentItem(target)
            return

        if key == Qt.Key.Key_Space:
            if not self.combo.popup.isVisible():
                self.combo.show_popup()
                return

            if self.list_has_focus:
                current_item = self.combo.list_widget.currentItem()

                if current_item is not None:
                    state = (
                        Qt.CheckState.Unchecked
                        if current_item.checkState() == Qt.CheckState.Checked
                        else Qt.CheckState.Checked
                    )
                    current_item.setCheckState(state)
                return

        super().keyPressEvent(event)


class MultiSelectComboBox(QWidget):
    selectionChanged = Signal(list)
    searchTextChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._options = []
        self._selected = set()

        self.setObjectName("multiSelectComboBox")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search field
        self.search_edit = MultiSelectSearchEdit(self)
        self.search_edit.setPlaceholderText("Cerca...")
        self.search_edit.textEdited.connect(self.on_search_text_changed)

        layout.addWidget(self.search_edit)

        # Dropdown button
        self.dropdown_button = QToolButton()
        self.dropdown_button.setFixedWidth(22)
        self.dropdown_button.setToolTip("Seleziona elementi")
        self.dropdown_button.clicked.connect(self.toggle_popup)

        icon_name = (
            "chevron-down-light.svg" if is_dark_mode() else "chevron-down-dark.svg"
        )
        icon_path = Path(__file__).resolve().parent / "icons" / icon_name

        self.dropdown_button.setIcon(QIcon(str(icon_path)))
        self.dropdown_button.setIconSize(QSize(12, 12))

        layout.addWidget(self.dropdown_button)

        # Popup
        self.popup = QFrame(self, Qt.WindowType.Popup)
        self.popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(4, 4, 4, 4)

        self.list_widget = MultiSelectListWidget()
        self.list_widget.itemChanged.connect(self.on_item_changed)

        popup_layout.addWidget(self.list_widget)

        self.update_selection_count()

    def set_options(self, options):
        """Set available options, preserving valid selections."""

        self._options = sorted(set(options), key=str.casefold)
        self._selected.intersection_update(self._options)

        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        for option in self._options:
            item = QListWidgetItem(option)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

            state = (
                Qt.CheckState.Checked
                if option in self._selected
                else Qt.CheckState.Unchecked
            )
            item.setCheckState(state)
            item.setSizeHint(QSize(0, 32))

            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

        self.filter_options(self.search_edit.text())
        self.update_selection_count()

    def selected_values(self):
        """Return selected options."""

        return sorted(self._selected, key=str.casefold)

    def search_edit(self):
        """Return the current search text."""

        return self.search_edit.text().strip()

    def set_selected_values(self, values):
        """Set selected options."""

        self._selected = set(values) & set(self._options)

        self.list_widget.blockSignals(True)

        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            state = (
                Qt.CheckState.Checked
                if item.text() in self._selected
                else Qt.CheckState.Unchecked
            )
            item.setCheckState(state)

        self.list_widget.blockSignals(False)

        self.update_selection_count()
        self.selectionChanged.emit(self.selected_values())

    def clear(self):
        """Clear search text and selections."""

        self.search_edit.clear()
        self._selected.clear()

        self.list_widget.blockSignals(True)

        for index in range(self.list_widget.count()):
            self.list_widget.item(index).setCheckState(Qt.CheckState.Unchecked)

        self.list_widget.blockSignals(False)

        self.filter_options("")
        self.update_selection_count()
        self.selectionChanged.emit([])

    def on_search_text_changed(self, text):
        self.filter_options(text)
        self.searchTextChanged.emit(text)

        if text and not self.popup.isVisible():
            self.show_popup()

    def filter_options(self, text):
        query = text.casefold().strip()

        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setHidden(query not in item.text().casefold())

    def on_item_changed(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            self._selected.add(item.text())
        else:
            self._selected.discard(item.text())

        self.update_selection_count()
        self.selectionChanged.emit(self.selected_values())

    def update_selection_count(self):
        count = len(self._selected)
        self.dropdown_button.setText(f"{count}" if count else "")

    def toggle_popup(self):
        if self.popup.isVisible():
            self.close_popup()
        else:
            self.show_popup()

    def show_popup(self):
        width = max(self.width(), 240)
        height = min(
            max(
                self.list_widget.sizeHintForRow(0) * min(self.list_widget.count(), 8)
                + 16,
                80,
            ),
            240,
        )

        self.popup.resize(width, height)
        self.popup.move(self.mapToGlobal(QPoint(0, self.height())))

        self.popup.show()

        self.search_edit.setFocus(Qt.FocusReason.OtherFocusReason)
        self.search_edit.grabKeyboard()

    def close_popup(self):
        self.search_edit.releaseKeyboard()
        self.popup.hide()
