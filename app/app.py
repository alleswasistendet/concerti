import sys

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from database.database import add_concert, update_concert

from .ArchivePage import ArchivePage
from .ConcertDialog import ConcertDialog
from .theme import apply_theme


class ConcertiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Concerti")
        self.resize(1600, 960)

        # Principal widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 16)

        sidebar_layout.addSpacing(30)

        # Navigation
        self.navigation = QButtonGroup(self)
        self.navigation.setExclusive(True)  # No multiple button selection admitted

        self.pages = QStackedWidget()

        self.archive_page = ArchivePage()
        self.archive_page.edit_requested.connect(self.open_edit_concert_dialog)

        sections = [
            ("Dashboard", self.create_page("Dashboard", "")),  # Dashboard page
            ("Archivio", self.archive_page),  # Archive page
        ]

        for index, (name, page) in enumerate(sections):
            button = QPushButton(name)
            button.setCheckable(True)

            self.navigation.addButton(button, index)
            sidebar_layout.addWidget(button)

            self.pages.addWidget(page)

        # New concert button
        self.new_concert_button = QPushButton("Nuovo evento")
        self.new_concert_button.clicked.connect(self.open_new_concert_dialog)
        sidebar_layout.addWidget(self.new_concert_button)

        sidebar_layout.addStretch()

        # Link between navigation and pages
        self.navigation.idClicked.connect(self.pages.setCurrentIndex)

        self.navigation.button(0).setChecked(True)  # Set the default page

        # Window layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

    def create_page(self, title, description):

        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(16)

        heading = QLabel(title)
        heading.setObjectName("page_title")

        # subtitle = QLabel(description)

        layout.addWidget(heading)
        # layout.addWidget(subtitle)
        layout.addStretch()

        return page

    def open_new_concert_dialog(self):
        dialog = ConcertDialog(parent=self)

        if dialog.exec():
            concert = dialog.get_concert()

            try:
                add_concert(concert)
                self.archive_page.reload_concerts()

            except Exception as error:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Impossibile salvare l'evento:\n{error}",
                )

    def open_edit_concert_dialog(self, concert_id, concert):
        dialog = ConcertDialog(concert, parent=self)

        if dialog.exec():
            updated_concert = dialog.get_concert()

            try:
                update_concert(concert_id, updated_concert)
                self.archive_page.reload_concerts()

            except Exception as error:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Impossibile aggiornare l'evento:\n{error}",
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)

    window = ConcertiApp()
    window.show()

    sys.exit(app.exec())
