"""Qt scene responsible for rendering canvas elements, grid, and axes."""

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsScene


class CanvasScene(QGraphicsScene):
    """Render the canvas model without owning its element business logic."""

    _default_grid_color = "#e8e8e8"
    _default_x_axis_color = "#d9534f"
    _default_y_axis_color = "#3c9d6e"
    _default_pen_primary_color = "#000000"

    def __init__(self, model, parent=None, theme_manager=None):
        super().__init__(parent)
        self.model = model
        self.settings = model.settings
        self.theme_manager = theme_manager
        self._element_items = {}
        self._preview_item = None
        self._preview_element = None

        app = QApplication.instance()
        if app is not None:
            app.paletteChanged.connect(self._on_palette_changed)

    def begin_add_preview(self, x, y):
        """Render a temporary element at a snapped position."""
        self.cancel_preview()
        geometry = self.model.geometry_at(x, y)
        self._preview_item = self._create_preview_item(geometry)

    def begin_move_preview(self, element):
        """Render a moving element preview while hiding its original item."""
        self.cancel_preview()
        self._preview_element = element
        self._element_items[element].setVisible(False)
        geometry = self.model.geometry_at(element.x, element.y, element)
        self._preview_item = self._create_preview_item(geometry)

    def move_preview(self, x, y):
        """Update the preview's snapped geometry."""
        if self._preview_item is None:
            return
        geometry = self.model.geometry_at(x, y, self._preview_element)
        self._preview_item.setRect(QRectF(*geometry))

    def finish_add_preview(self, element):
        """Replace an add preview with the permanent element drawing."""
        self.cancel_preview()
        self._element_items[element] = self._create_element_item(element)

    def finish_move_preview(self, element):
        """Update an element drawing after the model has moved it."""
        self.cancel_preview()
        item = self._element_items[element]
        item.setRect(self._element_rect(element))
        item.setVisible(True)

    def cancel_preview(self):
        """Remove a preview and restore an element being moved."""
        if self._preview_item is not None:
            self.removeItem(self._preview_item)
            self._preview_item = None
        if self._preview_element is not None:
            self._element_items[self._preview_element].setVisible(True)
            self._preview_element = None

    def remove_element(self, element):
        """Remove an element's graphics item after model deletion."""
        item = self._element_items.pop(element, None)
        if item is not None:
            self.removeItem(item)

    def _create_element_item(self, element):
        theme = self._active_theme()
        pen = QPen(
            QColor(theme.get("canvasPenPrimary", self._default_pen_primary_color)),
            self.settings.element_pen_width,
        )
        brush = QBrush(Qt.BrushStyle.NoBrush)
        item = self.addRect(self._element_rect(element), pen, brush)
        item.setZValue(0)
        return item

    def _create_preview_item(self, geometry):
        theme = self._active_theme()
        color = QColor(theme.get("highlight", "#3498db"))
        pen = QPen(color, 2, Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        fill_color = QColor(color)
        fill_color.setAlpha(48)
        item = self.addRect(QRectF(*geometry), pen, QBrush(fill_color))
        item.setZValue(1)
        return item

    @staticmethod
    def _element_rect(element):
        return QRectF(
            element.x - element.width / 2,
            element.y - element.height / 2,
            element.width,
            element.height,
        )

    def _active_theme(self):
        if self.theme_manager is None:
            return {}
        return self.theme_manager.get_active_theme()

    def drawBackground(self, painter, rect):
        """Draw the configurable grid behind the elements."""
        super().drawBackground(painter, rect)
        if not self._grid_is_visible_at_current_zoom():
            return

        theme = self._active_theme()
        pen = QPen(QColor(theme.get("canvasGrid", self._default_grid_color)))
        pen.setCosmetic(True)
        painter.save()
        painter.setPen(pen)

        horizontal_spacing = self.settings.grid_spacing_horizontal
        vertical_spacing = self.settings.grid_spacing_vertical
        left = int(rect.left() // horizontal_spacing)
        right = int(rect.right() // horizontal_spacing) + 1
        top = int(rect.top() // vertical_spacing)
        bottom = int(rect.bottom() // vertical_spacing) + 1
        lines = [
            QLineF(index * horizontal_spacing, rect.top(),
                   index * horizontal_spacing, rect.bottom())
            for index in range(left, right + 1)
        ]
        lines.extend(
            QLineF(rect.left(), index * vertical_spacing,
                   rect.right(), index * vertical_spacing)
            for index in range(top, bottom + 1)
        )
        painter.drawLines(lines)
        painter.restore()

    def _grid_is_visible_at_current_zoom(self):
        views = self.views()
        return (
            not views
            or views[0].transform().m11() >= self.settings.minimum_grid_zoom
        )

    def drawForeground(self, painter, rect):
        """Draw colored axes with dotted strokes in negative coordinates."""
        super().drawForeground(painter, rect)
        theme = self._active_theme()
        x_axis_color = QColor(theme.get("xAxis", self._default_x_axis_color))
        y_axis_color = QColor(theme.get("yAxis", self._default_y_axis_color))
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if rect.top() <= 0 <= rect.bottom():
            self._draw_axis(
                painter, rect.left(), min(rect.right(), 0), 0, 0,
                x_axis_color, Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter, max(rect.left(), 0), rect.right(), 0, 0,
                x_axis_color, Qt.PenStyle.SolidLine,
            )

        if rect.left() <= 0 <= rect.right():
            self._draw_axis(
                painter, 0, 0, rect.top(), min(rect.bottom(), 0),
                y_axis_color, Qt.PenStyle.DotLine,
            )
            self._draw_axis(
                painter, 0, 0, max(rect.top(), 0), rect.bottom(),
                y_axis_color, Qt.PenStyle.SolidLine,
            )

        painter.restore()

    def _on_palette_changed(self, _palette):
        """Redraw theme-dependent canvas colors."""
        self.update()

    @staticmethod
    def _draw_axis(painter, x1, x2, y1, y2, color, style):
        pen = QPen(color, 2.0, style)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(QLineF(x1, y1, x2, y2))
