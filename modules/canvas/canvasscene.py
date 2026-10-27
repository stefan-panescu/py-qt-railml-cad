"""Graphics scene for the canvas."""

from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsScene


class CanvasScene(QGraphicsScene):
    """Scene containing the default 512-by-512 canvas square."""

    _grid_spacing_horizontal = 200
    _grid_spacing_vertical = 400
    _minimum_grid_zoom = 0.2
    _default_grid_color = "#e8e8e8"
    _default_x_axis_color = "#d9534f"
    _default_y_axis_color = "#3c9d6e"
    _default_pen_primary_color = "#000000"
    _element_size = 800
    _element_data_key = 0

    def __init__(self, parent=None, theme_manager=None):
        """Initialize the scene and add its default square."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        app = QApplication.instance()
        if app is not None:
            app.paletteChanged.connect(self._on_palette_changed)

        self._primary_pen = QPen()
        theme = (
            self.theme_manager.get_active_theme()
            if self.theme_manager is not None
            else {}
        )
        self._primary_pen.setColor(
            QColor(theme.get("canvasPenPrimary", self._default_pen_primary_color))
        )
        self._primary_pen.setWidthF(5)

        self._primary_brush = QBrush(Qt.GlobalColor.transparent)
        self._preview_item = None
        self._moving_item = None

    def begin_add_element(self, position):
        """Create a temporary square preview at the requested scene position."""
        self.cancel_move_element()
        self.cancel_add_element()
        theme = (
            self.theme_manager.get_active_theme()
            if self.theme_manager is not None
            else {}
        )
        color = QColor(theme.get("highlight", "#3498db"))
        preview_pen = QPen(color, 2, Qt.PenStyle.DashLine)
        preview_pen.setCosmetic(True)
        fill_color = QColor(color)
        fill_color.setAlpha(48)
        self._preview_item = self.addRect(
            self._element_rect(position),
            preview_pen,
            QBrush(fill_color),
        )
        self._preview_item.setData(self._element_data_key, True)
        self._preview_item.setZValue(1)

    def begin_move_element(self, position):
        """Select an existing placed element and prepare its move preview."""
        self.cancel_add_element()
        self.cancel_move_element()
        for item in self.items(position):
            if item.data(self._element_data_key):
                self._moving_item = item
                self._moving_item.setVisible(False)
                self._preview_item = self.addRect(
                    item.rect(),
                    item.pen(),
                    item.brush(),
                )
                self._preview_item.setData(self._element_data_key, True)
                self._preview_item.setZValue(1)
                self.move_element_preview(position)
                return True
        return False

    def move_element_preview(self, position):
        """Move the temporary square preview to the cursor position."""
        if self._preview_item is not None:
            element_size = self._preview_item.rect().size()
            snapped_center = self._snapped_position(position)
            self._preview_item.setRect(
                QRectF(
                    snapped_center.x() - element_size.width() / 2,
                    snapped_center.y() - element_size.height() / 2,
                    element_size.width(),
                    element_size.height(),
                )
            )

    def has_selected_element_to_move(self):
        """Return whether the move tool has selected an element."""
        return self._moving_item is not None

    def place_element_preview(self):
        """Keep the preview square in the scene as a permanent element."""
        if self._preview_item is None:
            return
        if self._moving_item is not None:
            self._moving_item.setRect(self._preview_item.rect())
            self._moving_item.setVisible(True)
            self.removeItem(self._preview_item)
            self._moving_item = None
        else:
            self._preview_item.setPen(self._primary_pen)
            self._preview_item.setBrush(self._primary_brush)
            self._preview_item.setZValue(0)
        self._preview_item = None

    def cancel_add_element(self):
        """Remove the temporary preview square, if one exists."""
        if self._preview_item is not None:
            self.removeItem(self._preview_item)
            self._preview_item = None

    def cancel_move_element(self):
        """Cancel an active move and restore the selected element."""
        self.cancel_add_element()
        if self._moving_item is not None:
            self._moving_item.setVisible(True)
            self._moving_item = None

    def delete_element_at(self, position):
        """Delete the topmost placed element at the scene position."""
        for item in self.items(position):
            if (
                item is not self._preview_item
                and item.data(self._element_data_key)
            ):
                self.removeItem(item)
                return True
        return False

    def _snapped_position(self, position):
        snapped_x = (
            round(position.x() / self._grid_spacing_horizontal)
            * self._grid_spacing_horizontal
        )
        snapped_y = (
            round(position.y() / self._grid_spacing_vertical)
            * self._grid_spacing_vertical
        )
        return QPointF(snapped_x, snapped_y)

    def _element_rect(self, position):
        snapped_position = self._snapped_position(position)
        half_size = self._element_size / 2
        return QRectF(
            snapped_position.x() - half_size,
            snapped_position.y() - half_size,
            self._element_size,
            self._element_size,
        )

    def drawBackground(self, painter, rect):
        """Draw a subtle grid with independent horizontal and vertical spacing."""
        super().drawBackground(painter, rect)
        if not self._grid_is_visible_at_current_zoom():
            return

        theme = (
            self.theme_manager.get_active_theme()
            if self.theme_manager is not None
            else {}
        )
        pen = QPen(QColor(theme.get("canvasGrid", self._default_grid_color)))
        pen.setCosmetic(True)
        painter.save()
        painter.setPen(pen)

        left = int(rect.left() // self._grid_spacing_horizontal)
        right = int(rect.right() // self._grid_spacing_horizontal) + 1
        top = int(rect.top() // self._grid_spacing_vertical)
        bottom = int(rect.bottom() // self._grid_spacing_vertical) + 1
        lines = [
            QLineF(index * self._grid_spacing_horizontal, rect.top(),
                   index * self._grid_spacing_horizontal, rect.bottom())
            for index in range(left, right + 1)
        ]
        lines.extend(
            QLineF(rect.left(), index * self._grid_spacing_vertical,
                   rect.right(), index * self._grid_spacing_vertical)
            for index in range(top, bottom + 1)
        )
        painter.drawLines(lines)
        painter.restore()

    def _grid_is_visible_at_current_zoom(self):
        views = self.views()
        return not views or views[0].transform().m11() >= self._minimum_grid_zoom

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
