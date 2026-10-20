"""
Canvas module for PyRailMl.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView
from modules.canvas.scene import Scene

class Canvas(QGraphicsView):
    """Main canvas widget."""

    _zoom_factor = 1.15
    _minimum_zoom = 0.1
    _maximum_zoom = 20.0

    def __init__(self, parent=None):
        """Initialize canvas widget."""
        super().__init__(parent)
        self.parent = parent
        self.canvas_scene = Scene(self)
        self.setScene(self.canvas_scene)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self._panning = False
        self._last_pan_position = None
        self._zoom = 1.0
        self.fitInView(
            self.canvas_scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

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
