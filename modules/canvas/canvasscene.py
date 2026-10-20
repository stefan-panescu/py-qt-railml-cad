"""Graphics scene for the canvas."""

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsScene


class CanvasScene(QGraphicsScene):
    """Scene containing the default 512-by-512 canvas square."""

    _default_x_axis_color = "#d9534f"
    _default_y_axis_color = "#3c9d6e"
    _default_pen_primary_color = "#000000"

    def __init__(self, parent=None, theme_manager=None):
        """Initialize the scene and add its default square."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        app = QApplication.instance()
        if app is not None:
            app.paletteChanged.connect(self._on_palette_changed)

        self._primary_pen = QPen()
        self._primary_pen.setColor(QColor(
            self.theme_manager
            .get_active_theme()
            .get("canvasPenPrimary", self._default_pen_primary_color)
        ))
        self._primary_pen.setWidthF(5)

        self._primary_brush = QBrush(Qt.GlobalColor.transparent)

        # Demo square:
        self.square = QRectF(0, 0, 512, 512)
        self.addRect(
            self.square,
            self._primary_pen,
            self._primary_brush
        )

    def drawForeground(self, painter, rect):
        """Draw colored axes, with dotted strokes in negative coordinates."""
        super().drawForeground(painter, rect)
        theme = (
            self.theme_manager.get_active_theme()
            if self.theme_manager is not None
            else {}
        )
        x_axis_color = QColor(
            theme.get("xAxis", self._default_x_axis_color)
        )
        y_axis_color = QColor(
            theme.get("yAxis", self._default_y_axis_color)
        )
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if rect.top() <= 0 <= rect.bottom():
            self._draw_axis(
                painter,
                rect.left(),
                min(rect.right(), 0),
                0,
                0,
                x_axis_color,
                Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter,
                max(rect.left(), 0),
                rect.right(),
                0,
                0,
                x_axis_color,
                Qt.PenStyle.SolidLine,
            )

        if rect.left() <= 0 <= rect.right():
            self._draw_axis(
                painter,
                0,
                0,
                rect.top(),
                min(rect.bottom(), 0),
                y_axis_color,
                Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter,
                0,
                0,
                max(rect.top(), 0),
                rect.bottom(),
                y_axis_color,
                Qt.PenStyle.SolidLine,
            )

        painter.restore()

    def _on_palette_changed(self, _palette):
        """Redraw axes when the application theme changes or is previewed."""
        self.update()

    @staticmethod
    def _draw_axis(painter, x1, x2, y1, y2, color, style):
        pen = QPen(color, 2.0, style)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(QLineF(x1, y1, x2, y2))
