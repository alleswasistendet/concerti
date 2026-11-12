import sys

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from theme import apply_theme


class ConcertiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Concerti")
        self.resize(1600, 960)

        # title = QLabel("Concerti")
        # title.setStyleSheet("""
        #     font-size: 28px;
        #     font-weight: 600;
        #     padding: 30px
        # """)

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

        # logo = QLabel("Concerti")
        # logo.setObjectName("logo")
        # sidebar_layout.addWidget(logo)

        sidebar_layout.addSpacing(30)

        # Navigation
        self.navigation = QButtonGroup(self)
        self.navigation.setExclusive(True)  # No multiple button selection admitted

        self.pages = QStackedWidget()

        sections = [
            ("Dashboard", self.create_page("Dashboard", "")),
            ("Archivio", self.create_page("Archivio", "")),
            (
                "Nuovo evento",
                self.create_page("Nuovo evento", ""),
            ),
        ]

        for index, (name, page) in enumerate(sections):
            button = QPushButton(name)
            button.setCheckable(True)

            self.navigation.addButton(button, index)
            sidebar_layout.addWidget(button)

            self.pages.addWidget(page)

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

        subtitle = QLabel(description)

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addStretch()

        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)

    window = ConcertiApp()
    window.show()

    sys.exit(app.exec())
