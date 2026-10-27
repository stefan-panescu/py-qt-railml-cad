"""
Canvas module for PyRailMl.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView
from modules.canvas.canvasmodel import CanvasModel
from modules.canvas.canvas_settings import CanvasSettings
from modules.canvas.canvasscene import CanvasScene


class CanvasView(QGraphicsView):
    """Main canvas widget."""

    def __init__(self, parent=None, theme_manager=None, config=None):
        """Initialize canvas widget."""
        super().__init__(parent)
        settings = CanvasSettings.from_config(config) if config else CanvasSettings()
        self.canvas_model = CanvasModel(settings)
        self.canvas_scene = CanvasScene(
            self.canvas_model,
            self,
            theme_manager,
        )
        self.setScene(self.canvas_scene)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.viewport().setMouseTracking(True)
        self._zoom = 1.0
        self._adding_element = False
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
            self.canvas_model.settings.zoom_factor
            if event.angleDelta().y() > 0
            else 1 / self.canvas_model.settings.zoom_factor
        )
        next_zoom = self._zoom * factor
        if (
            self.canvas_model.settings.minimum_zoom
            <= next_zoom
            <= self.canvas_model.settings.maximum_zoom
        ):
            self.scale(factor, factor)
            self._zoom = next_zoom
            self._expand_scene_rect_to_viewport()
        event.accept()

    def mouseMoveEvent(self, event):
        """Update the element-placement preview."""
        if self._adding_element and self.dragMode() != self.DragMode.ScrollHandDrag:
            position = self.mapToScene(event.position().toPoint())
            self.canvas_scene.move_preview(position.x(), position.y())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Place the preview square on a left click."""
        if event.button() == Qt.MouseButton.LeftButton and self._adding_element:
            if self.dragMode() == self.DragMode.ScrollHandDrag:
                super().mousePressEvent(event)
                return
            position = self.mapToScene(event.position().toPoint())
            element = self.canvas_model.add_element(position.x(), position.y())
            self.canvas_scene.finish_add_preview(element)
            self._adding_element = False
            self.viewport().unsetCursor()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Snap moved elements after Qt completes its native drag."""
        super().mouseReleaseEvent(event)
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.dragMode() != self.DragMode.ScrollHandDrag
        ):
            self.canvas_scene.snap_selected_elements()

    def keyPressEvent(self, event):
        """Use Space to pan, Delete to remove selection, and Escape to cancel."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            if self.dragMode() != self.DragMode.ScrollHandDrag:
                self._set_space_pan_mode(True)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_add_element()
            self.canvas_scene.clearSelection()
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.canvas_scene.delete_selected_elements()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Restore the previous canvas interaction when Space is released."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._set_space_pan_mode(False)
            event.accept()
            return
        super().keyReleaseEvent(event)

    def focusOutEvent(self, event):
        """Avoid leaving hand-drag mode active after focus moves elsewhere."""
        if self.dragMode() == self.DragMode.ScrollHandDrag:
            self._set_space_pan_mode(False)
        super().focusOutEvent(event)

    def _set_space_pan_mode(self, enabled):
        if enabled:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            if self._adding_element:
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.viewport().unsetCursor()

    def begin_add_element(self):
        """Start placing one square that follows the mouse cursor."""
        self._adding_element = True
        position = self.mapToScene(self.viewport().rect().center())
        self.canvas_scene.begin_add_preview(position.x(), position.y())
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()

    def cancel_add_element(self):
        """Cancel square placement and remove its preview."""
        self._adding_element = False
        self.canvas_scene.cancel_preview()
        self.viewport().unsetCursor()

    def copy_elements(self):
        """Copy the selected elements for a later paste."""
        self.canvas_scene.copy_selected_elements()

    def paste_elements(self):
        """Paste copied elements into the canvas."""
        return self.canvas_scene.paste_elements()

    def center_on_origin(self):
        """Restore the default fit-to-square zoom and center on the origin."""
        self.resetTransform()
        self._zoom = 1.0
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
