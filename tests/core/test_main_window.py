"""
Tests for MainWindow class
"""
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction
from modules.core.main_window import MainWindow
from modules.config.config import Config

def test_main_window_creation(qapp):
    """Test that MainWindow can be created"""
    config = Config()
    config.set('Application', 'Name', 'PyQt6ify Pro')
    config.set('Application', 'Version', '1.0.0')
    window = MainWindow(config)
    assert isinstance(window, QMainWindow)
    assert window.windowTitle() == "PyQt6ify Pro 1.0.0"


def test_add_element_action_keeps_dashboard_alive(qapp, tmp_path, monkeypatch):
    """Test that Add Element switches to the canvas without deleting the dashboard."""
    import modules.core.main_window as main_window_module

    monkeypatch.setattr(main_window_module, 'Database', lambda _parent: object())
    config = Config(str(tmp_path / 'config.ini'))
    window = MainWindow(config)

    add_action = next(
        action for action in window.tool_bar.actions()
        if action.text() == 'Add Element'
    )
    add_action.trigger()
    qapp.processEvents()

    assert window.central_stack.currentWidget() is window.canvas
    assert window.dashboard is not None
    assert window.canvas._adding_element
    assert window.canvas.canvas_scene._preview_item is not None
    window.close()


def test_copy_paste_menu_actions_duplicate_selected_canvas_element(
    qapp,
    tmp_path,
    monkeypatch,
):
    """Edit menu copy and paste actions duplicate selected canvas elements."""
    import modules.core.main_window as main_window_module
    from modules.canvas.canvas_element_item import CanvasElementItem

    monkeypatch.setattr(main_window_module, 'Database', lambda _parent: object())
    config = Config(str(tmp_path / 'config.ini'))
    window = MainWindow(config)
    window.new_file()

    element = window.canvas.canvas_model.add_element(0, 0)
    item = CanvasElementItem(
        element,
        window.canvas.canvas_model.settings,
        window.theme_manager,
    )
    window.canvas.canvas_scene.addItem(item)
    item.setSelected(True)

    actions = window.menu_bar.findChildren(QAction)
    copy_action = next(action for action in actions if action.text() == '&Copy')
    paste_action = next(action for action in actions if action.text() == '&Paste')
    copy_action.trigger()
    paste_action.trigger()

    assert len(window.canvas.canvas_model.elements) == 2
    duplicate = window.canvas.canvas_model.elements[1]
    assert (duplicate.x, duplicate.y) == (200, 400)
    assert window.central_stack.currentWidget() is window.canvas
    window.close()
