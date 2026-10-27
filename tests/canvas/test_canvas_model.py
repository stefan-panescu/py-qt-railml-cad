"""Tests for canvas element logic and configurable numeric settings."""

import pytest

from modules.canvas.canvasmodel import CanvasModel
from modules.canvas.canvas_settings import CanvasSettings
from modules.config.config import Config


def test_model_snaps_and_manages_elements():
    model = CanvasModel()
    element = model.add_element(301, 601)

    assert (element.x, element.y) == (400, 800)
    assert (element.width, element.height) == (800, 800)
    assert element.connection_points == (
        (400, 400),
        (800, 800),
        (400, 1200),
        (0, 800),
    )
    assert model.element_at(100, 500) is element

    model.move_element(element, -201, -401)
    assert (element.x, element.y) == (-200, -400)
    assert element.connection_points[0] == (-200, -800)
    assert model.delete_element(element)
    assert model.element_at(-200, -400) is None


def test_settings_are_loaded_from_user_config(tmp_path):
    config = Config(str(tmp_path / "config.ini"))
    config.set("Canvas", "grid_spacing_horizontal", "250")
    config.set("Canvas", "grid_spacing_vertical", "500")
    config.set("Canvas", "element_size", "600")

    settings = CanvasSettings.from_config(config)
    model = CanvasModel(settings)
    element = model.add_element(251, 501)

    assert settings.grid_spacing_horizontal == 250
    assert settings.grid_spacing_vertical == 500
    assert (element.x, element.y) == (250, 500)
    assert (element.width, element.height) == (600, 600)


def test_invalid_canvas_settings_are_rejected(tmp_path):
    config = Config(str(tmp_path / "config.ini"))
    config.set("Canvas", "grid_spacing_horizontal", "0")

    with pytest.raises(ValueError, match="Canvas numeric settings"):
        CanvasSettings.from_config(config)
