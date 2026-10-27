"""Tests for canvas placement and move tools."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtTest import QTest

from modules.canvas.canvasview import CanvasView


def test_drag_element_snaps_to_grid(qapp):
    """Drag a selected element and snap it to the grid when released."""
    view = CanvasView()
    view.resize(800, 600)
    view.show()
    qapp.processEvents()

    scene = view.canvas_scene
    view.begin_add_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(0, 0)),
    )
    qapp.processEvents()
    element = scene.model.elements[0]
    item = scene.element_item(element)
    assert item.element is element
    assert item.boundingRect().left() < -412
    assert item.boundingRect().right() > 412
    assert element.connection_points == (
        (0, -400),
        (400, 0),
        (0, 400),
        (-400, 0),
    )

    start = view.mapFromScene(QPointF(element.x, element.y))
    destination = view.mapFromScene(QPointF(1200, 1600))
    QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(view.viewport(), destination)
    QTest.mouseRelease(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=destination,
    )
    qapp.processEvents()

    assert item.isSelected()
    assert QPointF(element.x, element.y) == QPointF(1200, 1600)
    assert element.connection_points == (
        (1200, 1200),
        (1600, 1600),
        (1200, 2000),
        (800, 1600),
    )


def test_delete_removes_selected_element_only(qapp):
    """Delete only the selected element using the keyboard."""
    view = CanvasView()
    view.resize(800, 600)
    view.show()
    qapp.processEvents()

    scene = view.canvas_scene
    view.begin_add_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(0, 0)),
    )
    qapp.processEvents()
    view.begin_add_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(1200, 0)),
    )
    qapp.processEvents()
    element, remaining_element = scene.model.elements

    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(element.x, element.y)),
    )
    QTest.keyClick(view, Qt.Key.Key_Delete)
    qapp.processEvents()

    assert element not in scene.model.elements
    assert remaining_element in scene.model.elements
    assert scene.element_item(element) is None
    assert scene.element_item(remaining_element) is not None

    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(remaining_element.x, remaining_element.y)),
    )
    qapp.processEvents()
    QTest.keyClick(view, Qt.Key.Key_Backspace)
    qapp.processEvents()
    assert remaining_element not in scene.model.elements


def test_element_selection_and_escape_deselect(qapp):
    """Select a canvas element natively and clear selection with Escape."""
    view = CanvasView()
    view.resize(800, 600)
    view.show()
    qapp.processEvents()

    view.begin_add_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(0, 0)),
    )
    qapp.processEvents()

    element = view.canvas_model.elements[0]
    item = view.canvas_scene.element_item(element)
    assert view.dragMode() == view.DragMode.RubberBandDrag

    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(element.x, element.y)),
    )
    qapp.processEvents()
    assert item.isSelected()
    assert item.pen().color() == QColor("#3498db")
    assert item.pen().isCosmetic()

    QTest.keyClick(view, Qt.Key.Key_Escape)
    qapp.processEvents()
    assert not item.isSelected()
    assert item.pen().color() == QColor("#000000")
    assert not item.pen().isCosmetic()


def test_space_temporarily_enables_hand_drag(qapp):
    """Space pans the canvas without permanently changing selection behavior."""
    view = CanvasView()
    view.resize(800, 600)
    view.show()
    view.setFocus()
    qapp.processEvents()

    QTest.keyPress(view, Qt.Key.Key_Space)
    assert view.dragMode() == view.DragMode.ScrollHandDrag

    center = view.viewport().rect().center()
    scene_center_before = view.mapToScene(center)
    QTest.mousePress(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=center,
    )
    QTest.mouseMove(
        view.viewport(),
        center + QPointF(30, 20).toPoint(),
    )
    QTest.mouseRelease(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=center + QPointF(30, 20).toPoint(),
    )
    QTest.keyRelease(view, Qt.Key.Key_Space)
    qapp.processEvents()

    assert view.dragMode() == view.DragMode.RubberBandDrag
    assert view.mapToScene(center) != scene_center_before
