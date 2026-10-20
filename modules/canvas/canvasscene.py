"""Graphics scene for the canvas."""

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsScene


class CanvasScene(QGraphicsScene):
    """Scene containing the default 512-by-512 canvas square."""

    _x_axis_color = QColor("#d9534f")
    _y_axis_color = QColor("#3c9d6e")

    def __init__(self, parent=None):
        """Initialize the scene and add its default square."""
        super().__init__(parent)
        self.square = QRectF(0, 0, 512, 512)
        self.addRect(
            self.square,
            QPen(Qt.GlobalColor.black),
            QBrush(Qt.GlobalColor.white),
        )

    def drawForeground(self, painter, rect):
        """Draw colored axes, with dotted strokes in negative coordinates."""
        super().drawForeground(painter, rect)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if rect.top() <= 0 <= rect.bottom():
            self._draw_axis(
                painter,
                rect.left(),
                min(rect.right(), 0),
                0,
                0,
                self._x_axis_color,
                Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter,
                max(rect.left(), 0),
                rect.right(),
                0,
                0,
                self._x_axis_color,
                Qt.PenStyle.SolidLine,
            )

        if rect.left() <= 0 <= rect.right():
            self._draw_axis(
                painter,
                0,
                0,
                rect.top(),
                min(rect.bottom(), 0),
                self._y_axis_color,
                Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter,
                0,
                0,
                max(rect.top(), 0),
                rect.bottom(),
                self._y_axis_color,
                Qt.PenStyle.SolidLine,
            )

        painter.restore()

    @staticmethod
    def _draw_axis(painter, x1, x2, y1, y2, color, style):
        pen = QPen(color, 1.0, style)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(QLineF(x1, y1, x2, y2))
