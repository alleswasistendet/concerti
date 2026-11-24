import subprocess
from pathlib import Path

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

LIGHT_COLORS = {
    QPalette.ColorRole.Window: "#f6f5f4",
    QPalette.ColorRole.WindowText: "#242424",
    QPalette.ColorRole.Base: "#ffffff",
    QPalette.ColorRole.AlternateBase: "#f0efed",
    QPalette.ColorRole.Text: "#242424",
    QPalette.ColorRole.Button: "#e8e7e5",
    QPalette.ColorRole.ButtonText: "#242424",
    QPalette.ColorRole.Highlight: "#777f8c",
    QPalette.ColorRole.HighlightedText: "#ffffff",
}

DARK_COLORS = {
    QPalette.ColorRole.Window: "#242424",
    QPalette.ColorRole.WindowText: "#ffffff",
    QPalette.ColorRole.Base: "#1e1e1e",
    QPalette.ColorRole.AlternateBase: "#303030",
    QPalette.ColorRole.Text: "#ffffff",
    QPalette.ColorRole.Button: "#303030",
    QPalette.ColorRole.ButtonText: "#ffffff",
    QPalette.ColorRole.Highlight: "#777f8c",
    QPalette.ColorRole.HighlightedText: "#ffffff",
}


def is_dark_mode() -> bool:
    """Check if GNOME is using dark mode."""

    result = subprocess.run(
        [
            "gsettings",
            "get",
            "org.gnome.desktop.interface",
            "color-scheme",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip().strip("'") == "prefer-dark"


def get_stylesheet(dark: bool) -> str:
    """Return the application stylesheet for the active theme."""

    colors = {
        "background": "#242424" if dark else "#f6f5f4",
        "surface": "#1e1e1e" if dark else "#ffffff",
        "alternate": "#303030" if dark else "#f0efed",
        "text": "#ffffff" if dark else "#242424",
        "border": "#454545" if dark else "#d5d4d2",
        "button": "#303030" if dark else "#e8e7e5",
        "button_hover": "#414141" if dark else "#deddda",
        "sidebar": "#242424" if dark else "#eeedeb",
        "sidebar_border": "#383838" if dark else "#d5d4d2",
        "sidebar_text": "#dedede" if dark else "#454545",
        "sidebar_hover": "#353535" if dark else "#deddda",
        "sidebar_checked": "#404040" if dark else "#d5d4d2",
        "accent": "#777f8c",
        "accent_text": "#ffffff",
        "disabled": "#888888",
    }

    icon_name = "chevron-down-light.svg" if dark else "chevron-down-dark.svg"
    icon_path = Path(__file__).resolve().parent / "icons" / icon_name

    return f"""
        /* General buttons */
        QPushButton {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 6px 10px;
        }}

        QPushButton:hover {{
            background-color: {colors["button_hover"]};
        }}

        QPushButton:pressed {{
            background-color: {colors["accent"]};
            color: {colors["accent_text"]};
        }}

        QPushButton:disabled {{
            color: {colors["disabled"]};
            background-color: {colors["background"]};
        }}

        /* Sidebar */
        QWidget#sidebar {{
            background-color: {colors["sidebar"]};
            border-right: 1px solid {colors["sidebar_border"]};
        }}

        QWidget#sidebar QPushButton {{
            background-color: transparent;
            color: {colors["sidebar_text"]};
            border: none;
            border-radius: 9px;
            padding: 0px;
        }}

        QWidget#sidebar QPushButton:hover {{
            background-color: {colors["sidebar_hover"]};
        }}

        QWidget#sidebar QPushButton:checked {{
            background-color: {colors["sidebar_checked"]};
        }}

        /* Date fields */
        QDateEdit {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 2px 8px;
        }}

        QDateEdit:hover {{
            background-color: {colors["button_hover"]};
        }}

        QDateEdit:focus {{
            border: 1px solid {colors["accent"]};
        }}

        QDateEdit:disabled {{
            color: {colors["disabled"]};
        }}

        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border: none;
            border-left: 1px solid {colors["border"]};
        }}

        QDateEdit::down-arrow {{
            image: url("{icon_path.as_posix()}");
            width: 10px;
            height: 10px;
        }}

        /* Calendar popup */
        QCalendarWidget {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
        }}

        QCalendarWidget QWidget {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
        }}

        QCalendarWidget QToolButton {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 4px 8px;
            min-height: 22px;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: {colors["button_hover"]};
        }}

        QCalendarWidget QToolButton:pressed {{
            background-color: {colors["accent"]};
            color: {colors["accent_text"]};
        }}

        QCalendarWidget QAbstractItemView {{
            background-color: {colors["surface"]};
            alternate-background-color: {colors["alternate"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            selection-background-color: {colors["accent"]};
            selection-color: {colors["accent_text"]};
            outline: none;
            gridline-color: {colors["border"]};
        }}

        /* Archive table */
        QTableView {{
            background-color: {colors["surface"]};
            alternate-background-color: {colors["alternate"]};
            color: {colors["text"]};
            selection-background-color: {colors["accent"]};
            selection-color: {colors["accent_text"]};
            gridline-color: {colors["border"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
        }}

        QTableView::item {{
            padding: 5px;
        }}

        QHeaderView::section {{
            background-color: {colors["alternate"]};
            color: {colors["text"]};
            border: none;
            border-bottom: 1px solid {colors["border"]};
            padding: 5px;
        }}

        /* Multi-select list */
        QListWidget {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 4px;
        }}

        QListWidget::item:selected {{
            background-color: {colors["alternate"]};
            color: {colors["text"]};
        }}

        QListWidget::indicator {{
            width: 14px;
            height: 14px;
            border: 1px solid {colors["disabled"]};
            border-radius: 3px;
            background-color: {colors["surface"]};
        }}

        QListWidget::indicator:checked {{
            background-color: {colors["accent"]};
            border: 1px solid {colors["accent"]};
        }}

        /* Dropdown menus */
        QComboBox {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 2px 8px;
        }}

        QComboBox:hover {{
            background-color: {colors["button_hover"]};
        }}

        QComboBox:focus {{
            border: 1px solid {colors["accent"]};
        }}

        QComboBox:disabled {{
            color: {colors["disabled"]};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border: none;
            border-left: 1px solid {colors["border"]};
        }}

        QComboBox::down-arrow {{
            image: url("{icon_path.as_posix()}");
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            selection-background-color: {colors["accent"]};
            selection-color: {colors["accent_text"]};
            outline: none;
            padding: 2px;
        }}

        /* Editable combo box text field */
        QComboBox QLineEdit {{
            background-color: transparent;
            color: {colors["text"]};
            border: none;
            padding: 0px;
        }}

        /* Multi-select filter */
        QWidget#multiSelectComboBox QLineEdit {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 2px 8px;
        }}

        QWidget#multiSelectComboBox QLineEdit:hover {{
            background-color: {colors["button_hover"]};
        }}

        QWidget#multiSelectComboBox QLineEdit:focus {{
            border: 1px solid {colors["accent"]};
        }}

        QWidget#multiSelectComboBox QToolButton {{
            background-color: {colors["button"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 5px;
            padding: 2px 6px;
        }}

        QWidget#multiSelectComboBox QToolButton:hover {{
            background-color: {colors["button_hover"]};
        }}
    """


def apply_theme(app: QApplication) -> None:
    """Apply a palette in line with GNOME mode."""

    colors = DARK_COLORS if is_dark_mode() else LIGHT_COLORS

    palette = QPalette()

    for role, color in colors.items():
        palette.setColor(role, QColor(color))

    app.setPalette(palette)
    app.setStyleSheet(get_stylesheet(is_dark_mode()))
