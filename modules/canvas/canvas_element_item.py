"""Qt graphics item that renders a canvas element."""

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem


class CanvasElementItem(QGraphicsRectItem):
    """Draw one element and its connection points as a single graphics item."""

    def __init__(self, element, settings, theme_manager=None, preview=False):
        self.element = element
        self.settings = settings
        self.theme_manager = theme_manager
        self.preview = preview
        super().__init__(
            QRectF(
                -element.width / 2,
                -element.height / 2,
                element.width,
                element.height,
            )
        )
        theme = self._theme()
        self._normal_pen_color = theme.get("canvasPenPrimary", "#000000")
        self._selection_color = theme.get("highlight", "#3498db")
        self.setPos(element.x, element.y)
        self.set_preview(preview)

    def boundingRect(self):
        """Include connection point circles that extend beyond the element."""
        bounds = super().boundingRect()
        radius = self.settings.connection_point_size / 2
        return bounds.adjusted(-radius, -radius, radius, radius)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        color = QColor(self._theme().get("highlight", self._selection_color))
        pen = QPen(color, 2 if self.preview else 1)
        pen.setCosmetic(True)
        painter.save()
        painter.setPen(pen)
        painter.setBrush(QBrush(color))
        diameter = self.settings.connection_point_size
        radius = diameter / 2
        for x, y in self.element.connection_points:
            painter.drawEllipse(
                QRectF(
                    x - self.element.x - radius,
                    y - self.element.y - radius,
                    diameter,
                    diameter,
                )
            )
        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            pen = self.pen()
            selected = bool(value)
            pen.setColor(
                QColor(
                    self._theme().get("highlight", "#3498db")
                    if selected
                    else self._normal_pen_color
                )
            )
            pen.setWidthF(
                3 if selected else self.settings.element_pen_width
            )
            pen.setCosmetic(selected)
            self.setPen(pen)
        return super().itemChange(change, value)

    def set_preview(self, preview):
        """Switch between the temporary preview and permanent element style."""
        self.preview = preview
        if preview:
            color = QColor(self._selection_color)
            pen = QPen(color, 2, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            color.setAlpha(48)
            self.setPen(pen)
            self.setBrush(QBrush(color))
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.setZValue(1)
        else:
            pen = QPen(
                QColor(self._normal_pen_color),
                self.settings.element_pen_width,
            )
            self.setPen(pen)
            self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            self.setZValue(0)
        self.update()

    def _theme(self):
        if self.theme_manager is None:
            return {}
        return self.theme_manager.get_active_theme()
