"""Qt scene responsible for rendering canvas elements, grid, and axes."""

from PyQt6.QtCore import QLineF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsScene,
)

from modules.canvas.canvas_element_item import CanvasElementItem
from modules.canvas.element import Element


class CanvasScene(QGraphicsScene):
    """Render the canvas model without owning its element business logic."""

    _default_grid_color = "#e8e8e8"
    _default_x_axis_color = "#d9534f"
    _default_y_axis_color = "#3c9d6e"

    def __init__(self, model, parent=None, theme_manager=None):
        super().__init__(parent)
        self.model = model
        self.settings = model.settings
        self.theme_manager = theme_manager
        self._preview_item = None

        app = QApplication.instance()
        if app is not None:
            app.paletteChanged.connect(self._on_palette_changed)

    def begin_add_preview(self, x, y):
        """Render a temporary element at a snapped position."""
        self.cancel_preview()
        center_x, center_y = self.model.snapped_position(x, y)
        size = self.settings.element_size
        element = Element(center_x, center_y, size, size)
        self._preview_item = CanvasElementItem(
            element,
            self.settings,
            self.theme_manager,
            preview=True,
        )
        self.addItem(self._preview_item)

    def move_preview(self, x, y):
        """Update the preview's snapped geometry."""
        if self._preview_item is None:
            return
        center_x, center_y = self.model.snapped_position(x, y)
        self._preview_item.setPos(center_x, center_y)

    def finish_add_preview(self, element):
        """Replace an add preview with the permanent element drawing."""
        if self._preview_item is None:
            self._preview_item = CanvasElementItem(
                element,
                self.settings,
                self.theme_manager,
            )
            self.addItem(self._preview_item)
        else:
            self._preview_item.element = element
            self._preview_item.setPos(element.x, element.y)
            self._preview_item.set_preview(False)
        self._preview_item = None

    def cancel_preview(self):
        """Remove the temporary element-placement preview."""
        if self._preview_item is not None:
            self.removeItem(self._preview_item)
            self._preview_item = None

    def element_item(self, element):
        """Find the graphics item that wraps an element."""
        return next(
            (
                item for item in self.items()
                if isinstance(item, CanvasElementItem)
                and item.element is element
                and not item.preview
            ),
            None,
        )

    def snap_selected_elements(self):
        """Snap dragged elements to the configured grid after a drag."""
        for item in self.selectedItems():
            if not isinstance(item, CanvasElementItem):
                continue
            self.model.move_element(
                item.element,
                item.pos().x(),
                item.pos().y(),
            )
            item.setPos(item.element.x, item.element.y)

    def delete_selected_elements(self):
        """Delete selected elements from the model and scene."""
        for item in self.selectedItems():
            if isinstance(item, CanvasElementItem):
                self.model.delete_element(item.element)
                self.removeItem(item)

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
