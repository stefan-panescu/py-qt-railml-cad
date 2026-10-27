"""
Tests for MainWindow class
"""
from PyQt6.QtWidgets import QMainWindow
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
