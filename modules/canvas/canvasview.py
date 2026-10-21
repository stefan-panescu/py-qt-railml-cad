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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.viewport().setMouseTracking(True)
        self._panning = False
        self._last_pan_position = None
        self._zoom = 1.0
        self._adding_element = False
        self._moving_element = False
        self._move_has_selection = False
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
        if self._adding_element or (
            self._moving_element and self._move_has_selection
        ):
            self.canvas_scene.move_element_preview(
                self.mapToScene(event.position().toPoint())
            )
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Place the preview square on a left click."""
        if event.button() == Qt.MouseButton.LeftButton and self._adding_element:
            self.canvas_scene.move_element_preview(
                self.mapToScene(event.position().toPoint())
            )
            self.canvas_scene.place_element_preview()
            self._adding_element = False
            self.viewport().unsetCursor()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._moving_element:
            position = self.mapToScene(event.position().toPoint())
            if not self._move_has_selection:
                if self.canvas_scene.begin_move_element(position):
                    self._move_has_selection = True
            else:
                self.canvas_scene.move_element_preview(position)
                self.canvas_scene.place_element_preview()
                self._moving_element = False
                self._move_has_selection = False
                self.viewport().unsetCursor()
            event.accept()
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_position = event.position().toPoint()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Stop panning when the middle mouse button is released."""
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._last_pan_position = None
            if self._adding_element or self._moving_element:
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.viewport().unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def begin_add_element(self):
        """Start placing one square that follows the mouse cursor."""
        self._moving_element = False
        self._move_has_selection = False
        self._adding_element = True
        self.canvas_scene.begin_add_element(
            self.mapToScene(self.viewport().rect().center())
        )
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

    def begin_move_element(self):
        """Start the two-click move flow for a placed element."""
        self._adding_element = False
        self.canvas_scene.cancel_add_element()
        self.canvas_scene.cancel_move_element()
        self._moving_element = True
        self._move_has_selection = False
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

    def cancel_add_element(self):
        """Cancel square placement and remove its preview."""
        if not self._adding_element and not self._moving_element:
            return
        self._adding_element = False
        self._moving_element = False
        self._move_has_selection = False
        self.canvas_scene.cancel_add_element()
        self.canvas_scene.cancel_move_element()
        self.viewport().unsetCursor()

    def keyPressEvent(self, event):
        """Cancel square placement with Escape."""
        if (
            (self._adding_element or self._moving_element)
            and event.key() == Qt.Key.Key_Escape
        ):
            self.cancel_add_element()
            event.accept()
            return
        super().keyPressEvent(event)

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
