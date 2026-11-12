import subprocess

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


def apply_theme(app: QApplication) -> None:
    """Apply a palette in line with GNOME mode."""

    colors = DARK_COLORS if is_dark_mode() else LIGHT_COLORS

    palette = QPalette()

    for role, color in colors.items():
        palette.setColor(role, QColor(color))

    app.setPalette(palette)
