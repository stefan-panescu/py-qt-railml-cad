"""Tests for canvas placement and move tools."""

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtTest import QTest

from modules.canvas.canvasview import CanvasView


def test_move_element_snaps_and_escape_restores(qapp):
    """Move a placed element to a snapped point and restore it on cancel."""
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

    view.begin_move_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(element.x, element.y)),
    )
    qapp.processEvents()
    assert view._move_has_selection
    assert not scene._element_items[element].isVisible()

    destination = QPointF(1200, 1600)
    QTest.mouseMove(view.viewport(), view.mapFromScene(destination))
    qapp.processEvents()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(destination),
    )
    qapp.processEvents()
    assert scene._element_items[element].isVisible()
    assert QPointF(element.x, element.y) == destination

    view.begin_move_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(element.x, element.y)),
    )
    qapp.processEvents()
    QTest.keyClick(view, Qt.Key.Key_Escape)
    qapp.processEvents()
    assert scene._element_items[element].isVisible()
    assert QPointF(element.x, element.y) == destination


def test_delete_element_removes_placed_element_only(qapp):
    """Delete a placed square without affecting the demo square."""
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

    view.begin_delete_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(element.x, element.y)),
    )
    qapp.processEvents()

    assert element not in scene.model.elements
    assert remaining_element in scene.model.elements
    assert not view._deleting_element

    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(QPointF(remaining_element.x, remaining_element.y)),
    )
    qapp.processEvents()
    assert remaining_element in scene.model.elements

    QTest.keyClick(view, Qt.Key.Key_Escape)
    qapp.processEvents()
    assert not view._deleting_element
