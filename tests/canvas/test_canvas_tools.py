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

    element = next(
        item for item in scene.items()
        if item.data(scene._element_data_key)
    )
    original_rect = element.rect()

    view.begin_move_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(original_rect.center()),
    )
    qapp.processEvents()
    assert view._move_has_selection
    assert not element.isVisible()

    destination = QPointF(1200, 1600)
    QTest.mouseMove(view.viewport(), view.mapFromScene(destination))
    qapp.processEvents()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(destination),
    )
    qapp.processEvents()
    assert element.isVisible()
    assert element.rect().center() == destination

    view.begin_move_element()
    QTest.mouseClick(
        view.viewport(),
        Qt.MouseButton.LeftButton,
        pos=view.mapFromScene(element.rect().center()),
    )
    qapp.processEvents()
    QTest.keyClick(view, Qt.Key.Key_Escape)
    qapp.processEvents()
    assert element.isVisible()
    assert element.rect().center() == destination
