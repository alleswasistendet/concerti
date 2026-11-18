from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class RangeSlider(QWidget):
    rangeChanged = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.minimum = 0
        self.maximum = 10000

        self.lower_value = self.minimum
        self.upper_value = self.maximum

        self.handle_radius = 7
        self.track_height = 4

        self.active_handle = None

        self.setMinimumHeight(30)
        self.setMouseTracking(True)

    def sizeHint(self):
        from PySide6.QtCore import QSize

        return QSize(250, 30)

    def setRange(self, minimum, maximum):
        if minimum > maximum:
            raise ValueError("Il valore minimo non può superare il massimo")

        self.minimum = minimum
        self.maximum = maximum

        self.lower_value = minimum
        self.upper_value = maximum

        self.update()
        self.rangeChanged.emit(self.lower_value, self.upper_value)

    def valueToPosition(self, value):
        margin = self.handle_radius
        available_width = self.width() - 2 * margin

        if self.maximum == self.minimum:
            return margin

        ratio = (value - self.minimum) / (self.maximum - self.minimum)
        return margin + ratio * available_width

    def positionToValue(self, position):
        margin = self.handle_radius
        available_width = self.width() - 2 * margin

        if available_width <= 0:
            return self.minimum

        ratio = (position - margin) / available_width
        ratio = max(0.0, min(ratio, 1.0))

        return round(self.minimum + ratio * (self.maximum - self.minimum))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_y = self.height() / 2
        margin = self.handle_radius

        left = margin
        right = self.width() - margin

        lower_x = self.valueToPosition(self.lower_value)
        upper_x = self.valueToPosition(self.upper_value)

        # Slider bar
        painter.setPen(
            QPen(
                QColor("#a0a0a0"),
                self.track_height,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(QPointF(left, center_y), QPointF(right, center_y))

        # Selected interval
        painter.setPen(
            QPen(
                QColor("#e0e0e0"),
                self.track_height,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(QPointF(lower_x, center_y), QPointF(upper_x, center_y))

        # Handles
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#e0e0e0")))

        painter.drawEllipse(
            QPointF(lower_x, center_y), self.handle_radius, self.handle_radius
        )

        painter.drawEllipse(
            QPointF(upper_x, center_y), self.handle_radius, self.handle_radius
        )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.position().x()

        lower_x = self.valueToPosition(self.lower_value)
        upper_x = self.valueToPosition(self.upper_value)

        # Select the closest handle
        if abs(x - lower_x) <= abs(x - upper_x):
            self.active_handle = "lower"
        else:
            self.active_handle = "upper"

        self.updateValue(x)

    def mouseMoveEvent(self, event):
        if self.active_handle is None:
            return

        self.updateValue(event.position().x())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_handle = None

    def updateValue(self, x):
        value = self.positionToValue(x)

        if self.active_handle == "lower":
            value = min(value, self.upper_value)
            if value != self.lower_value:
                self.lower_value = value
                self.rangeChanged.emit(self.lower_value, self.upper_value)

        elif self.active_handle == "upper":
            value = max(value, self.lower_value)
            if value != self.upper_value:
                self.upper_value = value
                self.rangeChanged.emit(self.lower_value, self.upper_value)

        self.update()
