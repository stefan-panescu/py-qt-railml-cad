"""
Canvas module for PyRailMl.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView
from modules.canvas.canvasscene import CanvasScene

class CanvasView(QGraphicsView):
    """Main canvas widget."""

    _zoom_factor = 1.15
    _minimum_zoom = 0.01
    _maximum_zoom = 20.0

    def __init__(self, parent=None, theme_manager=None):
        """Initialize canvas widget."""
        super().__init__(parent)
        self.parent = parent
        self.canvas_scene = CanvasScene(self, theme_manager)
        self.setScene(self.canvas_scene)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._panning = False
        self._last_pan_position = None
        self._zoom = 1.0
        # self.fitInView(
        #     self.canvas_scene.itemsBoundingRect(),
        #     Qt.AspectRatioMode.KeepAspectRatio,
        # )
        self._expand_scene_rect_to_viewport()

    def resizeEvent(self, event):
        """Keep the scrollable area open as the viewport grows."""
        super().resizeEvent(event)
        if hasattr(self, "canvas_scene"):
            self._expand_scene_rect_to_viewport()

    def wheelEvent(self, event):
        """Zoom toward the mouse pointer using the mouse wheel."""
        if event.angleDelta().y() == 0:
            super().wheelEvent(event)
            return

        factor = (
            self._zoom_factor
            if event.angleDelta().y() > 0
            else 1 / self._zoom_factor
        )
        next_zoom = self._zoom * factor
        if self._minimum_zoom <= next_zoom <= self._maximum_zoom:
            self.scale(factor, factor)
            self._zoom = next_zoom
            self._expand_scene_rect_to_viewport()
        event.accept()

    def mousePressEvent(self, event):
        """Start panning while the middle mouse button is held."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_position = event.position().toPoint()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Move the view while panning."""
        if self._panning:
            position = event.position().toPoint()
            delta = position - self._last_pan_position
            self._last_pan_position = position
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self._expand_scene_rect_to_viewport()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Stop panning when the middle mouse button is released."""
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._last_pan_position = None
            self.viewport().unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def center_on_origin(self):
        """Restore the default fit-to-square zoom and center on the origin."""
        self.resetTransform()
        self._zoom = 1.0
        # self.fitInView(
        #     self.canvas_scene.itemsBoundingRect(),
        #     Qt.AspectRatioMode.KeepAspectRatio,
        # )
        self.centerOn(0, 0)
        self._expand_scene_rect_to_viewport()

    def _expand_scene_rect_to_viewport(self):
        """Grow the scrollable scene area as the view moves into empty space."""
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        margin_x = visible_rect.width()
        margin_y = visible_rect.height()
        expanded_rect = visible_rect.adjusted(
            -margin_x,
            -margin_y,
            margin_x,
            margin_y,
        )
        self.canvas_scene.setSceneRect(
            self.canvas_scene.sceneRect().united(expanded_rect)
        )
